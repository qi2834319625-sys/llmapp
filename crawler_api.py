"""
Data crawler API routes.
"""
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

PAPER_DIR = Path(__file__).parent / "static" / "papers"

def register_crawler_routes(app):
    
    import app as _app
    
    def require_auth(request):
        return _app.require_auth(request)
    
    def get_db():
        return _app.get_db()
    
    def render(tpl, **ctx):
        return _app.render(tpl, **ctx)
    
    # ========== Crawler Dashboard ==========
    @app.get("/crawler", response_class=HTMLResponse)
    async def crawler_page(request: Request):
        user = require_auth(request)
        return render("crawler.html", request=request, user=user)
    
    # ========== Sources ==========
    @app.get("/api/crawler/sources")
    async def api_crawler_sources(request: Request):
        require_auth(request)
        conn = get_db()
        rows = conn.execute("SELECT * FROM crawl_sources ORDER BY name").fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])
    
    @app.post("/api/crawler/sources")
    async def api_crawler_add_source(request: Request):
        require_auth(request)
        body = await request.json()
        conn = get_db()
        conn.execute("""INSERT INTO crawl_sources (name, name_zh, base_url, source_type, api_endpoint, api_key, crawl_interval)
                       VALUES (?,?,?,?,?,?,?)""",
            (body['name'], body.get('name_zh',''), body.get('base_url',''), body.get('source_type','rss'),
             body.get('api_endpoint',''), body.get('api_key'), body.get('interval', 3600)))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True})
    
    @app.put("/api/crawler/sources/{source_id}")
    async def api_crawler_update_source(request: Request, source_id: int):
        require_auth(request)
        body = await request.json()
        conn = get_db()
        conn.execute("UPDATE crawl_sources SET is_active=? WHERE id=?", (body.get('is_active', 1), source_id))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True})
    
    # ========== Crawl Control ==========
    @app.post("/api/crawler/crawl")
    async def api_crawler_run(request: Request):
        """Trigger manual crawl"""
        require_auth(request)
        body = await request.json()
        source_name = body.get('source')
        
        from crawler import IACRCrawler, ArxivCrawler, SemanticScholarCrawler, process_download_queue
        
        results = []
        try:
            if source_name == 'iacr_eprint' or not source_name:
                crawler = IACRCrawler()
                papers = crawler.crawl(max_results=50)
                added = crawler.add_to_queue(papers)
                crawler.close()
                results.append({'source': 'iacr_eprint', 'found': len(papers), 'new': added})
            
            if source_name == 'arxiv' or not source_name:
                crawler = ArxivCrawler('cs.CR')
                papers = crawler.crawl(max_results=50)
                added = crawler.add_to_queue(papers)
                crawler.close()
                results.append({'source': 'arxiv_cs', 'found': len(papers), 'new': added})
            
            if source_name == 'semantic_scholar' or not source_name:
                crawler = SemanticScholarCrawler()
                papers = crawler.crawl(max_results=30)
                added = crawler.add_to_queue(papers)
                crawler.close()
                results.append({'source': 'semantic_scholar', 'found': len(papers), 'new': added})
            
            # Process some downloads
            downloaded = process_download_queue(max_downloads=3)
            
            return JSONResponse({"success": True, "results": results, "downloaded": downloaded})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)
    
    @app.post("/api/crawler/download")
    async def api_crawler_download(request: Request):
        """Process download queue"""
        require_auth(request)
        body = await request.json()
        max_dl = body.get('max', 5)
        
        from crawler import process_download_queue
        downloaded = process_download_queue(max_downloads=max_dl)
        return JSONResponse({"success": True, "downloaded": downloaded})
    
    # ========== Queue ==========
    @app.get("/api/crawler/queue")
    async def api_crawler_queue(request: Request, status: str = None, limit: int = 50):
        require_auth(request)
        conn = get_db()
        if status:
            rows = conn.execute("SELECT * FROM paper_fetch_queue WHERE status=? ORDER BY priority DESC, created_at LIMIT ?", (status, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM paper_fetch_queue ORDER BY priority DESC, created_at LIMIT ?", (limit,)).fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])
    
    @app.delete("/api/crawler/queue/{queue_id}")
    async def api_crawler_queue_delete(request: Request, queue_id: int):
        require_auth(request)
        conn = get_db()
        conn.execute("DELETE FROM paper_fetch_queue WHERE id=?", (queue_id,))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True})
    
    # ========== Logs ==========
    @app.get("/api/crawler/logs")
    async def api_crawler_logs(request: Request, limit: int = 20):
        require_auth(request)
        conn = get_db()
        rows = conn.execute("""
            SELECT l.*, s.name as source_name FROM crawl_logs l 
            LEFT JOIN crawl_sources s ON l.source_id=s.id 
            ORDER BY l.created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])
    
    # ========== Stats ==========
    @app.get("/api/crawler/stats")
    async def api_crawler_stats(request: Request):
        require_auth(request)
        conn = get_db()
        stats = {
            "sources": conn.execute("SELECT COUNT(*) FROM crawl_sources WHERE is_active=1").fetchone()[0],
            "queue_pending": conn.execute("SELECT COUNT(*) FROM paper_fetch_queue WHERE status='queued'").fetchone()[0],
            "queue_completed": conn.execute("SELECT COUNT(*) FROM paper_fetch_queue WHERE status='completed'").fetchone()[0],
            "queue_failed": conn.execute("SELECT COUNT(*) FROM paper_fetch_queue WHERE status='failed'").fetchone()[0],
            "total_papers": conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
            "downloaded_papers": conn.execute("SELECT COUNT(*) FROM papers WHERE downloaded=1").fetchone()[0],
            "total_size_mb": conn.execute("SELECT COALESCE(SUM(pdf_size),0)/1048576.0 FROM papers WHERE downloaded=1").fetchone()[0],
            "recent_crawls": [dict(r) for r in conn.execute("SELECT l.*, s.name FROM crawl_logs l LEFT JOIN crawl_sources s ON l.source_id=s.id ORDER BY l.created_at DESC LIMIT 5").fetchall()],
        }
        conn.close()
        return JSONResponse(stats)
    
    # ========== Auto-Classify ==========
    @app.post("/api/crawler/classify")
    async def api_crawler_classify(request: Request):
        """Auto-classify uncategorized papers"""
        require_auth(request)
        from crawler import classify_paper, KEYWORD_CATEGORIES
        
        conn = get_db()
        uncategorized = conn.execute("SELECT * FROM papers WHERE category_id IS NULL OR category_id=0").fetchall()
        
        classified = 0
        for paper in uncategorized:
            cat_name = classify_paper(paper['title'], paper['abstract'] or '', paper['keywords'] or '')
            if cat_name:
                cat = conn.execute("SELECT id FROM paper_categories WHERE name=?", (cat_name,)).fetchone()
                if cat:
                    conn.execute("UPDATE papers SET category_id=? WHERE id=?", (cat['id'], paper['id']))
                    classified += 1
        
        conn.commit()
        conn.close()
        return JSONResponse({"success": True, "classified": classified})
