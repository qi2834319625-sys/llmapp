"""Submit all 8 video tasks with correct task IDs, then poll"""
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

# Load scene data
with open("/tmp/scene_images.json") as f:
    scenes = json.load(f)

conn = sqlite3.connect("/root/portal/data/portal.db")

# Clear and re-insert scenes for project 2
conn.execute("DELETE FROM manga_scenes WHERE project_id=2")

print("=== Submitting %d video tasks ===" % len(scenes))

for s in scenes:
    snum = s["scene_number"]
    title = s["title"]
    vp = s.get("video_prompt", title)
    img_url = s.get("image_url", "")
    dialogue = s.get("dialogue", "")
    camera = s.get("camera", "")
    mood = s.get("mood", "")
    
    print("Scene %d: %s..." % (snum, title))
    
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
        
        print("  -> %s [%s]" % (str(task_id)[:40], status))
        
    except Exception as e:
        print("  -> ERROR: %s" % e)
        task_id = None
        vid_url = None
        status = "failed"
    
    # Save to DB
    conn.execute("""INSERT INTO manga_scenes 
        (project_id, scene_number, title, description, characters, dialogue, image_prompt, image_url, video_url, video_task_id, status)
        VALUES (2, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (snum, title, "%s %s" % (camera, mood), "", dialogue, "", img_url, vid_url, task_id, status))
    conn.commit()
    
    time.sleep(5)

print("\n=== All tasks submitted. Polling for completion ===")

# Poll for completion
for round_num in range(30):
    rows = conn.execute("SELECT id, scene_number, title, video_task_id FROM manga_scenes WHERE project_id=2 AND status='processing' AND video_task_id IS NOT NULL").fetchall()
    if not rows:
        print("All done!")
        break
    
    print("\nRound %d: %d pending..." % (round_num + 1, len(rows)))
    
    for sid, snum, title, tid in rows:
        try:
            result = call("/videos/" + tid, {}, timeout=30)
            status = result.get("status", "processing")
            vid_url = find_url(result)
            
            if vid_url:
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (vid_url, sid))
                conn.commit()
                print("  Scene %d: COMPLETED" % snum)
            elif status in ("completed", "success", "done"):
                print("  Scene %d: %s (no URL yet)" % (snum, status))
            else:
                print("  Scene %d: %s" % (snum, status))
        except Exception as e:
            print("  Scene %d: poll error %s" % (snum, e))
        time.sleep(2)
    
    if rows:
        time.sleep(60)

# Final
print("\n=== FINAL STATUS ===")
rows = conn.execute("SELECT scene_number, title, status, video_url FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()
done = 0
for r in rows:
    has = "YES" if r[3] else "NO"
    if r[2] == "done": done += 1
    print("Scene %d %s: %s video=%s" % (r[0], r[1], r[2], has))
print("\n%d/%d completed" % (done, len(rows)))
conn.close()
