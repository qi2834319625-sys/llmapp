"""
Local database for user data storage.
Password same as account password (SHA-256 hashed).
"""
import sqlite3, hashlib, json, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "portal.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_user_data_tables():
    """Create tables for user-generated content"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, module TEXT NOT NULL,
            title TEXT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS user_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, module TEXT NOT NULL,
            item_id INTEGER NOT NULL, item_type TEXT, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL,
            theme TEXT DEFAULT 'dark', language TEXT DEFAULT 'zh', notifications_enabled INTEGER DEFAULT 1,
            data_encryption INTEGER DEFAULT 0, settings_json TEXT DEFAULT '{}',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, action TEXT NOT NULL,
            module TEXT, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, filename TEXT NOT NULL,
            original_name TEXT, file_type TEXT, file_size INTEGER, module TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS strategy_strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, name TEXT NOT NULL,
            description TEXT, code TEXT NOT NULL, symbols TEXT DEFAULT '[]', params TEXT DEFAULT '{}',
            is_public INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS strategy_backtests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, strategy_id INTEGER,
            name TEXT, symbols TEXT, weights TEXT, start_date TEXT, end_date TEXT,
            initial_capital REAL, final_value REAL, total_return REAL, sharpe_ratio REAL,
            max_drawdown REAL, volatility REAL, num_trades INTEGER, result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(strategy_id) REFERENCES strategy_strategies(id)
        );
        CREATE INDEX IF NOT EXISTS idx_user_notes ON user_notes(user_id, module);
        CREATE INDEX IF NOT EXISTS idx_user_bookmarks ON user_bookmarks(user_id, module);
        CREATE INDEX IF NOT EXISTS idx_user_activities ON user_activities(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_strategy_strategies ON strategy_strategies(user_id);
        CREATE INDEX IF NOT EXISTS idx_strategy_backtests ON strategy_backtests(user_id, created_at);
        CREATE TABLE IF NOT EXISTS ai_music_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, filename TEXT NOT NULL,
            prompt TEXT, engine TEXT DEFAULT 'musicgen', duration INTEGER DEFAULT 30,
            genre TEXT, mood TEXT, tempo INTEGER DEFAULT 120, status TEXT DEFAULT 'pending',
            file_size INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE INDEX IF NOT EXISTS idx_ai_music_tracks ON ai_music_tracks(user_id, created_at);
        CREATE TABLE IF NOT EXISTS paper_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, name_zh TEXT,
            description TEXT, parent_id INTEGER, sort_order INTEGER DEFAULT 0,
            color TEXT DEFAULT '#00f5ff', icon TEXT DEFAULT '📄',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(parent_id) REFERENCES paper_categories(id)
        );
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, title_zh TEXT, authors TEXT,
            year INTEGER, venue TEXT, category_id INTEGER, abstract TEXT, abstract_zh TEXT,
            keywords TEXT, doi TEXT, pdf_url TEXT, pdf_path TEXT, pdf_size INTEGER DEFAULT 0,
            source TEXT DEFAULT 'iacr', source_id TEXT, rating REAL DEFAULT 0, citation_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending', summary TEXT, summary_zh TEXT, llm_summary TEXT, llm_review TEXT,
            downloaded INTEGER DEFAULT 0, metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES paper_categories(id)
        );
        CREATE TABLE IF NOT EXISTS paper_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
            content TEXT, note_type TEXT DEFAULT 'general', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(paper_id) REFERENCES papers(id), FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS paper_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_paper_id INTEGER NOT NULL,
            target_paper_id INTEGER NOT NULL, relation_type TEXT DEFAULT 'cites', strength REAL DEFAULT 1.0,
            FOREIGN KEY(source_paper_id) REFERENCES papers(id), FOREIGN KEY(target_paper_id) REFERENCES papers(id)
        );
        CREATE TABLE IF NOT EXISTS literature_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, title TEXT NOT NULL,
            content TEXT, paper_count INTEGER DEFAULT 0, period_start TEXT, period_end TEXT,
            generated_by TEXT DEFAULT 'llm', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(category_id) REFERENCES paper_categories(id)
        );
        CREATE TABLE IF NOT EXISTS paper_download_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id INTEGER NOT NULL, status TEXT DEFAULT 'queued',
            priority INTEGER DEFAULT 5, retry_count INTEGER DEFAULT 0, error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, completed_at TIMESTAMP,
            FOREIGN KEY(paper_id) REFERENCES papers(id)
        );
        CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category_id);
        CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year DESC);
        CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(status);
        CREATE INDEX IF NOT EXISTS idx_papers_source ON papers(source, source_id);
        CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title);
        CREATE INDEX IF NOT EXISTS idx_paper_relations ON paper_relations(source_paper_id, target_paper_id);
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def log_activity(user_id: int, action: str, module: str = None, details: str = None):
    try:
        conn = get_db()
        conn.execute("INSERT INTO user_activities (user_id, action, module, details) VALUES (?,?,?,?)",
            (user_id, action, module, details))
        conn.commit(); conn.close()
    except: pass

def get_user_notes(user_id: int, module: str = None):
    conn = get_db()
    if module:
        rows = conn.execute("SELECT * FROM user_notes WHERE user_id=? AND module=? ORDER BY updated_at DESC", (user_id, module)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM user_notes WHERE user_id=? ORDER BY updated_at DESC", (user_id,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def save_user_note(user_id: int, module: str, title: str, content: str):
    conn = get_db()
    existing = conn.execute("SELECT id FROM user_notes WHERE user_id=? AND module=? AND title=?", (user_id, module, title)).fetchone()
    if existing:
        conn.execute("UPDATE user_notes SET content=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (content, existing['id']))
    else:
        conn.execute("INSERT INTO user_notes (user_id, module, title, content) VALUES (?,?,?,?)", (user_id, module, title, content))
    conn.commit(); conn.close()

def get_user_bookmarks(user_id: int, module: str = None):
    conn = get_db()
    if module:
        rows = conn.execute("SELECT * FROM user_bookmarks WHERE user_id=? AND module=? ORDER BY created_at DESC", (user_id, module)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM user_bookmarks WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def toggle_bookmark(user_id: int, module: str, item_id: int, item_type: str = None, note: str = None):
    conn = get_db()
    existing = conn.execute("SELECT id FROM user_bookmarks WHERE user_id=? AND module=? AND item_id=?", (user_id, module, item_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM user_bookmarks WHERE id=?", (existing['id'],)); conn.commit(); conn.close(); return False
    else:
        conn.execute("INSERT INTO user_bookmarks (user_id, module, item_id, item_type, note) VALUES (?,?,?,?,?)", (user_id, module, item_id, item_type, note))
        conn.commit(); conn.close(); return True

def get_user_settings(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        try: d['settings_json'] = json.loads(d.get('settings_json', '{}'))
        except: d['settings_json'] = {}
        return d
    return {'theme': 'dark', 'language': 'zh', 'notifications_enabled': 1, 'settings_json': {}}

def save_user_settings(user_id: int, settings: dict):
    conn = get_db()
    existing = conn.execute("SELECT id FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
    theme = settings.get('theme', 'dark'); lang = settings.get('language', 'zh')
    notif = settings.get('notifications_enabled', 1); enc = settings.get('data_encryption', 0)
    json_str = json.dumps(settings)
    if existing:
        conn.execute("UPDATE user_settings SET theme=?,language=?,notifications_enabled=?,data_encryption=?,settings_json=?,updated_at=CURRENT_TIMESTAMP WHERE user_id=?", (theme, lang, notif, enc, json_str, user_id))
    else:
        conn.execute("INSERT INTO user_settings (user_id,theme,language,notifications_enabled,data_encryption,settings_json) VALUES (?,?,?,?,?,?)", (user_id, theme, lang, notif, enc, json_str))
    conn.commit(); conn.close()

def save_strategy(user_id: int, name: str, code: str, description: str = None, symbols: list = None, params: dict = None):
    conn = get_db()
    conn.execute("INSERT INTO strategy_strategies (user_id,name,description,code,symbols,params) VALUES (?,?,?,?,?,?)",
        (user_id, name, description, code, json.dumps(symbols or []), json.dumps(params or {})))
    conn.commit(); conn.close()

def get_user_strategies(user_id: int):
    conn = get_db()
    rows = conn.execute("SELECT * FROM strategy_strategies WHERE user_id=? ORDER BY updated_at DESC", (user_id,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def save_backtest_result(user_id: int, result: dict, strategy_id: int = None, name: str = None):
    conn = get_db()
    conn.execute("""INSERT INTO strategy_backtests (user_id,strategy_id,name,symbols,weights,start_date,end_date,
        initial_capital,final_value,total_return,sharpe_ratio,max_drawdown,volatility,num_trades,result_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, strategy_id, name, json.dumps(result.get('symbols', [])), json.dumps(result.get('weights', [])),
         result.get('start_date'), result.get('end_date'), result.get('initial_capital'), result.get('final_value'),
         result.get('total_return'), result.get('sharpe_ratio'), result.get('max_drawdown'), result.get('volatility'),
         result.get('num_trades'), json.dumps(result)))
    conn.commit(); conn.close()

def get_user_backtests(user_id: int, limit: int = 20):
    conn = get_db()
    rows = conn.execute("SELECT * FROM strategy_backtests WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close(); return [dict(r) for r in rows]


# ========== Knowledge Base Functions ==========

def init_knowledge_tables():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS knowledge_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, name_zh TEXT,
            description TEXT, icon TEXT DEFAULT '📚', color TEXT DEFAULT '#667eea',
            sort_order INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS knowledge_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, title TEXT NOT NULL,
            content TEXT NOT NULL, summary TEXT, source TEXT DEFAULT 'manual', source_url TEXT,
            tags TEXT DEFAULT '[]', importance INTEGER DEFAULT 5, view_count INTEGER DEFAULT 0,
            is_pinned INTEGER DEFAULT 0, is_public INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES knowledge_categories(id)
        );
        CREATE TABLE IF NOT EXISTS knowledge_daily_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, title TEXT NOT NULL,
            content TEXT NOT NULL, summary TEXT, source TEXT, source_url TEXT, tags TEXT DEFAULT '[]',
            date DATE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES knowledge_categories(id)
        );
        CREATE TABLE IF NOT EXISTS knowledge_search_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, query TEXT NOT NULL,
            results_count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS knowledge_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, role TEXT NOT NULL,
            content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE INDEX IF NOT EXISTS idx_know_items_cat ON knowledge_items(category_id);
        CREATE INDEX IF NOT EXISTS idx_know_items_title ON knowledge_items(title);
        CREATE INDEX IF NOT EXISTS idx_know_daily_date ON knowledge_daily_updates(date DESC);
        CREATE INDEX IF NOT EXISTS idx_know_chat_user ON knowledge_chat_history(user_id, created_at DESC);
    """)
    for c in [(1,'tech','科技','AI前沿、编程知识','💻','#667eea',1),(2,'crypto','密码学','密码学、网络安全','🔐','#11998e',2),(3,'finance','金融','投资策略、量化交易','💰','#f7971e',3),(4,'career','职业发展','求职面试、职场技能','💼','#ff6b9d',4),(5,'academic','学术研究','论文写作、研究方法','🎓','#38ef7d',5),(6,'life','生活知识','健康、旅行、美食','🌟','#f093fb',6),(7,'news','每日热点','全网热点新闻','📰','#e74c3c',7),(8,'tutorial','教程指南','各类教程、操作指南','📖','#3498db',8)]:
        conn.execute("INSERT OR IGNORE INTO knowledge_categories VALUES (?,?,?,?,?,?,?,1,CURRENT_TIMESTAMP)", c)
    conn.commit(); conn.close()

def search_knowledge(query, category_id=None, limit=20):
    conn = get_db(); sql = "SELECT k.*,c.name_zh as category_name,c.icon FROM knowledge_items k LEFT JOIN knowledge_categories c ON k.category_id=c.id WHERE k.is_public=1"; params = []
    if query: sql += " AND (k.title LIKE ? OR k.content LIKE ? OR k.tags LIKE ?)"; params += ["%"+query+"%"]*3
    if category_id: sql += " AND k.category_id=?"; params.append(category_id)
    sql += " ORDER BY k.is_pinned DESC,k.importance DESC,k.created_at DESC LIMIT ?"; params.append(limit)
    rows = conn.execute(sql, params).fetchall(); conn.close(); return [dict(r) for r in rows]

def get_daily_knowledge(date=None, limit=50):
    conn = get_db()
    if not date: date = datetime.date.today().isoformat()
    rows = conn.execute("SELECT d.*,c.name_zh FROM knowledge_daily_updates d LEFT JOIN knowledge_categories c ON d.category_id=c.id WHERE d.date=? ORDER BY d.created_at DESC LIMIT ?",(date,limit)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def add_knowledge_item(category_id, title, content, summary=None, source='manual', source_url=None, tags=None, importance=5):
    conn = get_db()
    conn.execute("INSERT INTO knowledge_items (category_id,title,content,summary,source,source_url,tags,importance) VALUES (?,?,?,?,?,?,?,?)",
        (category_id,title,content,summary,source,source_url,json.dumps(tags or []),importance))
    conn.commit(); conn.close()

def add_daily_update(category_id, title, content, summary=None, source=None, source_url=None, tags=None, date=None):
    conn = get_db()
    if not date: date = datetime.date.today().isoformat()
    conn.execute("INSERT INTO knowledge_daily_updates (category_id,title,content,summary,source,source_url,tags,date) VALUES (?,?,?,?,?,?,?,?)",
        (category_id,title,content,summary,source,source_url,json.dumps(tags or []),date))
    conn.commit(); conn.close()

def get_chat_history(user_id, limit=50):
    conn=get_db(); rows=conn.execute("SELECT * FROM knowledge_chat_history WHERE user_id=? ORDER BY created_at DESC LIMIT ?",(user_id,limit)).fetchall()
    conn.close(); return [dict(r) for r in reversed(rows)]

def add_chat_message(user_id, role, content):
    conn=get_db(); conn.execute("INSERT INTO knowledge_chat_history (user_id,role,content) VALUES (?,?,?)",(user_id,role,content)); conn.commit(); conn.close()

def log_knowledge_search(user_id, query, results_count):
    try:
        conn = get_db()
        conn.execute("INSERT INTO knowledge_search_log (user_id,query,results_count) VALUES (?,?,?)",(user_id,query,results_count))
        conn.commit(); conn.close()
    except: pass
