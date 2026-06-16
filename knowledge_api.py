"""
Knowledge Base API routes - LLM Q&A, knowledge retrieval, daily updates.
"""
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response

def register_knowledge_routes(app):
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

    # ========== Knowledge Base Page ==========
    @app.get("/knowledge", response_class=HTMLResponse)
    async def knowledge_page(request: Request):
        user = require_auth(request)
        return render("knowledge.html", request=request, user=user)

    # ========== Knowledge Categories ==========
    @app.get("/api/knowledge/categories")
    async def api_knowledge_categories(request: Request):
        require_auth(request)
        conn = get_db()
        rows = conn.execute("SELECT * FROM knowledge_categories WHERE is_active=1 ORDER BY sort_order").fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])

    # ========== Knowledge Search ==========
    @app.get("/api/knowledge/search")
    async def api_knowledge_search(request: Request, q: str = "", category_id: int = None, limit: int = 20):
        require_auth(request)
        uid = get_user_id(request)
        from database import search_knowledge, log_knowledge_search
        results = search_knowledge(q, category_id, limit)
        log_knowledge_search(uid, q, len(results))
        return JSONResponse({"query": q, "results": results, "count": len(results)})

    # ========== Knowledge Items CRUD ==========
    @app.get("/api/knowledge/items")
    async def api_knowledge_items(request: Request, category_id: int = None, limit: int = 50):
        require_auth(request)
        conn = get_db()
        if category_id:
            rows = conn.execute("SELECT k.*,c.name_zh as category_name FROM knowledge_items k LEFT JOIN knowledge_categories c ON k.category_id=c.id WHERE k.category_id=? ORDER BY k.created_at DESC LIMIT ?", (category_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT k.*,c.name_zh as category_name FROM knowledge_items k LEFT JOIN knowledge_categories c ON k.category_id=c.id ORDER BY k.created_at DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return JSONResponse([dict(r) for r in rows])

    @app.post("/api/knowledge/items")
    async def api_knowledge_add(request: Request):
        require_auth(request)
        body = await request.json()
        from database import add_knowledge_item
        add_knowledge_item(
            body.get("category_id"), body.get("title", ""), body.get("content", ""),
            body.get("summary"), body.get("source", "manual"), body.get("source_url"),
            body.get("tags"), body.get("importance", 5)
        )
        return JSONResponse({"success": True})

    @app.delete("/api/knowledge/items/{item_id}")
    async def api_knowledge_delete(request: Request, item_id: int):
        require_auth(request)
        conn = get_db()
        conn.execute("DELETE FROM knowledge_items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()
        return JSONResponse({"success": True})

    # ========== Daily Updates ==========
    @app.get("/api/knowledge/daily")
    async def api_knowledge_daily(request: Request, date: str = None, limit: int = 50):
        require_auth(request)
        from database import get_daily_knowledge
        items = get_daily_knowledge(date, limit)
        return JSONResponse({"date": date or __import__('datetime').date.today().isoformat(), "items": items, "count": len(items)})

    @app.post("/api/knowledge/daily/generate")
    async def api_generate_daily(request: Request):
        """Generate daily knowledge updates using LLM"""
        require_auth(request)
        body = await request.json()
        category_id = body.get("category_id", 7)  # Default to news
        date = body.get("date", __import__('datetime').date.today().isoformat())
        
        # Generate sample daily updates (in production, this would call LLM API)
        from database import add_daily_update
        sample_updates = [
            {"title": "AI前沿：大模型最新进展", "content": "今日AI领域重要进展包括多模态大模型、Agent框架、RAG技术等方面的突破...", "category_id": 1},
            {"title": "密码学：后量子密码标准化", "content": "NIST后量子密码标准化进程更新，CRYSTALS-Kyber和CRYSTALS-Dilithium进入最终轮...", "category_id": 2},
            {"title": "科技热点：GPT-5发布预告", "content": "OpenAI预告下一代大模型将具备更强的推理能力和多模态理解...", "category_id": 7},
        ]
        added = 0
        for u in sample_updates:
            add_daily_update(u["category_id"], u["title"], u["content"], source="AI生成", date=date)
            added += 1
        
        return JSONResponse({"success": True, "generated": added})

    # ========== LLM Chat ==========
    @app.post("/api/knowledge/chat")
    async def api_knowledge_chat(request: Request):
        require_auth(request)
        uid = get_user_id(request)
        body = await request.json()
        message = body.get("message", "")
        
        from database import add_chat_message, get_chat_history, search_knowledge
        
        # Save user message
        add_chat_message(uid, "user", message)
        
        # Search knowledge base for relevant context
        relevant = search_knowledge(message, limit=5)
        
        # Build context from knowledge base
        context = ""
        if relevant:
            context = "\n\n相关知识:\n"
            for r in relevant[:3]:
                context += f"- {r['title']}: {r.get('summary', r['content'][:100])}\n"
        
        # Call Agnes AI API for response
        try:
            import urllib.request as _req
            import json as _json
            api_key = "sk-gSc...oZ8R"
            prompt = f"你是一个知识助手。基于以下知识库内容回答用户的问题。{context}\n\n用户问题: {message}\n\n请用中文回答，保持专业和简洁。"
            data = _json.dumps({
                "model": "agnes-2.0-flash",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000, "temperature": 0.7
            }).encode()
            req = _req.Request("https://apihub.agnes-ai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, data=data)
            with _req.urlopen(req, timeout=60) as resp:
                result = _json.loads(resp.read().decode())
                answer = result.get("choices", [{}])[0].get("message", {}).get("content", "抱歉，我无法回答这个问题。")
        except Exception as e:
            answer = f"AI 服务暂时不可用。基于知识库搜索到 {len(relevant)} 条相关内容。请稍后再试。"
        
        # Save assistant response
        add_chat_message(uid, "assistant", answer)
        
        # Get updated history
        history = get_chat_history(uid, limit=20)
        
        return JSONResponse({"answer": answer, "history": history, "relevant": relevant})

    @app.get("/api/knowledge/chat/history")
    async def api_chat_history(request: Request):
        require_auth(request)
        uid = get_user_id(request)
        from database import get_chat_history
        return JSONResponse(get_chat_history(uid))

    # ========== Global Search ==========
    @app.get("/api/search")
    async def api_global_search(request: Request, q: str = "", limit: int = 10):
        """Global search across all modules"""
        require_auth(request)
        if not q or len(q) < 2:
            return JSONResponse({"query": q, "results": {}})
        
        conn = get_db()
        results = {}
        
        # Search papers
        papers = conn.execute("SELECT id,title,year,'paper' as type FROM papers WHERE title LIKE ? OR abstract LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if papers: results["papers"] = [dict(r) for r in papers]
        
        # Search knowledge
        knowledge = conn.execute("SELECT id,title,summary,'knowledge' as type FROM knowledge_items WHERE title LIKE ? OR content LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if knowledge: results["knowledge"] = [dict(r) for r in knowledge]
        
        # Search crypto papers
        crypto = conn.execute("SELECT id,title,'crypto' as type FROM crypto_papers WHERE title LIKE ? OR abstract LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if crypto: results["crypto"] = [dict(r) for r in crypto]
        
        # Search recruitment questions
        recruit = conn.execute("SELECT id,title,'recruitment' as type FROM recruitment_questions WHERE title LIKE ? OR content LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if recruit: results["recruitment"] = [dict(r) for r in recruit]
        
        # Search recipes
        recipes = conn.execute("SELECT id,title,'cooking' as type FROM recipes WHERE title LIKE ? OR content LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if recipes: results["cooking"] = [dict(r) for r in recipes]
        
        # Search study abroad
        study = conn.execute("SELECT id,title,'study' as type FROM study_abroad WHERE title LIKE ? OR content LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if study: results["study_abroad"] = [dict(r) for r in study]
        
        # Search CET words
        cet = conn.execute("SELECT id,word as title,'cet' as type FROM cet_exam WHERE word LIKE ? OR definition LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if cet: results["cet"] = [dict(r) for r in cet]
        
        # Search GNN entities
        gnn = conn.execute("SELECT id,name as title,'gnn' as type FROM gnn_entities WHERE name LIKE ? OR description LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if gnn: results["gnn"] = [dict(r) for r in gnn]
        
        # Search fashion items
        fashion = conn.execute("SELECT id,name as title,'fashion' as type FROM fashion_items WHERE name LIKE ? OR description LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if fashion: results["fashion"] = [dict(r) for r in fashion]
        
        # Search makeup tips
        makeup = conn.execute("SELECT id,title,'makeup' as type FROM makeup_tips WHERE title LIKE ? OR content LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if makeup: results["makeup"] = [dict(r) for r in makeup]
        
        # Search civil exam
        civil = conn.execute("SELECT id,title,'civil' as type FROM civil_exam WHERE title LIKE ? OR content LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if civil: results["civil_exam"] = [dict(r) for r in civil]
        
        # Search YouTube resources
        yt = conn.execute("SELECT id,title,'youtube' as type FROM youtube_resources WHERE title LIKE ? OR description LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if yt: results["youtube"] = [dict(r) for r in yt]
        
        # Search GitHub repos
        gh = conn.execute("SELECT id,name as title,'github' as type FROM github_repos WHERE name LIKE ? OR description LIKE ? LIMIT ?", ("%"+q+"%","%"+q+"%",limit)).fetchall()
        if gh: results["github"] = [dict(r) for r in gh]
        
        conn.close()
        total = sum(len(v) for v in results.values())
        import json as _json
        return Response(content=_json.dumps({"query": q, "results": results, "total": total}, ensure_ascii=False), media_type="application/json")
