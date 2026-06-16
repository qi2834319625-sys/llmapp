"""Quick submit all 8 video tasks"""
import json, urllib.request, time, sqlite3

k = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"
H = {"Authorization": "Bearer " + k, "Content-Type": "application/json"}

def submit_video(prompt):
    data = json.dumps({"model":"agnes-video-v2.0","prompt":prompt[:400],"num_frames":81,"frame_rate":24}).encode()
    req = urllib.request.Request(BASE+"/videos", headers=H, data=data)
    resp = urllib.request.urlopen(req, timeout=180)
    r = json.loads(resp.read().decode())
    return r.get("task_id") or r.get("id")

with open("/tmp/scene_images.json") as f:
    scenes = json.load(f)

conn = sqlite3.connect("/root/portal/data/portal.db")
conn.execute("DELETE FROM manga_scenes WHERE project_id=2")

print("Submitting %d videos..." % len(scenes))
tasks = []
for s in scenes:
    snum = s["scene_number"]
    title = s["title"]
    vp = s.get("video_prompt", title)
    prompt = "anime manga style, smooth camera movement, cinematic, " + vp
    
    print("Scene %d: %s..." % (snum, title))
    tid = submit_video(prompt)
    print("  -> %s" % str(tid)[:40])
    
    conn.execute("INSERT INTO manga_scenes (project_id,scene_number,title,description,dialogue,image_url,video_task_id,status) VALUES (2,?,?,?,?,?,?,?)",
        (snum, title, s.get("camera","")+" "+s.get("mood",""), s.get("dialogue",""), s.get("image_url",""), str(tid), "processing"))
    conn.commit()
    tasks.append({"scene": snum, "task_id": str(tid)})
    time.sleep(3)

print("\nAll submitted!")
with open("/tmp/video_tasks.json","w") as f:
    json.dump(tasks, f)
print("Tasks saved to /tmp/video_tasks.json")
conn.close()
