"""Submit all video tasks quickly, then poll"""
import json, urllib.request, time, sqlite3

k = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"
H = {"Authorization": "Bearer " + k, "Content-Type": "application/json"}

def call(endpoint, data, timeout=180):
    req = urllib.request.Request(BASE + endpoint, headers=H, data=json.dumps(data).encode())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

with open("/tmp/scene_images.json") as f:
    scenes = json.load(f)

# Submit all tasks first (fast)
print("Submitting %d video tasks..." % len(scenes))
tasks = []
for s in scenes:
    snum = s["scene_number"]
    title = s["title"]
    vp = s.get("video_prompt", title)
    try:
        r = call("/videos", {"model":"agnes-video-v2.0","prompt":"anime manga style, smooth camera movement, cinematic, "+vp[:400],"num_frames":81,"frame_rate":24}, timeout=180)
        tid = r.get("task_id") or r.get("id")
        url = None
        def find(obj, d=0):
            if d>6: return None
            if isinstance(obj,str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","video","mp4"]): return obj
            if isinstance(obj,dict):
                for k,v in obj.items():
                    if isinstance(v,str) and v.startswith("http"): return v
                    x = find(v,d+1)
                    if x: return x
            if isinstance(obj,list):
                for i in obj:
                    x = find(i,d+1)
                    if x: return x
            return None
        url = find(r)
        tasks.append({"scene_number":snum,"title":title,"task_id":str(tid) if tid else None,"video_url":url,"status":"done" if url else "processing"})
        print("  Scene %d: %s [%s]" % (snum, title, "done" if url else "task="+str(tid)[:20]))
    except Exception as e:
        tasks.append({"scene_number":snum,"title":title,"task_id":None,"video_url":None,"status":"failed"})
        print("  Scene %d: FAILED %s" % (snum, e))

# Save tasks
with open("/tmp/video_tasks.json","w") as f:
    json.dump(tasks, f)

# Poll for completion
print("\nPolling for completion...")
for round_num in range(30):
    pending = [t for t in tasks if t["status"]=="processing" and t.get("task_id")]
    if not pending:
        break
    print("\nRound %d: %d pending..." % (round_num+1, len(pending)))
    for t in pending:
        try:
            r = call("/videos/"+t["task_id"], {}, timeout=30)
            st = r.get("status","processing")
            def find(obj, d=0):
                if d>6: return None
                if isinstance(obj,str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","video","mp4"]): return obj
                if isinstance(obj,dict):
                    for k,v in obj.items():
                        if isinstance(v,str) and v.startswith("http"): return v
                        x = find(v,d+1)
                        if x: return x
                if isinstance(obj,list):
                    for i in obj:
                        x = find(i,d+1)
                        if x: return x
                return None
            url = find(r)
            if url:
                t["video_url"] = url
                t["status"] = "done"
                print("  Scene %d: COMPLETED" % t["scene_number"])
            elif st in ("completed","success","done"):
                print("  Scene %d: done but no URL" % t["scene_number"])
                t["status"] = "completed_no_url"
            else:
                print("  Scene %d: %s" % (t["scene_number"], st))
        except Exception as e:
            print("  Scene %d: poll error %s" % (t["scene_number"], e))
        time.sleep(2)
    if pending:
        time.sleep(30)

# Final
print("\n=== FINAL ===")
for t in tasks:
    print("Scene %d %s: %s" % (t["scene_number"], t["title"], t["status"]))

# Save to DB
conn = sqlite3.connect("/root/portal/data/portal.db")
for t in tasks:
    conn.execute("UPDATE manga_scenes SET video_url=?, video_task_id=?, status=? WHERE project_id=2 AND scene_number=?",
        (t["video_url"], t["task_id"], t["status"], t["scene_number"]))
conn.commit()
conn.close()
with open("/tmp/video_tasks_final.json","w") as f:
    json.dump(tasks, f)
print("\nDone!")
