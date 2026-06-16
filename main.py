"""
Portal Main Application
FastAPI backend with all API endpoints
"""
import os
import shutil
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

from database import engine, get_db, Base
from models import (
    User, CoupleMedia, CoupleStory, LeetCodeProblem, GitHubRepo,
    YouTubeVideo, CryptoPaper, GNNResource, InvestmentResource,
    MakeupResource, FashionResource, CookingResource, AbroadResource, CivilResource
)
from auth import (
    hash_password, verify_password, create_token,
    verify_token, init_user
)
from seed_data import seed_all_data

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portal System", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("static/modules", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)
os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ========== Pydantic Schemas ==========
class LoginRequest(BaseModel):
    username: str
    password: str


class StoryCreate(BaseModel):
    title: str
    content: str
    mood: str = "romantic"


class ResourceCreate(BaseModel):
    title: str
    content: str
    url: str = ""
    tags: str = ""


# ========== Startup ==========
@app.on_event("startup")
def startup():
    db = next(get_db())
    init_user(db)
    seed_all_data(db)


# ========== Login ==========
@app.post("/api/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.username)
    return {"token": token, "username": user.username}


@app.get("/api/verify")
def verify(user=Depends(verify_token)):
    return {"username": user.username}


# ========== Couple Space ==========
@app.post("/api/couple/upload")
async def upload_media(
    file: UploadFile = File(...),
    description: str = Form(""),
    user=Depends(verify_token)
):
    content_type = file.content_type or ""
    if content_type.startswith("video"):
        subdir = "videos"
        ftype = "video"
    else:
        subdir = "photos"
        ftype = "photo"

    save_path = f"uploads/{subdir}/{file.filename}"
    with open(save_path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)

    db = next(get_db())
    media = CoupleMedia(
        filename=file.filename,
        original_name=file.filename,
        file_type=ftype,
        file_path=save_path,
        description=description
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"id": media.id, "filename": media.filename, "type": ftype}


@app.get("/api/couple/media")
def list_media(type_filter: Optional[str] = None, user=Depends(verify_token)):
    db = next(get_db())
    q = db.query(CoupleMedia)
    if type_filter:
        q = q.filter(CoupleMedia.file_type == type_filter)
    items = q.order_by(CoupleMedia.uploaded_at.desc()).all()
    return [{
        "id": i.id, "filename": i.filename, "original_name": i.original_name,
        "file_type": i.file_type, "file_path": i.file_path,
        "description": i.description, "uploaded_at": str(i.uploaded_at)
    } for i in items]


@app.delete("/api/couple/media/{media_id}")
def delete_media(media_id: int, user=Depends(verify_token)):
    db = next(get_db())
    m = db.query(CoupleMedia).filter(CoupleMedia.id == media_id).first()
    if not m:
        raise HTTPException(404, "Not found")
    if os.path.exists(m.file_path):
        os.remove(m.file_path)
    db.delete(m)
    db.commit()
    return {"ok": True}


@app.post("/api/couple/story")
def create_story(story: StoryCreate, user=Depends(verify_token)):
    db = next(get_db())
    s = CoupleStory(title=story.title, content=story.content, mood=story.mood)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "title": s.title}


@app.get("/api/couple/stories")
def list_stories(user=Depends(verify_token)):
    db = next(get_db())
    items = db.query(CoupleStory).order_by(CoupleStory.created_at.desc()).all()
    return [{
        "id": i.id, "title": i.title, "content": i.content,
        "mood": i.mood, "created_at": str(i.created_at)
    } for i in items]


@app.delete("/api/couple/story/{story_id}")
def delete_story(story_id: int, user=Depends(verify_token)):
    db = next(get_db())
    s = db.query(CoupleStory).filter(CoupleStory.id == story_id).first()
    if not s:
        raise HTTPException(404)
    db.delete(s)
    db.commit()
    return {"ok": True}


# ========== Recruitment ==========
@app.get("/api/recruitment/leetcode")
def get_leetcode(search: Optional[str] = None, difficulty: Optional[str] = None,
                 tag: Optional[str] = None, page: int = 1, size: int = 20):
    db = next(get_db())
    q = db.query(LeetCodeProblem)
    if search:
        q = q.filter(LeetCodeProblem.title.contains(search) | LeetCodeProblem.number == int(search) if search.isdigit() else LeetCodeProblem.title.contains(search))
    if difficulty:
        q = q.filter(LeetCodeProblem.difficulty == difficulty)
    if tag:
        q = q.filter(LeetCodeProblem.tags.contains(tag))
    total = q.count()
    items = q.offset((page-1)*size).limit(size).all()
    return {
        "total": total, "page": page, "size": size,
        "items": [{"id": i.id, "number": i.number, "title": i.title,
                    "difficulty": i.difficulty, "tags": i.tags,
                    "description": i.description, "solution": i.solution,
                    "reference_url": i.reference_url} for i in items]
    }


@app.get("/api/recruitment/github")
def get_github(category: Optional[str] = None, language: Optional[str] = None):
    db = next(get_db())
    q = db.query(GitHubRepo)
    if category:
        q = q.filter(GitHubRepo.category == category)
    if language:
        q = q.filter(GitHubRepo.language == language)
    items = q.order_by(GitHubRepo.stars.desc()).all()
    return [{"id": i.id, "name": i.name, "url": i.url, "description": i.description,
             "language": i.language, "stars": i.stars, "category": i.category} for i in items]


@app.get("/api/recruitment/youtube")
def get_youtube(category: Optional[str] = None):
    db = next(get_db())
    q = db.query(YouTubeVideo)
    if category:
        q = q.filter(YouTubeVideo.category == category)
    items = q.all()
    return [{"id": i.id, "title": i.title, "video_id": i.video_id,
             "description": i.description, "category": i.category} for i in items]


# ========== Cryptography ==========
@app.get("/api/crypto/papers")
def get_papers(category: Optional[str] = None, year_from: Optional[int] = None,
               year_to: Optional[int] = None, classic_only: bool = False,
               search: Optional[str] = None):
    db = next(get_db())
    q = db.query(CryptoPaper)
    if category:
        q = q.filter(CryptoPaper.category == category)
    if year_from:
        q = q.filter(CryptoPaper.year >= year_from)
    if year_to:
        q = q.filter(CryptoPaper.year <= year_to)
    if classic_only:
        q = q.filter(CryptoPaper.is_classic == 1)
    if search:
        q = q.filter(CryptoPaper.title.contains(search) | CryptoPaper.abstract.contains(search))
    items = q.order_by(CryptoPaper.year.desc()).all()
    return [{
        "id": i.id, "title": i.title, "authors": i.authors,
        "year": i.year, "category": i.category,
        "abstract": i.abstract, "ai_summary": i.ai_summary,
        "url": i.url, "is_classic": i.is_classic
    } for i in items]


@app.get("/api/crypto/timeline")
def get_crypto_timeline():
    db = next(get_db())
    papers = db.query(CryptoPaper).order_by(CryptoPaper.year).all()
    timeline = {}
    for p in papers:
        y = str(p.year)
        if y not in timeline:
            timeline[y] = []
        timeline[y].append({"title": p.title, "category": p.category,
                            "ai_summary": p.ai_summary, "is_classic": p.is_classic})
    return timeline


# ========== GNN ==========
@app.get("/api/gnn/resources")
def get_gnn_resources(category: Optional[str] = None):
    db = next(get_db())
    q = db.query(GNNResource)
    if category:
        q = q.filter(GNNResource.category == category)
    items = q.all()
    return [{"id": i.id, "title": i.title, "resource_type": i.resource_type,
             "description": i.description, "url": i.url,
             "category": i.category} for i in items]


# ========== Generic Resource Endpoints ==========
def make_resource_endpoints(name: str, model_cls, path: str):
    @app.get(f"/api/{path}")
    def list_resources(tag: Optional[str] = None):
        db = next(get_db())
        q = db.query(model_cls)
        if tag and hasattr(model_cls, 'tags'):
            q = q.filter(model_cls.tags.contains(tag))
        items = q.all()
        result = []
        for i in items:
            d = {c.name: getattr(i, c.name) for c in i.__table__.columns}
            result.append(d)
        return result

    @app.post(f"/api/{path}")
    def create_resource(data: dict, user=Depends(verify_token)):
        db = next(get_db())
        item = model_cls(**data)
        db.add(item)
        db.commit()
        return {"id": item.id}

    @app.delete(f"/api/{path}/{{item_id}}")
    def delete_resource(item_id: int, user=Depends(verify_token)):
        db = next(get_db())
        item = db.query(model_cls).filter(model_cls.id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
        return {"ok": True}


make_resource_endpoints("investment", InvestmentResource, "investment")
make_resource_endpoints("makeup", MakeupResource, "makeup")
make_resource_endpoints("fashion", FashionResource, "fashion")
make_resource_endpoints("cooking", CookingResource, "cooking")
make_resource_endpoints("abroad", AbroadResource, "abroad")
make_resource_endpoints("civil", CivilResource, "civil")


# ========== Serve Frontend Pages ==========
@app.get("/", response_class=HTMLResponse)
def serve_login():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/main", response_class=HTMLResponse)
def serve_main():
    with open("static/main.html", "r", encoding="utf-8") as f:
        return f.read()


def serve_module(name: str):
    with open(f"static/modules/{name}.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/couple", response_class=HTMLResponse)
def cp(): return serve_module("couple")

@app.get("/recruitment", response_class=HTMLResponse)
def rec(): return serve_module("recruitment")

@app.get("/crypto", response_class=HTMLResponse)
def cr(): return serve_module("crypto")

@app.get("/gnn", response_class=HTMLResponse)
def gn(): return serve_module("gnn")

@app.get("/investment", response_class=HTMLResponse)
def inv(): return serve_module("investment")

@app.get("/makeup", response_class=HTMLResponse)
def mk(): return serve_module("makeup")

@app.get("/fashion", response_class=HTMLResponse)
def fa(): return serve_module("fashion")

@app.get("/cooking", response_class=HTMLResponse)
def co(): return serve_module("cooking")

@app.get("/abroad", response_class=HTMLResponse)
def ab(): return serve_module("abroad")

@app.get("/civil", response_class=HTMLResponse)
def ci(): return serve_module("civil")
