import json, urllib.request, time, sqlite3

API_KEY = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"

def find_url(obj, depth=0):
    if depth > 6: return None
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["video","output","storage","platform","mp4"]):
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

def post(path, data, timeout=120):
    payload = json.dumps(data).encode()
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"}, data=payload)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def get(path, timeout=30):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + API_KEY})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

conn = sqlite3.connect("/root/portal/data/portal.db")
scenes = conn.execute("SELECT ms.id, ms.scene_number, ms.title, ms.image_prompt, ms.description, ms.characters, ms.video_task_id, ms.status FROM manga_scenes ms JOIN manga_projects mp ON ms.project_id = mp.id WHERE mp.id = 2 ORDER BY ms.scene_number").fetchall()
print("Processing %d scenes..." % len(scenes))

for sid, snum, title, ip, desc, chars, task_id, status in scenes:
    print("\nScene %d: %s [%s]" % (snum, title, status))
    
    if task_id and status == "video_processing":
        try:
            result = get("/videos/" + task_id)
            new_status = result.get("status", "processing")
            vid_url = find_url(result)
            print("  Check: status=%s url=%s" % (new_status, (vid_url[:60]+"...") if vid_url else "none"))
            if vid_url:
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (vid_url, sid))
                conn.commit()
                print("  SAVED!")
                continue
            elif new_status in ("completed","done","success","finished"):
                print("  Completed but no URL. Response: %s" % json.dumps(result, ensure_ascii=False)[:400])
                continue
            else:
                print("  Still processing...")
                continue
        except Exception as e:
            print("  Check error: %s" % e)
    
    if status == "done":
        print("  Already done.")
        continue
    
    prompt = (ip or desc or ("anime style, " + chars + ", cinematic"))[:400]
    print("  Generating: %s..." % prompt[:80])
    
    try:
        result = post("/videos", {"model": "agnes-video-v2.0", "prompt": "anime manga style, smooth camera movement, cinematic, " + prompt, "num_frames": 81, "frame_rate": 24})
        new_task = result.get("task_id") or result.get("id")
        vid_url = find_url(result)
        print("  Result: task=%s url=%s" % (new_task, (vid_url[:60]+"...") if vid_url else "none"))
        
        if vid_url:
            conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (vid_url, sid))
            conn.commit()
            print("  DIRECT SAVE!")
        elif new_task:
            conn.execute("UPDATE manga_scenes SET video_task_id=?, status='video_processing' WHERE id=?", (new_task, sid))
            conn.commit()
            print("  Task: %s" % new_task)
        else:
            print("  Unexpected: %s" % json.dumps(result, ensure_ascii=False)[:300])
    except Exception as e:
        print("  Error: %s" % e)
    
    time.sleep(5)

print("\n=== FINAL ===")
rows = conn.execute("SELECT scene_number, title, status, CASE WHEN video_url IS NOT NULL THEN 'YES' ELSE 'NO' END FROM manga_scenes WHERE project_id=2 ORDER BY scene_number").fetchall()
for r in rows:
    print("  S%d '%s': %s video=%s" % (r[0], r[1], r[2], r[3]))
conn.close()
