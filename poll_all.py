"""Poll existing video tasks with full task IDs"""
import json, urllib.request, time, sqlite3

k = open("/root/portal/.agnes_key").read().strip()
conn = sqlite3.connect("/root/portal/data/portal.db")

# Get all scenes with video tasks
rows = conn.execute("SELECT id, scene_number, title, video_task_id, image_url, dialogue FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()

print("Polling %d scenes..." % len(rows))

for sid, snum, title, tid, img_url, dialogue in rows:
    if not tid:
        print("  Scene %d: no task_id, skipping" % snum)
        continue
    
    print("  Scene %d: polling %s..." % (snum, tid[:30]))
    
    try:
        req = urllib.request.Request("https://apihub.agnes-ai.com/v1/videos/" + tid,
            headers={"Authorization": "Bearer " + k})
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        
        status = result.get("status", "unknown")
        progress = result.get("progress", 0)
        
        # Find video URL in response
        vid_url = None
        def find(obj, d=0):
            if d > 6: return None
            if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage", "output", "video", "mp4"]):
                return obj
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str) and v.startswith("http"): return v
                    r = find(v, d+1)
                    if r: return r
            if isinstance(obj, list):
                for item in obj:
                    r = find(item, d+1)
                    if r: return r
            return None
        
        vid_url = find(result)
        
        print("    Status: %s, Progress: %s, URL: %s" % (status, progress, vid_url[:60]+"..." if vid_url else "none"))
        
        if vid_url:
            conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (vid_url, sid))
            conn.commit()
        else:
            conn.execute("UPDATE manga_scenes SET status=? WHERE id=?", (status, sid))
            conn.commit()
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("    404 - task may not exist")
        else:
            print("    HTTP %d" % e.code)
    except Exception as e:
        print("    Error: %s" % e)
    
    time.sleep(2)

# Summary
print("\n=== Summary ===")
rows = conn.execute("SELECT scene_number, title, status, video_url FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()
for r in rows:
    print("  Scene %d %s: %s video=%s" % (r[0], r[1], r[2], "YES" if r[3] else "NO"))
conn.close()
