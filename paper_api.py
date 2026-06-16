"""
Paper management API routes for key agreement research.
"""
import os, json, hashlib, time
from pathlib import Path

PAPER_DIR = Path(__file__).parent / "static" / "papers"
PAPER_DIR.mkdir(parents=True, exist_ok=True)

def register_paper_routes(app):
    """Register all paper-related routes"""
    
    from fastapi import Request, HTTPException, Form
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    import app as _app
    
    def require_auth(request):
        return _app.require_auth(request)
    
    def get_db():
        return _app.get_db()
    
    def render(tpl, **ctx):
        return _app.render(tpl, **ctx)
    
    def get_user_id(request):
        username = _app.get_current_user(request)
        if not username:
            raise HTTPException(status_code=401)
        conn = get_db()
        user = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        return user["id"] if user else None
    
    # ========== SPECIFIC ROUTES FIRST (before parameterized routes) ==========
    
    # --- HTML Pages ---
    @app.get("/papers", response_class=HTMLResponse)
    async def papers_page(request: Request):
        user = require_auth(request)
        return render("papers.html", request=request, user=user)
    
    @app.get("/papers/timeline", response_class=HTMLResponse)
    async def papers_timeline(request: Request):
        user = require_auth(request)
        return render("papers_timeline.html", request=request, user=user)
    
    @app.get("/papers/review/{category_id}", response_class=HTMLResponse)
    async def papers_review(request: Request, category_id: int):
        user = require_auth(request)
        return render("papers_review.html", request=request, user=user, category_id=category_id)
    
    # --- API: Categories (MUST be before /api/papers/{paper_id}) ---
    @app.get("/api/papers/categories")
    async def api_paper_categories(request: Request):
        require_auth(request)
        conn = get_db()
        rows = conn.execute("SELECT * FROM paper_categories ORDER BY sort_order, name").fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])
    
    @app.get("/api/papers/stats")
    async def api_papers_stats(request: Request):
        require_auth(request)
        conn = get_db()
        stats = {
            "total": conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
            "downloaded": conn.execute("SELECT COUNT(*) FROM papers WHERE downloaded=1").fetchone()[0],
            "by_category": [dict(r) for r in conn.execute("SELECT c.name, c.name_zh, c.color, COUNT(p.id) as count FROM paper_categories c LEFT JOIN papers p ON c.id=p.category_id GROUP BY c.id ORDER BY count DESC").fetchall()],
            "by_year": [dict(r) for r in conn.execute("SELECT year, COUNT(*) as count FROM papers WHERE year>0 GROUP BY year ORDER BY year DESC LIMIT 10").fetchall()],
            "recent": [dict(r) for r in conn.execute("SELECT id, title, year, created_at FROM papers ORDER BY created_at DESC LIMIT 5").fetchall()],
        }
        conn.close()
        return JSONResponse(stats)
    
    @app.get("/api/papers/reviews")
    async def api_get_reviews(request: Request, category_id: int = None):
        require_auth(request)
        conn = get_db()
        if category_id:
            rows = conn.execute("SELECT * FROM literature_reviews WHERE category_id=? ORDER BY created_at DESC", (category_id,)).fetchall()
        else:
            rows = conn.execute("SELECT r.*, c.name as category_name FROM literature_reviews r LEFT JOIN paper_categories c ON r.category_id=c.id ORDER BY r.created_at DESC").fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])
    
    # --- API: Papers CRUD ---
    @app.get("/api/papers")
    async def api_papers_list(request: Request, category_id: int = None, year: int = None, 
                               search: str = "", status: str = None, page: int = 1, per_page: int = 20):
        require_auth(request)
        conn = get_db()
        query = "SELECT p.*, c.name as category_name, c.color as category_color, c.icon as category_icon FROM papers p LEFT JOIN paper_categories c ON p.category_id=c.id WHERE 1=1"
        params = []
        if category_id:
            query += " AND p.category_id=?"
            params.append(category_id)
        if year:
            query += " AND p.year=?"
            params.append(year)
        if search:
            query += " AND (p.title LIKE ? OR p.authors LIKE ? OR p.keywords LIKE ?)"
            params.extend([f"%{search}%"] * 3)
        if status:
            query += " AND p.status=?"
            params.append(status)
        
        count_row = conn.execute(query.replace("p.*, c.name", "COUNT(*)"), params).fetchone()
        total = count_row[0] if count_row else 0
        
        query += " ORDER BY p.year DESC, p.created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page-1) * per_page])
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return JSONResponse({
            "papers": [dict(r) for r in rows],
            "total": total, "page": page, "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        })
    
    @app.post("/api/papers")
    async def api_paper_create(request: Request):
        require_auth(request)
        body = await request.json()
        conn = get_db()
        conn.execute("""INSERT INTO papers (title, title_zh, authors, year, venue, category_id, 
                       abstract, abstract_zh, keywords, doi, pdf_url, source, source_id, status)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (body.get("title",""), body.get("title_zh"), body.get("authors"), body.get("year"),
             body.get("venue"), body.get("category_id"), body.get("abstract"), body.get("abstract_zh"),
             body.get("keywords"), body.get("doi"), body.get("pdf_url"), body.get("source","manual"),
             body.get("source_id"), body.get("status","pending")))
        conn.commit()
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return JSONResponse({"id": pid, "success": True})
    
    # --- Parameterized routes LAST ---
    @app.get("/api/papers/{paper_id}")
    async def api_paper_detail(request: Request, paper_id: int):
        require_auth(request)
        conn = get_db()
        paper = conn.execute("SELECT p.*, c.name as category_name, c.color as category_color FROM papers p LEFT JOIN paper_categories c ON p.category_id=c.id WHERE p.id=?", (paper_id,)).fetchone()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在")
        notes = conn.execute("SELECT * FROM paper_notes WHERE paper_id=? ORDER BY created_at DESC", (paper_id,)).fetchall()
        related = conn.execute("""
            SELECT p.id, p.title, p.year, r.relation_type FROM paper_relations r 
            JOIN papers p ON r.target_paper_id=p.id WHERE r.source_paper_id=?
            UNION
            SELECT p.id, p.title, p.year, r.relation_type FROM paper_relations r 
            JOIN papers p ON r.source_paper_id=p.id WHERE r.target_paper_id=?
        """, (paper_id, paper_id)).fetchall()
        conn.close()
        result = dict(paper)
        result['notes'] = [dict(n) for n in notes]
        result['related'] = [dict(r) for r in related]
        return JSONResponse(result)
    
    @app.put("/api/papers/{paper_id}")
    async def api_paper_update(request: Request, paper_id: int):
        require_auth(request)
        body = await request.json()
        conn = get_db()
        conn.execute("""UPDATE papers SET title=?, title_zh=?, authors=?, year=?, venue=?,
                       category_id=?, abstract=?, abstract_zh=?, keywords=?, doi=?, pdf_url=?,
                       pdf_path=?, downloaded=?, summary=?, summary_zh=?, llm_summary=?, llm_review=?,
                       updated_at=CURRENT_TIMESTAMP WHERE id=?""",
            (body.get("title",""), body.get("title_zh"), body.get("authors"), body.get("year"),
             body.get("venue"), body.get("category_id"), body.get("abstract"), body.get("abstract_zh"),
             body.get("keywords"), body.get("doi"), body.get("pdf_url"), body.get("pdf_path"),
             body.get("downloaded", 0), body.get("summary"), body.get("summary_zh"),
             body.get("llm_summary"), body.get("llm_review"), paper_id))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True})
    
    @app.delete("/api/papers/{paper_id}")
    async def api_paper_delete(request: Request, paper_id: int):
        require_auth(request)
        conn = get_db()
        row = conn.execute("SELECT pdf_path FROM papers WHERE id=?", (paper_id,)).fetchone()
        if row and row["pdf_path"]:
            pdf_path = Path(row["pdf_path"])
            if pdf_path.exists():
                pdf_path.unlink()
        conn.execute("DELETE FROM paper_notes WHERE paper_id=?", (paper_id,))
        conn.execute("DELETE FROM paper_relations WHERE source_paper_id=? OR target_paper_id=?", (paper_id, paper_id))
        conn.execute("DELETE FROM papers WHERE id=?", (paper_id,))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True})
    
    # --- Download ---
    @app.post("/api/papers/{paper_id}/download")
    async def api_paper_download(request: Request, paper_id: int):
        require_auth(request)
        body = await request.json()
        pdf_url = body.get("pdf_url", "")
        
        conn = get_db()
        paper = conn.execute("SELECT * FROM papers WHERE id=?", (paper_id,)).fetchone()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在")
        
        if not pdf_url and not paper["pdf_url"]:
            raise HTTPException(status_code=400, detail="无 PDF 链接")
        
        import urllib.request as _req
        try:
            url = pdf_url or paper["pdf_url"]
            filename = f"paper_{paper_id}_{hashlib.md5(url.encode()).hexdigest()[:8]}.pdf"
            filepath = PAPER_DIR / filename
            
            req = _req.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with _req.urlopen(req, timeout=60) as resp:
                data = resp.read()
                with open(filepath, "wb") as f:
                    f.write(data)
            
            file_size = len(data)
            conn.execute("UPDATE papers SET pdf_path=?, pdf_size=?, downloaded=1, status='downloaded', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        (str(filepath), file_size, paper_id))
            conn.commit()
            conn.close()
            return JSONResponse({"success": True, "filename": filename, "size": file_size, "url": f"/static/papers/{filename}"})
        except Exception as e:
            conn.close()
            return JSONResponse({"success": False, "error": str(e)}, status_code=502)
    
    @app.get("/api/papers/{paper_id}/pdf")
    async def api_paper_pdf(request: Request, paper_id: int):
        require_auth(request)
        conn = get_db()
        paper = conn.execute("SELECT pdf_path FROM papers WHERE id=? AND downloaded=1", (paper_id,)).fetchone()
        conn.close()
        if not paper or not paper["pdf_path"]:
            raise HTTPException(status_code=404, detail="PDF 未下载")
        return FileResponse(paper["pdf_path"], media_type="application/pdf")
    
    # --- LLM Summary ---
    @app.post("/api/papers/{paper_id}/summarize")
    async def api_paper_summarize(request: Request, paper_id: int):
        require_auth(request)
        body = await request.json()
        language = body.get("language", "zh")
        
        conn = get_db()
        paper = conn.execute("SELECT * FROM papers WHERE id=?", (paper_id,)).fetchone()
        if not paper:
            raise HTTPException(status_code=404, detail="论文不存在")
        
        prompt = _build_summary_prompt(paper, language)
        summary = await _call_llm(prompt)
        
        if language == "zh":
            conn.execute("UPDATE papers SET llm_summary=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (summary, paper_id))
        else:
            conn.execute("UPDATE papers SET summary=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (summary, paper_id))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True, "summary": summary})
    
    @app.post("/api/papers/review/{category_id}")
    async def api_generate_review(request: Request, category_id: int):
        require_auth(request)
        body = await request.json()
        language = body.get("language", "zh")
        period_start = body.get("period_start", "2020")
        period_end = body.get("period_end", "2025")
        
        conn = get_db()
        category = conn.execute("SELECT * FROM paper_categories WHERE id=?", (category_id,)).fetchone()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        
        papers = conn.execute(
            "SELECT * FROM papers WHERE category_id=? AND year BETWEEN ? AND ? ORDER BY year DESC",
            (category_id, period_start, period_end)
        ).fetchall()
        
        if not papers:
            return JSONResponse({"error": "该分类下暂无论文"}, status_code=400)
        
        paper_summaries = []
        for p in papers:
            summary = p["llm_summary"] or p["summary"] or (p["abstract"][:200] if p["abstract"] else "")
            paper_summaries.append(f"[{p['year']}] {p['title']} - {summary[:100]}")
        
        prompt = _build_review_prompt(category, paper_summaries, language, period_start, period_end)
        review = await _call_llm(prompt)
        
        conn.execute("""INSERT INTO literature_reviews (category_id, title, content, paper_count, period_start, period_end)
                       VALUES (?,?,?,?,?,?)""",
            (category_id, f"{category['name_zh']} 文献综述 ({period_start}-{period_end})", review, len(papers), period_start, period_end))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True, "review": review, "paper_count": len(papers)})
    
    # --- Batch Import ---
    @app.post("/api/papers/import")
    async def api_papers_import(request: Request):
        require_auth(request)
        body = await request.json()
        papers = body.get("papers", [])
        category_id = body.get("category_id")
        
        conn = get_db()
        imported = 0
        for p in papers:
            try:
                conn.execute("""INSERT OR IGNORE INTO papers 
                    (title, title_zh, authors, year, venue, category_id, abstract, keywords, doi, pdf_url, source, source_id, status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (p.get("title",""), p.get("title_zh"), p.get("authors"), p.get("year"),
                     p.get("venue"), category_id or p.get("category_id"), p.get("abstract"),
                     p.get("keywords"), p.get("doi"), p.get("pdf_url"), p.get("source","import"),
                     p.get("source_id"), "pending"))
                imported += 1
            except:
                pass
        conn.commit()
        conn.close()
        return JSONResponse({"success": True, "imported": imported, "total": len(papers)})


def _build_summary_prompt(paper, language="zh"):
    title = paper["title"]
    abstract = paper["abstract"] or ""
    keywords = paper["keywords"] or ""
    authors = paper["authors"] or ""
    year = paper["year"] or ""
    venue = paper["venue"] or ""
    
    if language == "zh":
        return f"""请为以下密码学论文生成详细的中文总结：

标题：{title}
作者：{authors}
年份：{year}
期刊/会议：{venue}
关键词：{keywords}
摘要：{abstract}

请生成包含以下部分的总结：
1. 研究背景与动机
2. 核心贡献（3-5个要点）
3. 技术方法
4. 安全性分析
5. 性能评估
6. 局限性
7. 未来方向

请用中文回答，保持专业性和准确性。"""
    else:
        return f"""Generate a detailed summary for this cryptography paper:

Title: {title}
Authors: {authors}
Year: {year}
Venue: {venue}
Keywords: {keywords}
Abstract: {abstract}

Cover: Background, Contributions, Technical Approach, Security Analysis, Performance, Limitations, Future Directions.

Respond in English."""


def _build_review_prompt(category, paper_summaries, language, period_start, period_end):
    cat_name = category["name_zh"] or category["name"]
    cat_desc = category["description"] or ""
    papers_text = "\n".join(paper_summaries[:30])
    
    if language == "zh":
        return f"""请为"{cat_name}"研究方向生成详细的文献综述。

研究方向：{cat_name}
描述：{cat_desc}
时间范围：{period_start}-{period_end}
论文数量：{len(paper_summaries)}篇

部分论文摘要：
{papers_text}

请生成包含以下部分的综述：
1. 研究背景与意义
2. 发展历程
3. 主要技术路线分类
4. 代表性工作详解
5. 性能对比
6. 开放问题与挑战
7. 未来发展趋势
8. 参考文献

用中文回答，学术严谨，不少于2000字。"""
    else:
        return f"""Generate a literature review for "{cat_name}".

Direction: {cat_name}
Description: {cat_desc}
Period: {period_start}-{period_end}
Papers: {len(paper_summaries)}

Paper summaries:
{papers_text}

Cover: Background, Evolution, Technical Approaches, Representative Works, Comparison, Open Problems, Trends, References.

Respond in English, minimum 2000 words."""


async def _call_llm(prompt: str) -> str:
    """Call Agnes AI API for LLM generation"""
    import urllib.request as _req
    import json as _json
    
    api_key = "sk-gSc...oZ8R"
    
    try:
        data = _json.dumps({
            "model": "agnes-2.0-flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
            "temperature": 0.7
        }).encode()
        
        req = _req.Request("https://apihub.agnes-ai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=data)
        
        with _req.urlopen(req, timeout=120) as resp:
            result = _json.loads(resp.read().decode())
            return result.get("choices", [{}])[0].get("message", {}).get("content", "生成失败")
    except Exception as e:
        return f"LLM 调用失败: {str(e)}"
