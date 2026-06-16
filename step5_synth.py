"""Step 5: Synthesize final video with FFmpeg"""
import json, subprocess, os, shutil, sqlite3

with open("/tmp/video_tasks_final.json") as f:
    tasks = json.load(f)

print("=== Step 5: Video Synthesis ===")

tmp = "/tmp/manga_synth"
os.makedirs(tmp, exist_ok=True)

# Download completed videos
segments = []
for t in tasks:
    if t["status"] != "done" or not t.get("video_url"):
        continue
    path = "%s/scene_%02d.mp4" % (tmp, t["scene_number"])
    try:
        req = __import__("urllib").request.Request(t["video_url"], headers={"User-Agent":"Mozilla/5.0"})
        with __import__("urllib").request.urlopen(req, timeout=120) as resp:
            with open(path, "wb") as f:
                f.write(resp.read())
        size = os.path.getsize(path)
        if size > 1000:
            segments.append((path, t))
            print("  Downloaded scene %d: %d bytes" % (t["scene_number"], size))
    except Exception as e:
        print("  Failed scene %d: %s" % (t["scene_number"], e))

if not segments:
    print("No segments!")
    exit(1)

# Create concat file
with open("%s/concat.txt" % tmp, "w") as f:
    for path, t in segments:
        f.write("file '%s'\n" % path)

# FFmpeg concat
out = "/tmp/manga_complete.mp4"
cmd = ["ffmpeg","-y","-f","concat","-safe","-0","-i","%s/concat.txt"%tmp,
       "-c","libx264","-preset","fast","-crf","23","-pix_fmt","yuv420p",
       "-movflags","+faststart", out]

print("Running FFmpeg...")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
if result.returncode == 0 and os.path.exists(out):
    size = os.path.getsize(out)
    print("SUCCESS: %s (%d bytes)" % (out, size))
    # Copy to static
    dest = "/root/portal/static/videos/manga_complete.mp4"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(out, dest)
    print("Saved to: %s" % dest)
else:
    print("FFmpeg error: %s" % result.stderr[:500])
