"""Poll video completion and synthesize final video"""
import json, urllib.request, time, sqlite3, subprocess, os, shutil

k = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"

def poll_task(tid):
    req = urllib.request.Request(BASE+"/videos/"+tid, headers={"Authorization":"Bearer "+k})
    resp = urllib.request.urlopen(req, timeout=30)
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

with open("/tmp/video_tasks.json") as f:
    tasks = json.load(f)

conn = sqlite3.connect("/root/portal/data/portal.db")

print("=== Polling %d video tasks ===" % len(tasks))

for round_num in range(40):
    pending = [t for t in tasks if t.get("status","processing")=="processing" and t.get("task_id")]
    if not pending:
        print("All done!")
        break
    
    print("\nRound %d: %d pending..." % (round_num+1, len(pending)))
    
    for t in pending:
        tid = t["task_id"]
        snum = t["scene"]
        try:
            result = poll_task(tid)
            status = result.get("status","processing")
            vid_url = find_url(result)
            
            if vid_url:
                t["status"] = "done"
                t["video_url"] = vid_url
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE project_id=2 AND scene_number=?", (vid_url, snum))
                conn.commit()
                print("  Scene %d: COMPLETED" % snum)
            else:
                print("  Scene %d: %s" % (snum, status))
        except Exception as e:
            print("  Scene %d: %s" % (snum, str(e)[:50]))
        time.sleep(2)
    
    if pending:
        time.sleep(60)

# Check results
print("\n=== Results ===")
done = [t for t in tasks if t.get("status")=="done"]
failed = [t for t in tasks if t.get("status")!="done"]
print("Done: %d, Failed: %d" % (len(done), len(failed)))

if not done:
    print("No videos completed!")
    conn.close()
    exit(1)

# Step 5: Download and synthesize
print("\n=== Synthesizing final video ===")
tmp = "/tmp/manga_synth"
os.makedirs(tmp, exist_ok=True)

segments = []
for t in done:
    snum = t["scene"]
    url = t["video_url"]
    path = "%s/scene_%02d.mp4" % (tmp, snum)
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(path, "wb") as f:
                f.write(resp.read())
        size = os.path.getsize(path)
        if size > 1000:
            segments.append(path)
            print("  Downloaded scene %d: %d bytes" % (snum, size))
    except Exception as e:
        print("  Failed scene %d: %s" % (snum, e))

if not segments:
    print("No segments to synthesize!")
    conn.close()
    exit(1)

# FFmpeg concat
with open("%s/concat.txt" % tmp, "w") as f:
    for p in segments:
        f.write("file '%s'\n" % p)

out = "/tmp/manga_complete.mp4"
cmd = ["ffmpeg","-y","-f","concat","-safe","-0","-i","%s/concat.txt"%tmp,
       "-c","libx264","-preset","fast","-crf","23","-pix_fmt","yuv420p",
       "-movflags","+faststart", out]

print("Running FFmpeg...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
if result.returncode == 0 and os.path.exists(out):
    size = os.path.getsize(out)
    print("SUCCESS: %s (%.1f MB)" % (out, size/1024/1024))
    
    # Copy to static
    dest = "/root/portal/static/videos/manga_complete.mp4"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(out, dest)
    print("Saved to: %s" % dest)
    
    # Update project status
    conn.execute("UPDATE manga_projects SET status='completed' WHERE id=2")
    conn.commit()
else:
    print("FFmpeg error: %s" % result.stderr[:500])

conn.close()
print("\n=== DONE ===")
