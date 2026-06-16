"""Submit video tasks for project 2 and poll for completion"""
import json, urllib.request, time, sqlite3

k = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"
H = {"Authorization": "Bearer " + k, "Content-Type": "application/json"}

def call(endpoint, data, timeout=180):
    req = urllib.request.Request(BASE + endpoint, headers=H, data=json.dumps(data).encode())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def find_url(obj, depth=0):
    if depth > 6: return None
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","video","mp4","platform"]):
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

# Load scene images
with open("/tmp/scene_images.json") as f:
    scenes = json.load(f)

conn = sqlite3.connect("/root/portal/data/portal.db")

# First, clear old scenes for project 2 and insert new ones
conn.execute("DELETE FROM manga_scenes WHERE project_id=2")

print("=== Submitting %d video tasks ===" % len(scenes))

tasks = []
for s in scenes:
    snum = s["scene_number"]
    title = s["title"]
    vp = s.get("video_prompt", title)
    img_url = s.get("image_url", "")
    dialogue = s.get("dialogue", "")
    camera = s.get("camera", "")
    mood = s.get("mood", "")
    
    print("\nScene %d: %s" % (snum, title))
    
    # Submit video task
    try:
        result = call("/videos", {
            "model": "agnes-video-v2.0",
            "prompt": "anime manga style, smooth camera movement, cinematic, " + vp[:400],
            "num_frames": 81,
            "frame_rate": 24
        }, timeout=180)
        
        task_id = result.get("task_id") or result.get("id")
        vid_url = find_url(result)
        status = "done" if vid_url else "processing"
        
        print("  task=%s status=%s" % (str(task_id)[:30] if task_id else "none", status))
        
    except Exception as e:
        print("  ERROR: %s" % e)
        task_id = None
        vid_url = None
        status = "failed"
    
    # Insert into DB
    conn.execute("""INSERT INTO manga_scenes 
        (project_id, scene_number, title, description, characters, dialogue, image_prompt, image_url, video_url, video_task_id, status)
        VALUES (2, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (snum, title, "%s %s" % (camera, mood), "", dialogue, "", img_url, vid_url, str(task_id) if task_id else None, status))
    conn.commit()
    
    tasks.append({"scene_number": snum, "title": title, "task_id": task_id, "status": status})
    time.sleep(3)

# Poll for completion
print("\n=== Polling for completion ===")
for round_num in range(20):
    pending = [t for t in tasks if t["status"] == "processing" and t.get("task_id")]
    if not pending:
        break
    print("\nRound %d: %d pending..." % (round_num + 1, len(pending)))
    
    for t in pending:
        try:
            result = call("/videos/" + t["task_id"], {}, timeout=30)
            status = result.get("status", "processing")
            vid_url = find_url(result)
            
            if vid_url:
                t["status"] = "done"
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE project_id=2 AND scene_number=?",
                    (vid_url, t["scene_number"]))
                conn.commit()
                print("  Scene %d: COMPLETED" % t["scene_number"])
            elif status in ("completed", "success", "done"):
                print("  Scene %d: %s (no URL)" % (t["scene_number"], status))
            else:
                print("  Scene %d: %s" % (t["scene_number"], status))
        except urllib.error.HTTPError as e:
            print("  Scene %d: HTTP %d" % (t["scene_number"], e.code))
        except Exception as e:
            print("  Scene %d: %s" % (t["scene_number"], e))
        time.sleep(2)
    
    if pending:
        time.sleep(30)

# Final summary
print("\n=== FINAL ===")
rows = conn.execute("SELECT scene_number, title, status, video_url FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()
done_count = 0
for r in rows:
    has_vid = "YES" if r[3] else "NO"
    if r[2] == "done": done_count += 1
    print("  Scene %d %s: %s video=%s" % (r[0], r[1], r[2], has_vid))

print("\nTotal: %d/%d videos completed" % (done_count, len(rows)))
conn.close()
