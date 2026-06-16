import json, urllib.request, sqlite3, time

API_KEY = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"
conn = sqlite3.connect("/root/portal/data/portal.db")

def find_url(obj, depth=0):
    if depth > 6: return None
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage", "output", "video", "platform"]):
        return obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("http"): return v
            r = find_url(v, depth+1)
            if r: return r
    if isinstance(obj, list):
        for item in obj:
            r = find_url(item, depth+1)
            if r: return r
    return None

print("Starting video polling loop...")
round_num = 0
while True:
    round_num += 1
    scenes = conn.execute("SELECT id, scene_number, title, video_task_id, status FROM manga_scenes WHERE project_id=2 AND status='video_processing'").fetchall()
    
    if not scenes:
        print("All videos completed!")
        break
    
    print("\n--- Round %d: %d scenes pending ---" % (round_num, len(scenes)))
    all_done = True
    
    for sid, snum, title, tid, st in scenes:
        try:
            req = urllib.request.Request(BASE + "/videos/" + tid,
                headers={"Authorization": "Bearer " + API_KEY})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            
            status = result.get("status", "unknown")
            url = find_url(result)
            
            if url:
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (url, sid))
                conn.commit()
                print("  ✓ Scene %d '%s': COMPLETED" % (snum, title))
            else:
                print("  ⏳ Scene %d '%s': %s" % (snum, title, status))
                if status not in ("failed", "error"):
                    all_done = False
                    
        except Exception as e:
            print("  ✗ Scene %d error: %s" % (snum, e))
            all_done = False
        
        time.sleep(2)
    
    if all_done:
        break
    
    print("Waiting 30 seconds before next check...")
    time.sleep(30)

# Final
print("\n=== FINAL STATUS ===")
rows = conn.execute("SELECT scene_number, title, status, CASE WHEN video_url IS NOT NULL THEN 'YES' ELSE 'NO' END FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()
for r in rows:
    print("  Scene %d '%s': %s (video: %s)" % (r[0], r[1], r[2], r[3]))
conn.close()
