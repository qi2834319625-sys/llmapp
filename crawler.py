"""
Data collection and crawling engine for academic papers.
Supports: IACR ePrint, arXiv, DOI, Google Scholar, Semantic Scholar.
"""
import sqlite3, json, os, time, hashlib, re
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "portal.db")
PAPER_DIR = Path(__file__).parent / "static" / "papers"
PAPER_DIR.mkdir(parents=True, exist_ok=True)

# ========== Database Operations ==========

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_crawler_tables():
    """Initialize crawler-specific tables"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS crawl_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_zh TEXT,
            base_url TEXT,
            source_type TEXT DEFAULT 'rss',
            api_endpoint TEXT,
            api_key TEXT,
            crawl_interval INTEGER DEFAULT 3600,
            last_crawl TIMESTAMP,
            last_status TEXT DEFAULT 'idle',
            last_error TEXT,
            papers_found INTEGER DEFAULT 0,
            papers_new INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            config TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS crawl_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            action TEXT NOT NULL,
            status TEXT DEFAULT 'success',
            papers_found INTEGER DEFAULT 0,
            papers_new INTEGER DEFAULT 0,
            papers_downloaded INTEGER DEFAULT 0,
            error_message TEXT,
            duration_seconds REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(source_id) REFERENCES crawl_sources(id)
        );
        
        CREATE TABLE IF NOT EXISTS crawl_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            schedule_type TEXT DEFAULT 'interval',
            interval_seconds INTEGER DEFAULT 3600,
            cron_expression TEXT,
            next_run TIMESTAMP,
            last_run TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY(source_id) REFERENCES crawl_sources(id)
        );
        
        CREATE TABLE IF NOT EXISTS paper_fetch_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_id TEXT,
            title TEXT,
            authors TEXT,
            year INTEGER,
            abstract TEXT,
            pdf_url TEXT,
            doi TEXT,
            venue TEXT,
            keywords TEXT,
            status TEXT DEFAULT 'queued',
            priority INTEGER DEFAULT 5,
            retry_count INTEGER DEFAULT 0,
            error_message TEXT,
            paper_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_fetch_queue_status ON paper_fetch_queue(status, priority DESC);
        CREATE INDEX IF NOT EXISTS idx_fetch_queue_source ON paper_fetch_queue(source, source_id);
        CREATE INDEX IF NOT EXISTS idx_crawl_logs_source ON crawl_logs(source_id, created_at);
    """)
    
    # Seed default sources
    sources = [
        ('iacr_eprint', 'IACR ePrint Archive', 'https://eprint.iacr.org/', 'rss',
         'https://eprint.iacr.org/rss/', None, 3600),
        ('arxiv_cs', 'arXiv cs.CR', 'https://arxiv.org/', 'api',
         'https://export.arxiv.org/api/query', None, 7200),
        ('arxiv_crypto', 'arXiv Cryptography', 'https://arxiv.org/', 'api',
         'https://export.arxiv.org/api/query', None, 7200),
        ('semantic_scholar', 'Semantic Scholar', 'https://api.semanticscholar.org/', 'api',
         'https://api.semanticscholar.org/graph/v1/paper/search', None, 3600),
        ('crossref', 'CrossRef DOI', 'https://api.crossref.org/', 'api',
         'https://api.crossref.org/works', None, 1800),
    ]
    for s in sources:
        conn.execute("""INSERT OR IGNORE INTO crawl_sources 
            (name, name_zh, base_url, source_type, api_endpoint, api_key, crawl_interval)
            VALUES (?,?,?,?,?,?,?)""", s)
    
    conn.commit()
    conn.close()

# ========== Crawler Engines ==========

class PaperCrawler:
    """Base class for paper crawlers"""
    
    def __init__(self, source_name):
        self.source_name = source_name
        self.conn = get_db()
        source = self.conn.execute("SELECT * FROM crawl_sources WHERE name=?", (source_name,)).fetchone()
        self.source = dict(source) if source else None
    
    def crawl(self, query=None, max_results=50):
        """Crawl papers from source. Override in subclasses."""
        raise NotImplementedError
    
    def log_crawl(self, status, found=0, new=0, downloaded=0, error=None, duration=0):
        source_id = self.source['id'] if self.source else None
        self.conn.execute("""INSERT INTO crawl_logs 
            (source_id, action, status, papers_found, papers_new, papers_downloaded, error_message, duration_seconds)
            VALUES (?,?,?,?,?,?,?,?)""",
            (source_id, 'crawl', status, found, new, downloaded, error, duration))
        self.conn.execute("UPDATE crawl_sources SET last_crawl=CURRENT_TIMESTAMP, last_status=? WHERE id=?",
                         (status, source_id))
        self.conn.commit()
    
    def add_to_queue(self, papers):
        """Add crawled papers to fetch queue"""
        added = 0
        for p in papers:
            try:
                # Check if already exists
                existing = self.conn.execute(
                    "SELECT id FROM papers WHERE source=? AND source_id=?",
                    (self.source_name, p.get('source_id', ''))
                ).fetchone()
                if existing:
                    continue
                
                # Check queue
                existing_q = self.conn.execute(
                    "SELECT id FROM paper_fetch_queue WHERE source=? AND source_id=?",
                    (self.source_name, p.get('source_id', ''))
                ).fetchone()
                if existing_q:
                    continue
                
                self.conn.execute("""INSERT INTO paper_fetch_queue 
                    (source, source_id, title, authors, year, abstract, pdf_url, doi, venue, keywords, priority)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (self.source_name, p.get('source_id', ''), p.get('title', ''), p.get('authors', ''),
                     p.get('year'), p.get('abstract', ''), p.get('pdf_url', ''), p.get('doi', ''),
                     p.get('venue', ''), p.get('keywords', ''), p.get('priority', 5)))
                added += 1
            except Exception as e:
                pass
        self.conn.commit()
        return added
    
    def close(self):
        self.conn.close()


class IACRCrawler(PaperCrawler):
    """Crawler for IACR ePrint Archive"""
    
    def __init__(self):
        super().__init__('iacr_eprint')
        self.base_url = "https://eprint.iacr.org"
        self.rss_url = "https://eprint.iacr.org/rss/"
    
    def crawl(self, query=None, max_results=50):
        """Crawl IACR ePrint RSS feed"""
        import urllib.request
        import xml.etree.ElementTree as ET
        
        papers = []
        try:
            req = urllib.request.Request(self.rss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode('utf-8')
            
            root = ET.fromstring(data)
            items = root.findall('.//item')[:max_results]
            
            for item in items:
                title = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                description = item.findtext('description', '').strip()
                pub_date = item.findtext('pubDate', '').strip()
                
                # Extract year from date
                year = None
                if pub_date:
                    try:
                        year = int(pub_date.split()[-1])
                    except:
                        year = datetime.now().year
                
                # Extract paper ID from link
                source_id = link.split('/')[-1] if link else ''
                
                # Clean abstract
                abstract = re.sub(r'<[^>]+>', '', description)[:2000] if description else ''
                
                papers.append({
                    'source_id': source_id,
                    'title': title,
                    'authors': '',
                    'year': year or datetime.now().year,
                    'abstract': abstract,
                    'pdf_url': f"{self.base_url}/{source_id}.pdf" if source_id else '',
                    'venue': 'IACR ePrint',
                    'keywords': '',
                    'priority': 8  # High priority for crypto papers
                })
            
            self.log_crawl('success', found=len(papers))
        except Exception as e:
            self.log_crawl('error', error=str(e))
        
        return papers
    
    def crawl_recent(self, days=7):
        """Crawl recent papers from IACR"""
        papers = self.crawl(max_results=100)
        # Filter by date
        cutoff = datetime.now() - timedelta(days=days)
        return [p for p in papers if p.get('year', 0) >= cutoff.year]


class ArxivCrawler(PaperCrawler):
    """Crawler for arXiv API"""
    
    def __init__(self, category='cs.CR'):
        super().__init__('arxiv_cs' if category == 'cs.CR' else 'arxiv_crypto')
        self.category = category
        self.api_url = "https://export.arxiv.org/api/query"
    
    def crawl(self, query=None, max_results=50):
        """Crawl arXiv API"""
        import urllib.request
        import urllib.parse
        import xml.etree.ElementTree as ET
        
        papers = []
        search_query = query or f"cat:{self.category}"
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        url = f"{self.api_url}?search_query={urllib.parse.quote(search_query)}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read().decode('utf-8')
            
            root = ET.fromstring(data)
            # arXiv uses ns0 prefix, register it
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
            
            for entry in root.findall('atom:entry', ns)[:max_results]:
                # Try both namespaced and raw tag names
                title_elem = entry.find('atom:title', ns) or entry.find('.//{http://www.w3.org/2005/Atom}title')
                title = (title_elem.text or '').strip().replace('\n', ' ') if title_elem is not None else ''
                
                summary_elem = entry.find('atom:summary', ns) or entry.find('.//{http://www.w3.org/2005/Atom}summary')
                summary = (summary_elem.text or '').strip().replace('\n', ' ')[:2000] if summary_elem is not None else ''
                
                published = entry.findtext('atom:published', '', ns)
                arxiv_id = entry.findtext('atom:id', '', ns).split('/')[-1]
                
                # Extract year
                year = None
                if published:
                    try:
                        year = int(published[:4])
                    except:
                        year = datetime.now().year
                
                # Get authors
                authors = ', '.join([
                    (a.findtext('atom:name', '', ns) or '') 
                    for a in entry.findall('atom:author', ns)
                ])
                
                # Get PDF link
                pdf_url = ''
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf' or link.get('type') == 'application/pdf':
                        pdf_url = link.get('href', '')
                        break
                
                # Get categories/keywords
                keywords = ', '.join([c.get('term', '') for c in entry.findall('atom:category', ns)])
                
                papers.append({
                    'source_id': arxiv_id,
                    'title': title,
                    'authors': authors,
                    'year': year or datetime.now().year,
                    'abstract': summary,
                    'pdf_url': pdf_url,
                    'venue': f"arXiv:{self.category}",
                    'keywords': keywords,
                    'priority': 7
                })
            
            self.log_crawl('success', found=len(papers))
        except Exception as e:
            self.log_crawl('error', error=str(e))
        
        return papers


class SemanticScholarCrawler(PaperCrawler):
    """Crawler for Semantic Scholar API"""
    
    def __init__(self):
        super().__init__('semantic_scholar')
        self.api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    def crawl(self, query=None, max_results=50):
        """Crawl Semantic Scholar API"""
        import urllib.request
        import urllib.parse
        
        papers = []
        search_query = query or "key agreement cryptography"
        
        url = f"{self.api_url}?query={urllib.parse.quote(search_query)}&fields=title,authors,year,abstract,externalIds,venue,publicationDate&limit={max_results}"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
            
            for p in data.get('data', []):
                papers.append({
                    'source_id': p.get('paperId', ''),
                    'title': p.get('title', ''),
                    'authors': ', '.join([a.get('name', '') for a in p.get('authors', [])]),
                    'year': p.get('year', datetime.now().year),
                    'abstract': (p.get('abstract', '') or '')[:2000],
                    'pdf_url': '',
                    'doi': p.get('externalIds', {}).get('DOI', ''),
                    'venue': p.get('venue', ''),
                    'keywords': '',
                    'priority': 6
                })
            
            self.log_crawl('success', found=len(papers))
        except Exception as e:
            self.log_crawl('error', error=str(e))
        
        return papers


# ========== Auto-Classification ==========

KEYWORD_CATEGORIES = {
    'DH-based': ['diffie-hellman', 'diffie hellman', 'dh key', 'dhke', 'classical key agreement'],
    'ECDH-based': ['elliptic curve', 'ecdh', 'ecies', 'ecc', 'curve25519', 'x25519', 'ec key'],
    'Lattice-based': ['lattice', 'lwe', 'rlwe', 'kyber', 'saber', 'ntru', 'post-quantum key', 'pqc'],
    'Code-based': ['code-based', 'mceliece', 'qc-mdpc', 'ldpc key'],
    'MQ-based': ['multivariate', 'mq problem', 'rainbow', 'oil and vinegar'],
    'Isogeny-based': ['isogeny', 'sidh', 'sike', 'csidh', 'supersingular'],
    'Lightweight': ['lightweight', 'iot key', 'constrained', 'sensor network', 'rfid key'],
    'Group Key': ['group key', 'group agreement', 'multi-party key', 'broadcast encryption'],
    'IBE-based': ['identity-based', 'ibe key', 'attribute-based key', 'abe key'],
    'Physical Layer': ['physical layer', 'channel key', 'rf fingerprint', 'wireless key'],
    'Blockchain': ['blockchain key', 'smart contract key', 'distributed key'],
    'TLS/SSL': ['tls key', 'ssl key', 'handshake', 'key exchange protocol'],
    'PAKE': ['pake', 'password authenticated', 'password-based key', 'opake'],
}

def classify_paper(title, abstract='', keywords=''):
    """Auto-classify paper based on keywords"""
    text = f"{title} {abstract} {keywords}".lower()
    
    scores = {}
    for cat, kws in KEYWORD_CATEGORIES.items():
        score = sum(1 for kw in kws if kw in text)
        if score > 0:
            scores[cat] = score
    
    if not scores:
        return None
    
    return max(scores, key=scores.get)


# ========== Download Manager ==========

def process_download_queue(max_downloads=5):
    """Process pending downloads in queue"""
    conn = get_db()
    
    # Get pending items
    items = conn.execute(
        "SELECT * FROM paper_fetch_queue WHERE status='queued' ORDER BY priority DESC, created_at LIMIT ?",
        (max_downloads,)
    ).fetchall()
    
    downloaded = 0
    for item in items:
        try:
            if not item['pdf_url']:
                conn.execute("UPDATE paper_fetch_queue SET status='no_pdf' WHERE id=?", (item['id'],))
                continue
            
            # Download PDF
            import urllib.request
            filename = f"auto_{item['source']}_{item['source_id'] or hashlib.md5(item['title'].encode()).hexdigest()[:8]}.pdf"
            filepath = PAPER_DIR / filename
            
            req = urllib.request.Request(item['pdf_url'], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                with open(filepath, "wb") as f:
                    f.write(data)
            
            # Auto-classify
            category_name = classify_paper(item['title'], item['abstract'], item['keywords'])
            category_id = None
            if category_name:
                cat = conn.execute("SELECT id FROM paper_categories WHERE name=?", (category_name,)).fetchone()
                if cat:
                    category_id = cat['id']
            
            # Insert into papers
            conn.execute("""INSERT INTO papers 
                (title, authors, year, venue, category_id, abstract, pdf_url, pdf_path, pdf_size, source, source_id, status, downloaded)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                (item['title'], item['authors'], item['year'], item['venue'], category_id,
                 item['abstract'], item['pdf_url'], str(filepath), len(data),
                 item['source'], item['source_id'], 'downloaded'))
            
            paper_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            
            # Update queue
            conn.execute("UPDATE paper_fetch_queue SET status='completed', paper_id=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                        (paper_id, item['id']))
            
            downloaded += 1
            
        except Exception as e:
            conn.execute("UPDATE paper_fetch_queue SET status='failed', error_message=?, retry_count=retry_count+1 WHERE id=?",
                        (str(e)[:200], item['id']))
    
    conn.commit()
    conn.close()
    return downloaded


# ========== Scheduled Crawl ==========

def run_scheduled_crawl():
    """Run all scheduled crawls"""
    conn = get_db()
    sources = conn.execute("SELECT * FROM crawl_sources WHERE is_active=1").fetchall()
    
    results = []
    for source in sources:
        try:
            crawler = None
            if source['name'] == 'iacr_eprint':
                crawler = IACRCrawler()
            elif source['name'] == 'arxiv_cs':
                crawler = ArxivCrawler('cs.CR')
            elif source['name'] == 'arxiv_crypto':
                crawler = ArxivCrawler('cs.CR')
                crawler.source_name = 'arxiv_crypto'
            elif source['name'] == 'semantic_scholar':
                crawler = SemanticScholarCrawler()
            
            if crawler:
                papers = crawler.crawl(max_results=50)
                added = crawler.add_to_queue(papers)
                crawler.close()
                
                # Update source stats
                conn.execute("UPDATE crawl_sources SET papers_found=papers_found+?, papers_new=papers_new+? WHERE id=?",
                            (len(papers), added, source['id']))
                
                results.append({
                    'source': source['name'],
                    'found': len(papers),
                    'new': added
                })
        except Exception as e:
            results.append({'source': source['name'], 'error': str(e)})
    
    # Process downloads
    downloaded = process_download_queue(max_downloads=3)
    
    conn.commit()
    conn.close()
    
    return {'crawls': results, 'downloaded': downloaded}
