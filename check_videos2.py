import json, urllib.request, time, sqlite3, os

# Read API key from environment or file
AGNES_API_KEY = os.environ.get("AGNES_API_KEY", "")
if not AGNES_API_KEY:
    try:
        with open("/root/portal/.agnes_key", "r") as f:
            AGNES_API_KEY = f.read().strip()
    except:
        pass

AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

print("API Key: %s..." % AGNES_API_KEY[:10] if AGNES_API_KEY else "NOT SET")

conn = sqlite3.connect("/root/portal/data/portal.db")
scenes = conn.execute("""
    SELECT ms.id, ms.scene_number, ms.title, ms.video_task_id, ms.status
    FROM manga_scenes ms
    JOIN manga_projects mp ON ms.project_id = mp.id
    WHERE mp.id = 2 AND ms.video_task_id IS NOT NULL
    ORDER BY ms.scene_number
""").fetchall()

print("Checking %d scenes..." % len(scenes))

for scene_id, scene_num, title, task_id, status in scenes:
    print("\nScene %d '%s' [%s]" % (scene_num, title, status))
    
    try:
        req = urllib.request.Request(
            AGNES_BASE_URL + "/videos/" + task_id,
            headers={"Authorization": "Bearer " + AGNES_API_KEY}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            
            new_status = result.get("status", "unknown")
            print("  API status: %s" % new_status)
            print("  Response: %s" % json.dumps(result, ensure_ascii=False)[:500])
            
            # Deep search for URL
            vid_url = None
            
            def find_url(obj, depth=0):
                if depth > 5:
                    return None
                if isinstance(obj, str) and obj.startswith("http"):
                    return obj
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, str) and v.startswith("http"):
                            print("  Found URL in key '%s': %s" % (k, v[:80]))
                            return v
                        r = find_url(v, depth+1)
                        if r:
                            return r
                if isinstance(obj, list):
                    for item in obj:
                        r = find_url(item, depth+1)
                        if r:
                            return r
                return None
            
            vid_url = find_url(result)
            print("  Video URL: %s" % (vid_url[:80] + "..." if vid_url else "NOT FOUND"))
            
            if vid_url:
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (vid_url, scene_id))
                conn.commit()
                print("  -> UPDATED!")
            else:
                conn.execute("UPDATE manga_scenes SET status=? WHERE id=?", (new_status, scene_id))
                conn.commit()
                
    except Exception as e:
        print("  Error: %s" % e)
    
    time.sleep(2)

# Final
print("\n=== FINAL STATUS ===")
scenes = conn.execute("SELECT scene_number, title, status, CASE WHEN video_url IS NOT NULL THEN 'YES' ELSE 'NO' END FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()
for s in scenes:
    print("  Scene %d '%s': %s (video: %s)" % (s[0], s[1], s[2], s[3]))
conn.close()
