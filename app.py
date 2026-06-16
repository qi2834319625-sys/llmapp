"""
Multi-System Web Portal - Main Application v3.0
FastAPI + Jinja2 + SQLite
Port 8080
"""
import os, json, sqlite3, hashlib, subprocess
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, Request, Response, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import jinja2
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from seed_data import seed_all_data

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "portal.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
SECRET_KEY = "qmlaizyh-portal-secret-key-2026"
AUTH_USERNAME = "qmlaizyh"
AUTH_PASSWORD = "qwe123123"

app = FastAPI(title="Multi-System Portal", version="3.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=jinja2.select_autoescape(["html", "xml"]),
    auto_reload=True,
)
# Add built-in functions to Jinja2 globals
_jinja_env.globals['enumerate'] = enumerate
_jinja_env.globals['len'] = len
_jinja_env.globals['range'] = range
_jinja_env.globals['int'] = int
_jinja_env.globals['float'] = float

def render(template_name, **context):
    template = _jinja_env.get_template(template_name)
    return HTMLResponse(content=template.render(**context))

serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    for d in ["photos", "videos", "files", "audio"]:
        (UPLOAD_DIR / d).mkdir(parents=True, exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS couple_photos (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, original_name TEXT, caption TEXT, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS couple_videos (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, original_name TEXT, caption TEXT, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS couple_stories (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, mood TEXT DEFAULT '💕', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS couple_timeline (id INTEGER PRIMARY KEY AUTOINCREMENT, event_date TEXT NOT NULL, title TEXT NOT NULL, description TEXT, icon TEXT DEFAULT '💕', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS recruitment_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, difficulty TEXT DEFAULT 'Medium', category TEXT, description TEXT, solution TEXT, reference_url TEXT, source TEXT DEFAULT 'LeetCode', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS github_repos (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, url TEXT, description TEXT, stars INTEGER DEFAULT 0, language TEXT, category TEXT, fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS youtube_resources (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, url TEXT, description TEXT, channel TEXT, category TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS crypto_papers (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, authors TEXT, year INTEGER, abstract TEXT, summary TEXT, keywords TEXT, venue TEXT, pdf_url TEXT, category TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS gnn_entities (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, entity_type TEXT, properties TEXT, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS gnn_relations (id INTEGER PRIMARY KEY AUTOINCREMENT, source_id INTEGER, target_id INTEGER, relation_type TEXT, weight REAL DEFAULT 1.0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(source_id) REFERENCES gnn_entities(id), FOREIGN KEY(target_id) REFERENCES gnn_entities(id));
        CREATE TABLE IF NOT EXISTS investment_records (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, asset_type TEXT, amount REAL, return_rate REAL, risk_level TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS makeup_tips (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT, content TEXT, difficulty TEXT DEFAULT 'Beginner', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS fashion_items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT, season TEXT, color TEXT, style TEXT, description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, cuisine TEXT, difficulty TEXT, cook_time INTEGER, ingredients TEXT, steps TEXT, tips TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS study_abroad (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT NOT NULL, university TEXT, program TEXT, requirements TEXT, deadline TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS civil_exam (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT NOT NULL, topic TEXT, content TEXT, question_type TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS cet_exam (id INTEGER PRIMARY KEY AUTOINCREMENT, exam_type TEXT NOT NULL, section TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, answer TEXT, difficulty TEXT DEFAULT 'Medium', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS couple_letters (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, is_read INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS couple_bucketlist (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT NOT NULL, category TEXT DEFAULT '✨', is_done INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS manga_projects (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, novel_text TEXT, style TEXT DEFAULT 'anime', status TEXT DEFAULT 'active', cover_url TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS manga_scenes (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL, scene_number INTEGER NOT NULL, title TEXT, description TEXT, characters TEXT, dialogue TEXT, image_prompt TEXT, image_url TEXT, video_url TEXT, video_task_id TEXT, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(project_id) REFERENCES manga_projects(id));
        CREATE TABLE IF NOT EXISTS manga_characters (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL, name TEXT NOT NULL, description TEXT, appearance TEXT, personality TEXT, reference_url TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(project_id) REFERENCES manga_projects(id));
    """)
    pw_hash = hashlib.sha256(AUTH_PASSWORD.encode()).hexdigest()
    conn.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", (AUTH_USERNAME, pw_hash))
    # Seed couple timeline
    if conn.execute("SELECT COUNT(*) FROM couple_timeline").fetchone()[0] == 0:
        conn.executemany("INSERT INTO couple_timeline (event_date,title,description,icon) VALUES (?,?,?,?)", [
            ("2024-01-01","我们相遇","在那个特别的那天，命运让我们相遇了 💕","💫"),
            ("2024-02-14","第一个情人节","一起度过的第一个情人节，甜蜜而难忘","💝"),
            ("2024-05-01","第一次旅行","一起去看世界，留下了美好的回忆","✈️"),
            ("2024-08-08","周年纪念","在一起一年了，感谢彼此的陪伴","🎂"),
        ])
    seed_all_data(conn)
    conn.commit()
    conn.close()
    
    # Initialize user data tables
    from database import init_user_data_tables
    init_user_data_tables()
    
    # Initialize crawler tables
    from crawler import init_crawler_tables
    init_crawler_tables()
    
    # Initialize knowledge base tables
    from database import init_knowledge_tables
    init_knowledge_tables()
    
    # Seed paper categories for key agreement research
    _seed_paper_categories()

def _seed_paper_categories():
    """Seed the paper categories for key agreement research directions"""
    conn = get_db()
    categories = [
            (1, 'DH-based', '基于 Diffie-Hellman 的密钥协商', '经典DH密钥交换协议及其变体', None, 1, '#00f5ff', '🔑'),
            (2, 'ECDH-based', '基于椭圆曲线的密钥协商', 'ECDH、ECIES等椭圆曲线密码协议', None, 2, '#ff00e5', '🌀'),
            (3, 'Post-Quantum', '后量子密钥协商', '抵抗量子计算攻击的密钥协商协议', None, 3, '#39ff14', '⚛️'),
            (4, 'Lattice-based PKE', '基于格的密钥协商', 'LWE/RLWE等格基密码方案', 3, 1, '#39ff14', '📐'),
            (5, 'Code-based', '基于编码的密钥协商', 'McEliece等编码密码方案', 3, 2, '#39ff14', '📊'),
            (6, 'MQ-based', '基于多变量的密钥协商', '多变量多项式密码方案', 3, 3, '#39ff14', '🔢'),
            (7, 'Isogeny-based', '基于同构的密钥协商', 'SIDH/SIKE等同源密码方案', 3, 4, '#39ff14', '🌊'),
            (8, 'Lightweight', '轻量级密钥协商', '适用于IoT和嵌入式设备的轻量级协议', None, 4, '#ff6b00', '📱'),
            (9, 'Group Key', '群组密钥协商', '多方参与的群组密钥协商协议', None, 5, '#b026ff', '👥'),
            (10, 'IBE-based', '基于身份的密钥协商', '基于身份的认证密钥协商协议', None, 6, '#ffe600', '🪪'),
            (11, 'Physical Layer', '物理层密钥协商', '利用无线信道特征的物理层安全密钥生成', None, 7, '#ff0040', '📡'),
            (12, 'Blockchain', '区块链密钥协商', '基于区块链的分布式密钥管理与协商', None, 8, '#4d4dff', '⛓️'),
            (13, 'TLS/SSL', 'TLS/SSL密钥协商', 'TLS握手协议及密钥交换机制', None, 9, '#00bcd4', '🔒'),
            (14, 'PAKE', '密码认证密钥协商', '基于口令的认证密钥协商协议', None, 10, '#e91e63', '🛡️'),
            (15, 'Survey/Review', '综述与调研', '密钥协商方向的综述性论文', None, 11, '#9c27b0', '📚'),
        ]
    for cat in categories:
        conn.execute(
            "INSERT OR IGNORE INTO paper_categories (id, name, name_zh, description, parent_id, sort_order, color, icon) VALUES (?,?,?,?,?,?,?,?)",
            cat
        )
    conn.commit()
    conn.close()

def create_token(username):
    return serializer.dumps({"username": username})

def verify_token(token):
    try:
        return serializer.loads(token, max_age=86400).get("username")
    except (SignatureExpired, BadSignature):
        return None

def get_current_user(request):
    token = request.cookies.get("auth_token")
    return verify_token(token) if token else None

def require_auth(request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401)
    return user

init_db()

# ========== Auth Routes ==========
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if get_current_user(request):
        return RedirectResponse("/dashboard")
    return render("login.html", request=request)

@app.post("/login")
async def login(request: Request, username=Form(...), password=Form(...)):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, pw_hash)).fetchone()
    conn.close()
    if user:
        token = create_token(username)
        resp = RedirectResponse("/dashboard", status_code=302)
        resp.set_cookie(key="auth_token", value=token, httponly=True, max_age=86400)
        return resp
    return render("login.html", request=request, error="用户名或密码错误")

@app.get("/logout")
async def logout():
    resp = RedirectResponse("/")
    resp.delete_cookie("auth_token")
    return resp

# ========== Dashboard ==========
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = require_auth(request)
    conn = get_db()
    stats = {
        "lc": conn.execute("SELECT COUNT(*) FROM recruitment_questions").fetchone()[0],
        "gh": conn.execute("SELECT COUNT(*) FROM github_repos").fetchone()[0],
        "yt": conn.execute("SELECT COUNT(*) FROM youtube_resources").fetchone()[0],
        "crypto": conn.execute("SELECT COUNT(*) FROM crypto_papers").fetchone()[0],
        "manga": conn.execute("SELECT COUNT(*) FROM manga_projects").fetchone()[0],
        "scenes": conn.execute("SELECT COUNT(*) FROM manga_scenes").fetchone()[0],
    }
    conn.close()
    return render("dashboard.html", request=request, user=user, stats=stats)

# ========== Couple Space ==========
@app.get("/couple", response_class=HTMLResponse)
async def couple_page(request: Request):
    user = require_auth(request)
    conn = get_db()
    photos = conn.execute("SELECT * FROM couple_photos ORDER BY uploaded_at DESC").fetchall()
    videos = conn.execute("SELECT * FROM couple_videos ORDER BY uploaded_at DESC").fetchall()
    stories = conn.execute("SELECT * FROM couple_stories ORDER BY created_at DESC").fetchall()
    timeline = conn.execute("SELECT * FROM couple_timeline ORDER BY event_date DESC").fetchall()
    letters = conn.execute("SELECT * FROM couple_letters ORDER BY created_at DESC").fetchall()
    bucket = conn.execute("SELECT * FROM couple_bucketlist ORDER BY created_at DESC").fetchall()
    conn.close()
    import time
    start_date = datetime(2024, 1, 1)
    return render("couple.html", request=request, user=user, photos=photos, videos=videos, stories=stories, timeline=timeline, letters=letters, bucket=bucket, days_together=(datetime.now()-start_date).days)

@app.post("/couple/upload/photo")
async def upload_photo(request: Request, file=File(...), caption=Form("")):
    require_auth(request)
    ext = os.path.splitext(file.filename)[1]
    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    filepath = UPLOAD_DIR / "photos" / filename
    with open(filepath, "wb") as f:
        f.write(await file.read())
    conn = get_db()
    conn.execute("INSERT INTO couple_photos (filename, original_name, caption) VALUES (?,?,?)", (filename, file.filename, caption))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.post("/couple/upload/video")
async def upload_video(request: Request, file=File(...), caption=Form("")):
    require_auth(request)
    ext = os.path.splitext(file.filename)[1]
    filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    filepath = UPLOAD_DIR / "videos" / filename
    with open(filepath, "wb") as f:
        f.write(await file.read())
    conn = get_db()
    conn.execute("INSERT INTO couple_videos (filename, original_name, caption) VALUES (?,?,?)", (filename, file.filename, caption))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.post("/couple/story/add")
async def add_story(request: Request, title=Form(...), content=Form(...), mood=Form("💕")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO couple_stories (title, content, mood) VALUES (?,?,?)", (title, content, mood))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.post("/couple/timeline/add")
async def add_timeline(request: Request, event_date=Form(...), title=Form(...), description=Form(""), icon=Form("💕")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO couple_timeline (event_date, title, description, icon) VALUES (?,?,?,?)", (event_date, title, description, icon))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.get("/couple/delete/{item_type}/{item_id}")
async def delete_couple_item(request: Request, item_type: str, item_id: int):
    require_auth(request)
    conn = get_db()
    # Whitelist allowed tables to prevent SQL injection
    ALLOWED_TABLES = {"photo": "couple_photos", "video": "couple_videos", "story": "couple_stories",
                       "timeline": "couple_timeline", "letter": "couple_letters", "bucket": "couple_bucketlist"}
    table = ALLOWED_TABLES.get(item_type)
    if not table:
        raise HTTPException(status_code=400, detail="无效的类型")
    if item_type in ("photo", "video"):
        row = conn.execute("SELECT filename FROM " + table + " WHERE id=?", (item_id,)).fetchone()
        if row:
            fp = UPLOAD_DIR / (item_type + "s") / row["filename"]
            if fp.exists(): fp.unlink()
        conn.execute("DELETE FROM " + table + " WHERE id=?", (item_id,))
    elif item_type == "timeline":
        conn.execute("DELETE FROM couple_timeline WHERE id=?", (item_id,))
    elif item_type == "letter":
        conn.execute("DELETE FROM couple_letters WHERE id=?", (item_id,))
    elif item_type == "bucket":
        conn.execute("DELETE FROM couple_bucketlist WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.post("/couple/letter/add")
async def add_letter(request: Request, sender=Form(...), title=Form(...), content=Form(...)):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO couple_letters (sender, title, content) VALUES (?,?,?)", (sender, title, content))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.post("/couple/bucket/add")
async def add_bucket(request: Request, item=Form(...), category=Form("✨")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO couple_bucketlist (item, category) VALUES (?,?)", (item, category))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

@app.post("/couple/bucket/toggle/{item_id}")
async def toggle_bucket(request: Request, item_id: int):
    require_auth(request)
    conn = get_db()
    conn.execute("UPDATE couple_bucketlist SET is_done=1-is_done WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/couple", status_code=302)

# ========== Recruitment ==========
@app.get("/recruitment", response_class=HTMLResponse)
async def recruitment_page(request: Request, category="", difficulty="", search="", tab="leetcode"):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM recruitment_questions WHERE 1=1"
    p = []
    if category: q += " AND category=?"; p.append(category)
    if difficulty: q += " AND difficulty=?"; p.append(difficulty)
    if search: q += " AND (title LIKE ? OR description LIKE ?)"; p.extend([f"%{search}%", f"%{search}%"])
    q += " ORDER BY id"
    questions = conn.execute(q, p).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM recruitment_questions").fetchall()
    difficulties = conn.execute("SELECT DISTINCT difficulty FROM recruitment_questions").fetchall()
    repos = conn.execute("SELECT * FROM github_repos ORDER BY stars DESC LIMIT 30").fetchall()
    youtube = conn.execute("SELECT * FROM youtube_resources ORDER BY category").fetchall()
    conn.close()
    return render("recruitment.html", request=request, user=user, questions=questions,
                   categories=categories, difficulties=difficulties, repos=repos, youtube=youtube,
                   filter_category=category, filter_difficulty=difficulty, search=search, active_tab=tab)

# ========== Crypto Papers ==========
@app.get("/crypto", response_class=HTMLResponse)
async def crypto_page(request: Request, year_from=0, year_to=2026, category="", search="", tab="papers"):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM crypto_papers WHERE year BETWEEN ? AND ?"
    p = [year_from, year_to]
    if category: q += " AND category=?"; p.append(category)
    if search: q += " AND (title LIKE ? OR summary LIKE ? OR keywords LIKE ?)"; p.extend([f"%{search}%"]*3)
    q += " ORDER BY year DESC"
    papers = conn.execute(q, p).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM crypto_papers").fetchall()
    yr = conn.execute("SELECT MIN(year), MAX(year) FROM crypto_papers").fetchone()
    conn.close()
    return render("crypto.html", request=request, user=user, papers=papers, categories=categories,
                   year_from=year_from, year_to=year_to, filter_category=category, search=search,
                   min_year=yr[0] or 1940, max_year=yr[1] or 2026, active_tab=tab)

# ========== GNN ==========
@app.get("/gnn", response_class=HTMLResponse)
async def gnn_page(request: Request):
    user = require_auth(request)
    conn = get_db()
    entities = conn.execute("SELECT * FROM gnn_entities ORDER BY entity_type, name").fetchall()
    relations = conn.execute("SELECT r.*, s.name as source_name, t.name as target_name FROM gnn_relations r JOIN gnn_entities s ON r.source_id=s.id JOIN gnn_entities t ON r.target_id=t.id").fetchall()
    conn.close()
    return render("gnn.html", request=request, user=user, entities=entities, relations=relations)

@app.post("/gnn/entity/add")
async def add_gnn_entity(request: Request, name=Form(...), entity_type=Form(...), properties=Form("{}"), description=Form("")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO gnn_entities (name, entity_type, properties, description) VALUES (?,?,?,?)", (name, entity_type, properties, description))
    conn.commit()
    conn.close()
    return RedirectResponse("/gnn", status_code=302)

@app.post("/gnn/relation/add")
async def add_gnn_relation(request: Request, source_id=Form(...), target_id=Form(...), relation_type=Form(...), weight=Form(1.0)):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO gnn_relations (source_id, target_id, relation_type, weight) VALUES (?,?,?,?)", (source_id, target_id, relation_type, weight))
    conn.commit()
    conn.close()
    return RedirectResponse("/gnn", status_code=302)

# ========== Investment ==========
@app.get("/investment", response_class=HTMLResponse)
async def investment_page(request: Request):
    user = require_auth(request)
    conn = get_db()
    records = conn.execute("SELECT * FROM investment_records ORDER BY created_at DESC").fetchall()
    conn.close()
    return render("investment.html", request=request, user=user, records=records)

@app.post("/investment/add")
async def add_investment(request: Request, name=Form(...), asset_type=Form(...), amount=Form(0), return_rate=Form(0), risk_level=Form("Medium"), notes=Form("")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO investment_records (name, asset_type, amount, return_rate, risk_level, notes) VALUES (?,?,?,?,?,?)", (name, asset_type, amount, return_rate, risk_level, notes))
    conn.commit()
    conn.close()
    return RedirectResponse("/investment", status_code=302)

# ========== Makeup ==========
@app.get("/makeup", response_class=HTMLResponse)
async def makeup_page(request: Request, category=""):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM makeup_tips"; p = []
    if category: q += " WHERE category=?"; p.append(category)
    q += " ORDER BY category"
    tips = conn.execute(q, p).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM makeup_tips").fetchall()
    conn.close()
    return render("makeup.html", request=request, user=user, tips=tips, categories=categories, filter_category=category)

# ========== Fashion ==========
@app.get("/fashion", response_class=HTMLResponse)
async def fashion_page(request: Request, season="", style=""):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM fashion_items WHERE 1=1"; p = []
    if season: q += " AND season=?"; p.append(season)
    if style: q += " AND style=?"; p.append(style)
    items = conn.execute(q, p).fetchall()
    seasons = conn.execute("SELECT DISTINCT season FROM fashion_items").fetchall()
    styles = conn.execute("SELECT DISTINCT style FROM fashion_items").fetchall()
    conn.close()
    return render("fashion.html", request=request, user=user, items=items, seasons=seasons, styles=styles, filter_season=season, filter_style=style)

# ========== Cooking ==========
@app.get("/cooking", response_class=HTMLResponse)
async def cooking_page(request: Request, cuisine="", difficulty=""):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM recipes WHERE 1=1"; p = []
    if cuisine: q += " AND cuisine=?"; p.append(cuisine)
    if difficulty: q += " AND difficulty=?"; p.append(difficulty)
    q += " ORDER BY cuisine, name"
    recipes = conn.execute(q, p).fetchall()
    cuisines = conn.execute("SELECT DISTINCT cuisine FROM recipes").fetchall()
    difficulties = conn.execute("SELECT DISTINCT difficulty FROM recipes").fetchall()
    conn.close()
    return render("cooking.html", request=request, user=user, recipes=recipes, cuisines=cuisines, difficulties=difficulties, filter_cuisine=cuisine, filter_difficulty=difficulty)

# ========== Study Abroad ==========
@app.get("/study-abroad", response_class=HTMLResponse)
async def study_abroad_page(request: Request, country=""):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM study_abroad"; p = []
    if country: q += " WHERE country=?"; p.append(country)
    q += " ORDER BY country, university"
    programs = conn.execute(q, p).fetchall()
    countries = conn.execute("SELECT DISTINCT country FROM study_abroad").fetchall()
    conn.close()
    return render("study_abroad.html", request=request, user=user, programs=programs, countries=countries, filter_country=country)

# ========== Civil Exam ==========
@app.get("/civil-exam", response_class=HTMLResponse)
async def civil_exam_page(request: Request, subject=""):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM civil_exam"; p = []
    if subject: q += " WHERE subject=?"; p.append(subject)
    q += " ORDER BY subject, id"
    topics = conn.execute(q, p).fetchall()
    subjects = conn.execute("SELECT DISTINCT subject FROM civil_exam").fetchall()
    conn.close()
    return render("civil_exam.html", request=request, user=user, topics=topics, subjects=subjects, filter_subject=subject)

# ========== CET Exam ==========
@app.get("/cet-exam", response_class=HTMLResponse)
async def cet_exam_page(request: Request, exam_type="CET-4", section="Vocabulary", search=""):
    user = require_auth(request)
    conn = get_db()
    q = "SELECT * FROM cet_exam WHERE exam_type=?"; p = [exam_type]
    if section: q += " AND section=?"; p.append(section)
    if search: q += " AND (title LIKE ? OR content LIKE ?)"; p.extend([f"%{search}%", f"%{search}%"])
    q += " ORDER BY id"
    items = conn.execute(q, p).fetchall()
    sections = conn.execute("SELECT DISTINCT section FROM cet_exam WHERE exam_type=?", (exam_type,)).fetchall()
    conn.close()
    return render("cet_exam.html", request=request, user=user, items=items, sections=sections,
                   filter_exam_type=exam_type, filter_section=section, search=search)

@app.get("/api/couple/stories")
async def api_stories(request: Request):
    require_auth(request)
    conn = get_db()
    stories = conn.execute("SELECT * FROM couple_stories ORDER BY created_at DESC").fetchall()
    conn.close()
    return JSONResponse([dict(s) for s in stories])

@app.get("/api/recruitment/stats")
async def api_recruitment_stats(request: Request):
    require_auth(request)
    conn = get_db()
    stats = conn.execute("SELECT difficulty, COUNT(*) as count FROM recruitment_questions GROUP BY difficulty").fetchall()
    conn.close()
    return JSONResponse([dict(s) for s in stats])

# ========== Manga Generation System ==========
AGNES_API_KEY = "sk-gScQfsupCor8Cp6O7pHS8IhxdbttANFlgLNQ3plVNWSToZ8R"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

@app.get("/manga", response_class=HTMLResponse)
async def manga_page(request: Request, project_id=None):
    user = require_auth(request)
    conn = get_db()
    projects = conn.execute("SELECT * FROM manga_projects ORDER BY updated_at DESC").fetchall()
    scenes = []
    characters = []
    active_project = None
    if project_id:
        active_project = conn.execute("SELECT * FROM manga_projects WHERE id=?", (project_id,)).fetchone()
        scenes = conn.execute("SELECT * FROM manga_scenes WHERE project_id=? ORDER BY scene_number", (project_id,)).fetchall()
        characters = conn.execute("SELECT * FROM manga_characters WHERE project_id=?", (project_id,)).fetchall()
    elif projects:
        active_project = projects[0]
        scenes = conn.execute("SELECT * FROM manga_scenes WHERE project_id=? ORDER BY scene_number", (active_project["id"],)).fetchall()
        characters = conn.execute("SELECT * FROM manga_characters WHERE project_id=?", (active_project["id"],)).fetchall()
    conn.close()
    return render("manga.html", request=request, user=user, projects=projects,
                   active_project=active_project, scenes=scenes, characters=characters)

@app.post("/manga/project/create")
async def create_manga_project(request: Request, title=Form(...), description=Form(""), novel_text=Form(""), style=Form("anime")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO manga_projects (title, description, novel_text, style) VALUES (?,?,?,?)",
                 (title, description, novel_text, style))
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    # Auto-generate scenes from novel text
    await auto_generate_scenes(pid, novel_text, style)
    return RedirectResponse(f"/manga?project_id={pid}", status_code=302)

async def auto_generate_scenes(project_id, novel_text, style):
    """Use Agnes AI to analyze novel and generate scene breakdown"""
    import urllib.request, urllib.parse, json
    try:
        # Ask AI to break novel into scenes
        prompt = f"""你是一位专业的漫剧导演。请将以下小说文本分解为5-8个漫剧场景。

小说内容：
{novel_text[:3000]}

请按以下JSON格式输出（只输出JSON，不要其他内容）：
{{"scenes": [{{"scene_number": 1, "title": "场景标题", "description": "场景描述（50字以内）", "characters": "出场人物", "dialogue": "关键对话", "image_prompt": "英文图像提示词，描述这个画面的视觉内容，包括人物、场景、氛围、光影等，用于AI生图"}}]}}

风格要求：{style}风格，画面要有电影感，注重人物表情和动作。"""
        
        data = json.dumps({
            "model": "agnes-2.0-flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
            "temperature": 0.8
        }).encode()
        
        req = urllib.request.Request(f"{AGNES_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            data=data)
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                scene_data = json.loads(content[start:end])
                conn = get_db()
                for scene in scene_data.get("scenes", []):
                    conn.execute("""INSERT INTO manga_scenes 
                        (project_id, scene_number, title, description, characters, dialogue, image_prompt, status) 
                        VALUES (?,?,?,?,?,?,?,?)""",
                        (project_id, scene.get("scene_number", 1), scene.get("title", ""),
                         scene.get("description", ""), scene.get("characters", ""),
                         scene.get("dialogue", ""), scene.get("image_prompt", ""), "pending"))
                conn.commit()
                conn.close()
    except Exception as e:
        print(f"Auto-generate scenes error: {e}")

@app.post("/manga/scene/generate-image")
async def generate_scene_image(request: Request, scene_id=Form(...)):
    """Generate image for a scene using Agnes AI"""
    require_auth(request)
    conn = get_db()
    scene = conn.execute("SELECT * FROM manga_scenes WHERE id=?", (scene_id,)).fetchone()
    if not scene:
        conn.close()
        return JSONResponse({"error": "Scene not found"}, status_code=404)
    
    prompt = scene["image_prompt"]
    if not prompt:
        prompt = f"anime style manga panel, {scene['description']}, {scene['characters']}, cinematic lighting, highly detailed"
    
    # Add style prefix
    style_prefix = "anime manga style, high quality, detailed illustration, cinematic composition, "
    full_prompt = style_prefix + prompt
    
    try:
        import urllib.request, urllib.parse, json
        data = json.dumps({
            "model": "agnes-image-2.1-flash",
            "prompt": full_prompt[:500],
            "size": "1024x768"
        }).encode()
        
        req = urllib.request.Request(f"{AGNES_BASE_URL}/images/generations",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            data=data)
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            image_url = result.get("data", [{}])[0].get("url", "")
            
            if image_url:
                conn.execute("UPDATE manga_scenes SET image_url=?, status='image_done' WHERE id=?", (image_url, scene_id))
                conn.commit()
                conn.close()
                return JSONResponse({"image_url": image_url, "status": "image_done"})
    except Exception as e:
        print(f"Image generation error: {e}")
    
    conn.close()
    return JSONResponse({"error": "Generation failed"}, status_code=500)

@app.post("/manga/scene/generate-video")
async def generate_scene_video(request: Request, scene_id=Form(...)):
    """Generate video for a scene using Agnes AI"""
    require_auth(request)
    conn = get_db()
    scene = conn.execute("SELECT * FROM manga_scenes WHERE id=?", (scene_id,)).fetchone()
    if not scene:
        conn.close()
        return JSONResponse({"error": "Scene not found"}, status_code=404)
    
    prompt = scene["image_prompt"] or scene["description"]
    if not prompt:
        prompt = f"anime style, {scene['characters']}, cinematic scene"
    
    try:
        import urllib.request, urllib.parse, json
        data = json.dumps({
            "model": "agnes-video-v2.0",
            "prompt": f"anime manga style, smooth camera movement, {prompt[:300]}",
            "num_frames": 81,
            "frame_rate": 24
        }).encode()
        
        req = urllib.request.Request(f"{AGNES_BASE_URL}/videos",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            data=data)
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            task_id = result.get("task_id", result.get("id", ""))
            
            if task_id:
                conn.execute("UPDATE manga_scenes SET video_task_id=?, status='video_processing' WHERE id=?", (task_id, scene_id))
                conn.commit()
                conn.close()
                return JSONResponse({"task_id": task_id, "status": "video_processing"})
    except Exception as e:
        print(f"Video generation error: {e}")
    
    conn.close()
    return JSONResponse({"error": "Generation failed"}, status_code=500)

@app.get("/manga/scene/video-status")
async def check_video_status(request: Request, task_id=""):
    """Check video generation status"""
    require_auth(request)
    import urllib.request, json
    try:
        req = urllib.request.Request(f"{AGNES_BASE_URL}/videos/{task_id}",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            status = result.get("status", "processing")
            video_url = result.get("url", result.get("video_url", ""))
            
            if video_url and status == "completed":
                conn = get_db()
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE video_task_id=?", (video_url, task_id))
                conn.commit()
                conn.close()
            
            return JSONResponse({"status": status, "video_url": video_url})
    except Exception as e:
        return JSONResponse({"status": "processing", "error": str(e)})

@app.post("/manga/character/add")
async def add_character(request: Request, project_id=Form(...), name=Form(...), description=Form(""), appearance=Form(""), personality=Form("")):
    require_auth(request)
    conn = get_db()
    conn.execute("INSERT INTO manga_characters (project_id, name, description, appearance, personality) VALUES (?,?,?,?,?)",
                 (project_id, name, description, appearance, personality))
    conn.commit()
    conn.close()
    return RedirectResponse(f"/manga?project_id={project_id}", status_code=302)

@app.get("/manga/delete/{item_type}/{item_id}")
async def delete_manga_item(request: Request, item_type: str, item_id: int):
    require_auth(request)
    conn = get_db()
    if item_type == "project":
        conn.execute("DELETE FROM manga_scenes WHERE project_id=?", (item_id,))
        conn.execute("DELETE FROM manga_characters WHERE project_id=?", (item_id,))
        conn.execute("DELETE FROM manga_projects WHERE id=?", (item_id,))
    elif item_type == "scene":
        conn.execute("DELETE FROM manga_scenes WHERE id=?", (item_id,))
    elif item_type == "character":
        conn.execute("DELETE FROM manga_characters WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return RedirectResponse("/manga", status_code=302)

@app.get("/manga/stream-video")
async def stream_video(request: Request, url: str = ""):
    """Proxy video streaming to avoid CORS issues"""
    require_auth(request)
    if not url:
        return Response(status_code=400)
    
    import urllib.request, urllib.parse
    try:
        # Validate URL
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return Response(status_code=400)
        if parsed.scheme not in ("http", "https"):
            return Response(status_code=400)
        
        import urllib.request
        range_header = request.headers.get("range", "")
        req_headers = {
            "User-Agent": "Mozilla/5.0",
        }
        if range_header:
            req_headers["Range"] = range_header
        
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read()
            status_code = resp.getcode()
            content_type = resp.headers.get("Content-Type", "video/mp4")
            content_length = resp.headers.get("Content-Length")
            content_range = resp.headers.get("Content-Range")
            accept_ranges = resp.headers.get("Accept-Ranges", "bytes")
            
            headers = {
                "Content-Type": content_type,
                "Accept-Ranges": "bytes",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=86400",
            }
            if content_length:
                headers["Content-Length"] = content_length
            if content_range:
                headers["Content-Range"] = content_range
            
            return Response(
                content=content,
                status_code=status_code if status_code != 200 else (206 if range_header else 200),
                headers=headers
            )
    except urllib.error.HTTPError as e:
        return Response(status_code=e.code)
    except Exception as e:
        print("Video stream error:", e)
        return Response(status_code=502)

@app.get("/manga/download/{project_id}")
async def download_manga_project(request: Request, project_id: int, type: str = "all"):
    """Download all generated images and videos as a zip file"""
    require_auth(request)
    import io, zipfile, urllib.request
    conn = get_db()
    project = conn.execute("SELECT * FROM manga_projects WHERE id=?", (project_id,)).fetchone()
    scenes = conn.execute("SELECT * FROM manga_scenes WHERE project_id=? ORDER BY scene_number", (project_id,)).fetchall()
    conn.close()
    
    if not project:
        return JSONResponse({"error": "Project not found"}, status_code=404)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add project info
        info_lines = [
            "Project: %s" % project['title'],
            "Style: %s" % project['style'],
            "Description: %s" % (project['description'] or 'N/A'),
            "",
            "--- Scenes ---",
        ]
        for scene in scenes:
            info_lines.append("Scene %d: %s [%s]" % (scene['scene_number'], scene['title'], scene['status']))
            if scene['dialogue']:
                info_lines.append("  Dialogue: %s" % scene['dialogue'])
            if scene['image_url']:
                info_lines.append("  Image: %s" % scene['image_url'])
            if scene['video_url']:
                info_lines.append("  Video: %s" % scene['video_url'])
            info_lines.append("")
        zf.writestr("README.txt", "\n".join(info_lines))
        
        for scene in scenes:
            # Download image if available and requested
            if scene['image_url'] and type in ("all", "images"):
                try:
                    req = urllib.request.Request(scene['image_url'], headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        img_data = resp.read()
                        ext = 'png' if 'png' in scene['image_url'].lower() else 'jpg'
                        zf.writestr("images/scene_%02d_%s.%s" % (scene['scene_number'], scene['title'], ext), img_data)
                except Exception as e:
                    print("Failed image scene %d: %s" % (scene['scene_number'], e))
            
            # Download video if available and requested
            if scene['video_url'] and type in ("all", "videos"):
                try:
                    req = urllib.request.Request(scene['video_url'], headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        vid_data = resp.read()
                        zf.writestr("videos/scene_%02d_%s.mp4" % (scene['scene_number'], scene['title']), vid_data)
                except Exception as e:
                    print("Failed video scene %d: %s" % (scene['scene_number'], e))
    
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.read(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=manga_%s_%s.zip" % (project_id, type)}
    )


# ========== Music API (iTunes Search - free, no key needed) ==========
ITUNES_SEARCH_API = "https://itunes.apple.com/search"

@app.get("/api/music/search")
async def api_music_search(request: Request, keyword="轻音乐", num=10):
    require_auth(request)
    import urllib.parse, urllib.request
    try:
        params = urllib.parse.urlencode({"term": keyword, "media": "music", "entity": "song", "limit": num})
        url = f"{ITUNES_SEARCH_API}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            songs = []
            for s in data.get("results", []):
                duration_ms = s.get("trackTimeMillis", 0)
                duration_sec = duration_ms // 1000 if duration_ms else 0
                songs.append({
                    "mid": str(s.get("trackId", "")),
                    "title": s.get("trackName", ""),
                    "singer": s.get("artistName", ""),
                    "album": s.get("collectionName", ""),
                    "interval": duration_sec,
                    "preview_url": s.get("previewUrl", ""),
                })
            return JSONResponse({"songs": songs})
    except Exception as e:
        print(f"Music search error: {e}")
    return JSONResponse({"songs": [], "error": "Search failed"})

@app.get("/api/music/proxy")
async def api_music_proxy(request: Request, url: str = ""):
    """代理音频文件，绕过CORS限制，并转码为MP3"""
    require_auth(request)
    import urllib.request, subprocess, tempfile, os
    if not url:
        return Response(status_code=400)
    try:
        from urllib.parse import unquote
        url = unquote(url)
        # 下载原始音频
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://music.apple.com/"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            audio_data = resp.read()
        
        # 用 ffmpeg 转成 MP3（浏览器兼容性更好）
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as tmp_in:
            tmp_in.write(audio_data)
            tmp_in_path = tmp_in.name
        
        tmp_out_path = tmp_in_path.replace('.m4a', '.mp3')
        result = subprocess.run(
            ['ffmpeg', '-y', '-i', tmp_in_path, '-f', 'mp3', '-ab', '128k', tmp_out_path],
            capture_output=True, timeout=30
        )
        
        if os.path.exists(tmp_out_path) and os.path.getsize(tmp_out_path) > 0:
            with open(tmp_out_path, 'rb') as f:
                mp3_data = f.read()
            # 清理临时文件
            os.unlink(tmp_in_path)
            os.unlink(tmp_out_path)
            return Response(content=mp3_data, media_type="audio/mpeg")
        
        # 转码失败，返回原始数据
        os.unlink(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)
        return Response(content=audio_data, media_type="audio/mp4")
    except Exception as e:
        print(f"Music proxy error: {e}")
    return Response(status_code=502)

# ========== Notifications API ==========
import json as _json

@app.get("/api/notifications")
async def api_notifications(request: Request):
    """Get system notifications for current user"""
    require_auth(request)
    # Return mock notifications - in production this would query a notifications table
    notifications = [
        {"id": 1, "type": "info", "title": "系统更新", "message": "Dashboard 已升级，新增天气 widget 和实时时钟", "time": "刚刚", "read": False},
        {"id": 2, "type": "success", "title": "学习提醒", "message": "你已经连续学习 7 天了，继续保持！🔥", "time": "1小时前", "read": False},
        {"id": 3, "type": "warning", "title": "考试倒计时", "message": "距离 CET-6 考试还有 15 天，加油备考！", "time": "3小时前", "read": True},
        {"id": 4, "type": "info", "title": "新功能上线", "message": "单词闯关游戏已上线，去 CET 系统试试吧！🎮", "time": "1天前", "read": True},
    ]
    return JSONResponse(notifications)

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """System settings page"""
    user = require_auth(request)
    return render("settings.html", request=request, user=user)

# ========== Market Data API (Real-time) ==========

@app.get("/api/market/stock/{symbol}")
async def api_stock_price(request: Request, symbol: str):
    """Get real-time stock price from Yahoo Finance"""
    require_auth(request)
    import urllib.request as _req
    import json as _json
    try:
        # Yahoo Finance API (free, no key)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1mo&interval=1d"
        req = _req.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with _req.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read().decode())
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            timestamps = result.get("timestamp", [])
            closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            return JSONResponse({
                "symbol": symbol,
                "price": meta.get("regularMarketPrice", 0),
                "currency": meta.get("currency", "USD"),
                "change": meta.get("regularMarketPrice", 0) - meta.get("previousClose", 0),
                "change_pct": round((meta.get("regularMarketPrice", 0) / meta.get("previousClose", 1) - 1) * 100, 2),
                "history": [{"date": str(t), "price": c} for t, c in zip(timestamps[-30:], closes[-30:]) if c],
                "name": meta.get("shortName", symbol),
            })
    except Exception as e:
        return JSONResponse({"error": str(e), "symbol": symbol}, status_code=502)

@app.get("/api/market/crypto/{coin_id}")
async def api_crypto_price(request: Request, coin_id: str):
    """Get real-time crypto price from CoinGecko (free, no key)"""
    require_auth(request)
    import urllib.request as _req
    import json as _json
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
        req = _req.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with _req.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read().decode())
            md = data.get("market_data", {})
            return JSONResponse({
                "id": coin_id,
                "name": data.get("name", coin_id),
                "symbol": data.get("symbol", "").upper(),
                "price_usd": md.get("current_price", {}).get("usd", 0),
                "price_cny": md.get("current_price", {}).get("cny", 0),
                "change_24h": md.get("price_change_percentage_24h", 0),
                "change_7d": md.get("price_change_percentage_7d", 0),
                "change_30d": md.get("price_change_percentage_30d", 0),
                "market_cap": md.get("market_cap", {}).get("usd", 0),
                "high_24h": md.get("high_24h", {}).get("usd", 0),
                "low_24h": md.get("low_24h", {}).get("usd", 0),
                "sparkline": md.get("sparkline_7d", {}).get("price", []),
            })
    except Exception as e:
        return JSONResponse({"error": str(e), "id": coin_id}, status_code=502)

@app.get("/api/market/search")
async def api_market_search(request: Request, q: str = ""):
    """Search for stocks and crypto"""
    require_auth(request)
    import urllib.request as _req
    import json as _json
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=5&newsCount=0"
        req = _req.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with _req.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read().decode())
            quotes = data.get("quotes", [])
            return JSONResponse([{
                "symbol": q.get("symbol", ""),
                "name": q.get("shortname", q.get("longname", "")),
                "type": q.get("quoteType", ""),
                "exchange": q.get("exchange", ""),
            } for q in quotes if q.get("quoteType") in ("EQUITY", "ETF", "CRYPTOCURRENCY")])
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)

# ========== Backtesting Engine ==========

@app.post("/api/backtest")
async def api_backtest(request: Request):
    """Run portfolio backtesting with simulated historical data"""
    require_auth(request)
    import json as _json
    from datetime import datetime, timedelta
    import math, random
    
    try:
        body = await request.json()
        symbols = body.get("symbols", ["AAPL", "MSFT", "GOOGL"])
        weights = body.get("weights", None)
        start_date = body.get("start_date", "2024-01-01")
        end_date = body.get("end_date", "2025-01-01")
        initial_capital = body.get("initial_capital", 100000)
        strategy = body.get("strategy", "buy_and_hold")
        
        if not weights:
            weights = [1.0 / len(symbols)] * len(symbols)
        
        # Generate simulated price data using Geometric Brownian Motion
        random.seed(42)
        sim_start = datetime.strptime(start_date, "%Y-%m-%d")
        sim_end = datetime.strptime(end_date, "%Y-%m-%d")
        
        symbol_configs = {
            "AAPL": {"base": 180, "vol": 0.02, "drift": 0.0008},
            "MSFT": {"base": 370, "vol": 0.018, "drift": 0.001},
            "GOOGL": {"base": 140, "vol": 0.022, "drift": 0.0006},
            "NVDA": {"base": 450, "vol": 0.035, "drift": 0.0015},
            "TSLA": {"base": 250, "vol": 0.04, "drift": 0.0005},
            "AMZN": {"base": 155, "vol": 0.02, "drift": 0.0007},
            "BTC-USD": {"base": 42000, "vol": 0.045, "drift": 0.0012},
            "ETH-USD": {"base": 2200, "vol": 0.05, "drift": 0.001},
            "SPY": {"base": 450, "vol": 0.012, "drift": 0.0005},
            "QQQ": {"base": 380, "vol": 0.015, "drift": 0.0007},
        }
        
        current_date = sim_start
        trading_days = []
        while current_date <= sim_end:
            if current_date.weekday() < 5:
                trading_days.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        portfolio_data = {}
        for symbol in symbols:
            config = symbol_configs.get(symbol, {"base": 100, "vol": 0.025, "drift": 0.0005})
            prices = [config["base"]]
            for i in range(1, len(trading_days)):
                ret = random.gauss(config["drift"], config["vol"])
                prices.append(prices[-1] * (1 + ret))
            portfolio_data[symbol] = {"dates": trading_days, "prices": prices}
        
        # Run backtesting simulation
        portfolio_value = []
        cash = initial_capital
        holdings = {s: 0 for s in portfolio_data}
        
        for i, date in enumerate(trading_days):
            if i == 0:
                for j, symbol in enumerate(portfolio_data):
                    price = portfolio_data[symbol]["prices"][i]
                    alloc = initial_capital * weights[j]
                    qty = int(alloc / price)
                    holdings[symbol] = qty
                    cash -= qty * price
            
            total_value = cash
            for symbol in portfolio_data:
                if holdings[symbol] > 0:
                    price = portfolio_data[symbol]["prices"][i]
                    total_value += holdings[symbol] * price
            
            portfolio_value.append({"date": date, "value": round(total_value, 2)})
            
            if strategy == "rebalance_monthly" and i > 0:
                prev_date = trading_days[i-1]
                if date[:7] != prev_date[:7]:
                    current_value = total_value
                    for j, symbol in enumerate(portfolio_data):
                        price = portfolio_data[symbol]["prices"][i]
                        target_value = current_value * weights[j]
                        target_qty = int(target_value / price)
                        diff = target_qty - holdings[symbol]
                        if diff > 0:
                            cost = diff * price
                            if cash >= cost:
                                holdings[symbol] += diff
                                cash -= cost
                        elif diff < 0:
                            proceeds = abs(diff) * price
                            holdings[symbol] += diff
                            cash += proceeds
        
        values = [p["value"] for p in portfolio_value]
        total_return = (values[-1] - values[0]) / values[0] * 100 if values else 0
        max_val = max(values) if values else 0
        max_drawdown = min((v - max_val) / max_val * 100 for v in values) if values and max_val > 0 else 0
        days = max((sim_end - sim_start).days, 1)
        years = days / 365.25
        annualized_return = ((values[-1] / values[0]) ** (1/max(years,0.01)) - 1) * 100 if values and values[0] > 0 else 0
        
        daily_returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
        avg_return = sum(daily_returns) / len(daily_returns) if daily_returns else 0
        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns) if daily_returns else 0
        annualized_vol = math.sqrt(variance) * math.sqrt(252) * 100 if variance > 0 else 0
        sharpe = (annualized_return - 4) / annualized_vol if annualized_vol > 0 else 0
        
        return JSONResponse({
            "strategy": strategy,
            "symbols": symbols,
            "weights": [round(w, 3) for w in weights],
            "start_date": trading_days[0],
            "end_date": trading_days[-1],
            "trading_days": len(trading_days),
            "initial_capital": initial_capital,
            "final_value": round(values[-1], 2),
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "volatility": round(annualized_vol, 2),
            "sharpe_ratio": round(sharpe, 2),
            "data_source": "simulated",
            "portfolio_history": portfolio_value[::max(1, len(portfolio_value)//100)],
            "holdings": {s: h for s, h in holdings.items() if h > 0},
            "remaining_cash": round(cash, 2),
        })
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()}, status_code=500)
        



# ========== Strategy Lab API ==========

@app.get("/strategy-lab", response_class=HTMLResponse)
async def strategy_lab_page(request: Request):
    """Strategy Lab - write custom trading strategies"""
    user = require_auth(request)
    return render("strategy_lab.html", request=request, user=user)

@app.post("/api/strategy/run")
async def api_strategy_run(request: Request):
    """Run user-defined strategy backtest in sandbox"""
    require_auth(request)
    import json as _json
    from datetime import datetime, timedelta
    import math, random, io, sys, traceback
    
    try:
        body = await request.json()
        code = body.get("code", "")
        symbols = body.get("symbols", ["AAPL", "MSFT"])
        start_date = body.get("start_date", "2024-01-01")
        end_date = body.get("end_date", "2024-12-31")
        initial_capital = body.get("initial_capital", 100000)
        
        if not code.strip():
            return JSONResponse({"error": "策略代码为空"}, status_code=400)
        
        # Security: block dangerous imports and operations
        blocked = ['os.', 'sys.', 'subprocess', 'importlib', '__import__', 
                    'open(', 'exec(', 'eval(', 'compile(', 'globals(', 'locals(',
                    '__builtins__', 'getattr(', 'setattr(', 'delattr(',
                    'class ', 'lambda ', 'yield ', 'raise ', 'assert ']
        for b in blocked:
            if b in code:
                return JSONResponse({"error": f"安全限制: 不允许使用 '{b}'"}, status_code=400)
        
        # Generate simulated price data
        random.seed(42)
        sim_start = datetime.strptime(start_date, "%Y-%m-%d")
        sim_end = datetime.strptime(end_date, "%Y-%m-%d")
        trading_days = []
        current = sim_start
        while current <= sim_end:
            if current.weekday() < 5:
                trading_days.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        symbol_configs = {
            "AAPL": {"base": 180, "vol": 0.02, "drift": 0.0008},
            "MSFT": {"base": 370, "vol": 0.018, "drift": 0.001},
            "GOOGL": {"base": 140, "vol": 0.022, "drift": 0.0006},
            "NVDA": {"base": 450, "vol": 0.035, "drift": 0.0015},
            "TSLA": {"base": 250, "vol": 0.04, "drift": 0.0005},
            "AMZN": {"base": 155, "vol": 0.02, "drift": 0.0007},
            "BTC-USD": {"base": 42000, "vol": 0.045, "drift": 0.0012},
            "ETH-USD": {"base": 2200, "vol": 0.05, "drift": 0.001},
            "SPY": {"base": 450, "vol": 0.012, "drift": 0.0005},
            "QQQ": {"base": 380, "vol": 0.015, "drift": 0.0007},
        }
        
        price_data = {}
        for sym in symbols:
            cfg = symbol_configs.get(sym, {"base": 100, "vol": 0.025, "drift": 0.0005})
            prices = [cfg["base"]]
            for i in range(1, len(trading_days)):
                ret = random.gauss(cfg["drift"], cfg["vol"])
                prices.append(prices[-1] * (1 + ret))
            price_data[sym] = prices
        
        # Build the strategy execution environment
        holdings = {s: 0 for s in symbols}
        cash = initial_capital
        portfolio_history = []
        trades = []
        logs = []
        
        # Helper functions available to user code
        def get_price(symbol, day_idx):
            """Get price of symbol at day index"""
            if symbol in price_data and 0 <= day_idx < len(price_data[symbol]):
                return price_data[symbol][day_idx]
            return None
        
        def get_prices(symbol):
            """Get full price history of symbol"""
            return price_data.get(symbol, [])
        
        def buy(symbol, amount, day_idx):
            """Buy with cash amount. Returns shares bought."""
            price = get_price(symbol, day_idx)
            if price and price > 0 and cash >= amount:
                qty = int(amount / price)
                if qty > 0:
                    cost = qty * price
                    holdings[symbol] += qty
                    trades.append({"day": day_idx, "date": trading_days[day_idx], "action": "BUY", "symbol": symbol, "qty": qty, "price": round(price, 2), "cost": round(cost, 2)})
                    return qty
            return 0
        
        def sell(symbol, qty, day_idx):
            """Sell shares. Returns cash received."""
            price = get_price(symbol, day_idx)
            if price and holdings[symbol] >= qty > 0:
                holdings[symbol] -= qty
                proceeds = qty * price
                trades.append({"day": day_idx, "date": trading_days[day_idx], "action": "SELL", "symbol": symbol, "qty": qty, "price": round(price, 2), "proceeds": round(proceeds, 2)})
                return proceeds
            return 0
        
        def get_portfolio_value(day_idx):
            """Get total portfolio value at day index"""
            val = cash
            for s in symbols:
                p = get_price(s, day_idx)
                if p:
                    val += holdings[s] * p
            return val
        
        def log(msg):
            """Log a message"""
            logs.append(str(msg))
        
        def sma(symbol, period, day_idx):
            """Simple Moving Average"""
            prices = get_prices(symbol)
            if day_idx < period - 1:
                return None
            return sum(prices[day_idx-period+1:day_idx+1]) / period
        
        def ema(symbol, period, day_idx):
            """Exponential Moving Average"""
            prices = get_prices(symbol)
            if day_idx < period - 1:
                return None
            k = 2 / (period + 1)
            e = prices[day_idx - period + 1]
            for i in range(day_idx - period + 2, day_idx + 1):
                e = prices[i] * k + e * (1 - k)
            return e
        
        def rsi(symbol, period, day_idx):
            """Relative Strength Index"""
            prices = get_prices(symbol)
            if day_idx < period:
                return None
            gains, losses = [], []
            for i in range(day_idx - period + 1, day_idx + 1):
                d = prices[i] - prices[i-1]
                gains.append(max(d, 0))
                losses.append(max(-d, 0))
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            if avg_loss == 0:
                return 100
            rs = avg_gain / avg_loss
            return 100 - 100 / (1 + rs)
        
        # Execute user strategy
        safe_globals = {
            "__builtins__": {
                "len": len, "range": range, "int": int, "float": float,
                "str": str, "abs": abs, "min": min, "max": max, "sum": sum,
                "round": round, "print": log, "enumerate": enumerate,
                "zip": zip, "list": list, "dict": dict, "tuple": tuple,
                "True": True, "False": False, "None": None,
            },
            "math": math,
            "get_price": get_price,
            "get_prices": get_prices,
            "buy": buy,
            "sell": sell,
            "get_portfolio_value": get_portfolio_value,
            "log": log,
            "sma": sma,
            "ema": ema,
            "rsi": rsi,
            "symbols": symbols,
            "num_days": len(trading_days),
            "initial_capital": initial_capital,
            "cash": cash,
            "holdings": holdings,
        }
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            exec(code, safe_globals)
        except Exception as e:
            sys.stdout = old_stdout
            return JSONResponse({
                "error": f"策略执行错误: {str(e)}",
                "trace": traceback.format_exc(),
                "logs": logs,
            }, status_code=400)
        
        sys.stdout = old_stdout
        
        # Calculate final portfolio value for each day
        for i in range(len(trading_days)):
            val = safe_globals.get("cash", cash)
            for s in symbols:
                h = safe_globals.get("holdings", holdings).get(s, 0)
                p = get_price(s, i)
                if p:
                    val += h * p
            portfolio_history.append({"date": trading_days[i], "value": round(val, 2)})
        
        # Get trades from safe_globals (user may have modified)
        final_trades = safe_globals.get("_trades", trades)
        final_cash = safe_globals.get("cash", cash)
        final_holdings = safe_globals.get("holdings", holdings)
        
        # Calculate metrics
        values = [p["value"] for p in portfolio_history]
        total_return = (values[-1] - values[0]) / values[0] * 100 if values and values[0] > 0 else 0
        max_val = max(values) if values else 0
        max_drawdown = min((v - max_val) / max_val * 100 for v in values) if values and max_val > 0 else 0
        days = max((sim_end - sim_start).days, 1)
        years = days / 365.25
        annualized_return = ((values[-1] / values[0]) ** (1/max(years,0.01)) - 1) * 100 if values and values[0] > 0 else 0
        daily_returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
        avg_ret = sum(daily_returns) / len(daily_returns) if daily_returns else 0
        var = sum((r - avg_ret)**2 for r in daily_returns) / len(daily_returns) if daily_returns else 0
        ann_vol = math.sqrt(var) * math.sqrt(252) * 100 if var > 0 else 0
        sharpe = (annualized_return - 4) / ann_vol if ann_vol > 0 else 0
        
        return JSONResponse({
            "success": True,
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "volatility": round(ann_vol, 2),
            "sharpe_ratio": round(sharpe, 2),
            "final_value": round(values[-1], 2) if values else initial_capital,
            "initial_capital": initial_capital,
            "trading_days": len(trading_days),
            "num_trades": len(final_trades),
            "trades": final_trades[:50],
            "portfolio_history": portfolio_history[::max(1, len(portfolio_history)//200)],
            "holdings": {s: h for s, h in final_holdings.items() if h > 0},
            "remaining_cash": round(final_cash, 2),
            "logs": logs[:100],
        })
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()}, status_code=500)


# ========== User Data API ==========

def _get_user_id(request):
    """Get current user ID from token"""
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401)
    conn = get_db()
    user = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401)
    return user["id"]

@app.get("/api/user/notes")
async def api_get_notes(request: Request, module: str = None):
    uid = _get_user_id(request)
    from database import get_user_notes
    return JSONResponse(get_user_notes(uid, module))

@app.post("/api/user/notes")
async def api_save_note(request: Request):
    uid = _get_user_id(request)
    body = await request.json()
    from database import save_user_note
    save_user_note(uid, body.get("module",""), body.get("title",""), body.get("content",""))
    return JSONResponse({"success": True})

@app.get("/api/user/bookmarks")
async def api_get_bookmarks(request: Request, module: str = None):
    uid = _get_user_id(request)
    from database import get_user_bookmarks
    return JSONResponse(get_user_bookmarks(uid, module))

@app.post("/api/user/bookmark/toggle")
async def api_toggle_bookmark(request: Request):
    uid = _get_user_id(request)
    body = await request.json()
    from database import toggle_bookmark
    is_bookmarked = toggle_bookmark(uid, body.get("module",""), body.get("item_id",0), body.get("item_type"), body.get("note"))
    return JSONResponse({"bookmarked": is_bookmarked})

@app.get("/api/user/settings")
async def api_get_settings(request: Request):
    uid = _get_user_id(request)
    from database import get_user_settings
    return JSONResponse(get_user_settings(uid))

@app.post("/api/user/settings")
async def api_save_settings(request: Request):
    uid = _get_user_id(request)
    body = await request.json()
    from database import save_user_settings
    save_user_settings(uid, body)
    return JSONResponse({"success": True})

@app.get("/api/user/stats")
async def api_get_user_stats(request: Request):
    uid = _get_user_id(request)
    conn = get_db()
    stats = {
        "notes": conn.execute("SELECT COUNT(*) FROM user_notes WHERE user_id=?", (uid,)).fetchone()[0],
        "bookmarks": conn.execute("SELECT COUNT(*) FROM user_bookmarks WHERE user_id=?", (uid,)).fetchone()[0],
        "strategies": conn.execute("SELECT COUNT(*) FROM strategy_strategies WHERE user_id=?", (uid,)).fetchone()[0],
        "backtests": conn.execute("SELECT COUNT(*) FROM strategy_backtests WHERE user_id=?", (uid,)).fetchone()[0],
    }
    conn.close()
    return JSONResponse(stats)

@app.get("/api/user/strategies")
async def api_get_strategies(request: Request):
    uid = _get_user_id(request)
    from database import get_user_strategies
    return JSONResponse(get_user_strategies(uid))

@app.post("/api/user/strategies")
async def api_save_strategy(request: Request):
    uid = _get_user_id(request)
    body = await request.json()
    from database import save_strategy
    save_strategy(uid, body.get("name",""), body.get("code",""), body.get("description"), body.get("symbols"), body.get("params"))
    return JSONResponse({"success": True})

@app.get("/api/user/backtests")
async def api_get_backtests(request: Request, limit: int = 20):
    uid = _get_user_id(request)
    from database import get_user_backtests
    return JSONResponse(get_user_backtests(uid, limit))

# ========== AI Music Generation API ==========

@app.get("/ai-music", response_class=HTMLResponse)
async def ai_music_page(request: Request):
    """AI Music Generation Studio"""
    user = require_auth(request)
    return render("ai_music.html", request=request, user=user)

@app.post("/api/ai-music/generate")
async def api_ai_music_generate(request: Request):
    """Generate AI music using various engines"""
    require_auth(request)
    import urllib.request as _req
    import json as _json
    import os, time, hashlib
    
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        engine = body.get("engine", "musicgen")  # musicgen, stable_audio, suno, udio
        duration = min(body.get("duration", 30), 120)  # Max 120 seconds
        genre = body.get("genre", "")
        tempo = body.get("tempo", 120)
        mood = body.get("mood", "")
        instruments = body.get("instruments", [])
        melody_notes = body.get("melody_notes", [])  # Custom melody
        key = body.get("key", "C")
        scale = body.get("scale", "major")
        
        if not prompt:
            return JSONResponse({"error": "请输入音乐描述"}, status_code=400)
        
        # Build enhanced prompt with musical parameters
        enhanced_prompt = prompt
        if genre:
            enhanced_prompt += f", {genre} style"
        if mood:
            enhanced_prompt += f", {mood} mood"
        if instruments:
            enhanced_prompt += f", featuring {', '.join(instruments)}"
        if tempo:
            enhanced_prompt += f", {tempo} BPM"
        if key and scale:
            enhanced_prompt += f" key of {key} {scale}"
        
        # Generate unique filename
        timestamp = str(int(time.time()))
        file_hash = hashlib.md5(f"{prompt}{timestamp}".encode()).hexdigest()[:12]
        filename = f"ai_music_{file_hash}.mp3"
        output_dir = os.path.join(os.path.dirname(__file__), "static", "audio", "generated")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        result = {
            "success": True,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "engine": engine,
            "duration": duration,
            "filename": filename,
            "url": f"/static/audio/generated/{filename}",
            "timestamp": timestamp,
        }
        
        if engine == "musicgen":
            # Use HuggingFace MusicGen API (free tier)
            try:
                api_url = "https://api-inference.huggingface.co/models/facebook/musicgen-medium"
                api_key = os.environ.get("HF_API_KEY", "")
                
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                
                payload = _json.dumps({
                    "inputs": enhanced_prompt,
                    "parameters": {"duration": duration}
                }).encode()
                
                req = _req.Request(api_url, data=payload, headers=headers, method="POST")
                with _req.urlopen(req, timeout=120) as resp:
                    audio_data = resp.read()
                    if len(audio_data) > 1000:
                        with open(output_path, "wb") as f:
                            f.write(audio_data)
                        result["status"] = "completed"
                        result["format"] = "wav"
                    else:
                        result["status"] = "failed"
                        result["error"] = "API returned empty response"
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                
        elif engine == "stable_audio":
            # Use Stability AI Stable Audio API
            try:
                api_url = "https://api.stability.ai/v2beta/audio/stable-audio-3/generate"
                api_key = os.environ.get("STABILITY_API_KEY", "")
                
                if not api_key:
                    result["status"] = "no_api_key"
                    result["error"] = "需要 Stability AI API Key"
                else:
                    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
                    body_parts = []
                    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="prompt"\r\n\r\n{enhanced_prompt}\r\n')
                    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="duration"\r\n\r\n{duration}\r\n')
                    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="format"\r\n\r\nmp3\r\n')
                    body_parts.append(f'--{boundary}--\r\n')
                    payload = ''.join(body_parts).encode()
                    
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": f"multipart/form-data; boundary={boundary}",
                    }
                    req = _req.Request(api_url, data=payload, headers=headers, method="POST")
                    with _req.urlopen(req, timeout=120) as resp:
                        data = _json.loads(resp.read().decode())
                        if "audio" in data:
                            import base64
                            audio_data = base64.b64decode(data["audio"])
                            with open(output_path, "wb") as f:
                                f.write(audio_data)
                            result["status"] = "completed"
                        else:
                            result["status"] = "failed"
                            result["error"] = str(data)
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
        
        elif engine == "suno":
            # Suno API (requires API key)
            api_key = os.environ.get("SUNO_API_KEY", "")
            if not api_key:
                result["status"] = "no_api_key"
                result["error"] = "需要 Suno API Key"
            else:
                try:
                    api_url = "https://api.sunoapi.com/v1/generate"
                    payload = _json.dumps({
                        "prompt": enhanced_prompt,
                        "duration": duration,
                        "make_instrumental": len(instruments) == 0,
                    }).encode()
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    req = _req.Request(api_url, data=payload, headers=headers, method="POST")
                    with _req.urlopen(req, timeout=60) as resp:
                        data = _json.loads(resp.read().decode())
                        if data.get("status") == "completed" and data.get("audio_url"):
                            audio_url = data["audio_url"]
                            with _req.urlopen(audio_url, timeout=60) as audio_resp:
                                with open(output_path, "wb") as f:
                                    f.write(audio_resp.read())
                            result["status"] = "completed"
                        else:
                            result["status"] = "processing"
                            result["task_id"] = data.get("task_id", "")
                except Exception as e:
                    result["status"] = "failed"
                    result["error"] = str(e)
        
        else:
            result["status"] = "unknown_engine"
            result["error"] = f"未知引擎: {engine}"
        
        # Save to database
        try:
            conn = get_db()
            uid = _get_user_id(request)
            conn.execute(
                """INSERT INTO ai_music_tracks 
                   (user_id, filename, prompt, engine, duration, genre, mood, tempo, status, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)""",
                (uid, filename, prompt, engine, duration, genre, mood, tempo, result.get("status", "unknown"))
            )
            conn.commit()
            conn.close()
        except:
            pass
        
        return JSONResponse(result)
        
    except Exception as e:
        import traceback
        return JSONResponse({"error": str(e), "trace": traceback.format_exc()}, status_code=500)

@app.get("/api/ai-music/library")
async def api_ai_music_library(request: Request):
    """Get user's generated music library"""
    uid = _get_user_id(request)
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM ai_music_tracks WHERE user_id=? ORDER BY created_at DESC LIMIT 50",
        (uid,)
    ).fetchall()
    conn.close()
    return JSONResponse([dict(r) for r in rows])

@app.delete("/api/ai-music/{track_id}")
async def api_ai_music_delete(request: Request, track_id: int):
    """Delete a generated track"""
    uid = _get_user_id(request)
    conn = get_db()
    row = conn.execute("SELECT filename FROM ai_music_tracks WHERE id=? AND user_id=?", (track_id, uid)).fetchone()
    if row:
        # Delete file
        filepath = os.path.join(os.path.dirname(__file__), "static", "audio", "generated", row["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
        conn.execute("DELETE FROM ai_music_tracks WHERE id=?", (track_id,))
        conn.commit()
    conn.close()
    return JSONResponse({"success": True})

# ========== Register Paper Routes ==========
from paper_api import register_paper_routes
register_paper_routes(app)

# ========== Register Crawler Routes ==========
from crawler_api import register_crawler_routes
register_crawler_routes(app)

# ========== System Health API ==========
@app.get("/api/system/health")
async def api_system_health(request: Request):
    """System health check - returns status of all subsystems"""
    require_auth(request)
    conn = get_db()
    
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "dashboard": {"status": "ok", "description": "控制台"},
            "investment": {"status": "ok", "records": conn.execute("SELECT COUNT(*) FROM investment_records").fetchone()[0]},
            "crypto": {"status": "ok", "papers": conn.execute("SELECT COUNT(*) FROM crypto_papers").fetchone()[0]},
            "recruitment": {"status": "ok", "questions": conn.execute("SELECT COUNT(*) FROM recruitment_questions").fetchone()[0]},
            "papers": {"status": "ok", "total": conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0], "downloaded": conn.execute("SELECT COUNT(*) FROM papers WHERE downloaded=1").fetchone()[0]},
            "ai_music": {"status": "ok", "tracks": conn.execute("SELECT COUNT(*) FROM ai_music_tracks").fetchone()[0]},
            "strategy_lab": {"status": "ok", "strategies": conn.execute("SELECT COUNT(*) FROM strategy_strategies").fetchone()[0]},
            "crawler": {"status": "ok", "sources": conn.execute("SELECT COUNT(*) FROM crawl_sources WHERE is_active=1").fetchone()[0], "queue": conn.execute("SELECT COUNT(*) FROM paper_fetch_queue WHERE status='queued'").fetchone()[0]},
        },
        "database": {
            "path": "data/portal.db",
            "size_mb": round(os.path.getsize("data/portal.db") / 1048576, 2) if os.path.exists("data/portal.db") else 0
        }
    }
    conn.close()
    return JSONResponse(health)

# ========== Register Crawler Routes ==========
from crawler_api import register_crawler_routes
register_crawler_routes(app)

# ========== Register Knowledge Routes ==========
from knowledge_api import register_knowledge_routes
register_knowledge_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
