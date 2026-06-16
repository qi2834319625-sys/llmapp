"""
Music API module - iTunes Search (free, no key needed)
"""
import json, urllib.request, urllib.parse
from fastapi import Request
from fastapi.responses import JSONResponse

ITUNES_SEARCH_API = "https://itunes.apple.com/search"

async def search_music(request: Request, keyword: str = "轻音乐", num: int = 10):
    """Search songs using iTunes Search API (free, no auth)"""
    try:
        url = f"{ITUNES_SEARCH_API}?term={urllib.parse.quote(keyword)}&media=music&entity=song&limit={num}"
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
                    "artwork": s.get("artworkUrl100", ""),
                })
            return JSONResponse({"songs": songs})
    except Exception as e:
        print(f"Music search error: {e}")
    return JSONResponse({"songs": [], "error": "Search failed"})

async def get_music_url(request: Request, mid: str = ""):
    """Get song preview URL from iTunes"""
    if not mid:
        return JSONResponse({"url": ""})
    try:
        url = f"https://itunes.apple.com/lookup?id={mid}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            if results:
                preview_url = results[0].get("previewUrl", "")
                return JSONResponse({"url": preview_url})
    except Exception as e:
        print(f"Music URL error: {e}")
    return JSONResponse({"url": ""})
