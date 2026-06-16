"""
Manga Pipeline Step 4: Generate videos from images
"""
import json, urllib.request, time, sqlite3, os

k = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"
H = {"Authorization": "Bearer " + k, "Content-Type": "application/json"}

def call(endpoint, data, timeout=180):
    req = urllib.request.Request(BASE + endpoint, headers=H, data=json.dumps(data).encode())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def find_url(obj, depth=0):
    if depth > 6: return None
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","platform","video","mp4"]):
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

# Load images
with open("/tmp/scene_images.json") as f:
    scenes = json.load(f)

print("=== Step 4: Generate Videos ===")

video_results = []
for scene in scenes:
    snum = scene["scene_number"]
    title = scene["title"]
    vprompt = scene.get("video_prompt", title)
    
    print("\n  Scene %d: %s..." % (snum, title))
    
    try:
        result = call("/videos", {
            "model": "agnes-video-v2.0",
            "prompt": "anime manga style, smooth camera movement, cinematic, " + vprompt[:400],
            "num_frames": 81,
            "frame_rate": 24
        }, timeout=180)
        
        vid_url = find_url(result)
        task_id = result.get("task_id") or result.get("id")
        
        if vid_url:
            print("    Direct video: %s" % vid_url[:60])
            status = "done"
        elif task_id:
            print("    Task: %s" % str(task_id)[:30])
            status = "processing"
            vid_url = None
        else:
            print("    FAILED: %s" % str(result)[:100])
            status = "failed"
            vid_url = None
            task_id = None
            
    except Exception as e:
        print("    Error: %s" % e)
        status = "failed"
        vid_url = None
        task_id = None
    
    video_results.append({
        "scene_number": snum,
        "title": title,
        "image_url": scene["image_url"],
        "video_url": vid_url,
        "task_id": str(task_id) if task_id else None,
        "status": status,
        "dialogue": scene.get("dialogue", "")
    })
    
    time.sleep(5)

# Save to DB
conn = sqlite3.connect("/root/portal/data/portal.db")
for v in video_results:
    conn.execute("UPDATE manga_scenes SET video_url=?, video_task_id=?, status=? WHERE project_id=2 AND scene_number=?",
        (v["video_url"], v["task_id"], v["status"], v["scene_number"]))
conn.commit()
conn.close()

with open("/tmp/scene_videos.json", "w") as f:
    json.dump(video_results, f, ensure_ascii=False, indent=2)

done = len([v for v in video_results if v["status"] == "done"])
proc = len([v for v in video_results if v["status"] == "processing"])
print("\n=== Videos: %d done, %d processing, %d failed ===" % (done, proc, len(video_results)-done-proc))
