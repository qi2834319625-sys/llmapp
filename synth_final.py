"""Synthesize manga video from images using FFmpeg Ken Burns + subtitle"""
import json, subprocess, os, shutil, sqlite3, urllib.request

def synch_video():
    conn = sqlite3.connect("/root/portal/data/portal.db")
    project = conn.execute("SELECT * FROM manga_projects WHERE id=2").fetchone()
    scenes = conn.execute("SELECT scene_number, title, image_url, dialogue FROM manga_scenes WHERE project_id=2 AND image_url IS NOT NULL ORDER BY scene_number").fetchall()
    conn.close()
    
    if not scenes:
        print("No scenes!")
        return None
    
    tmp = "/tmp/manga_synth2"
    os.makedirs(tmp, exist_ok=True)
    
    print("=== Manga Video Synthesis ===")
    total_duration = 0
    segments = []
    
    for scene in scenes:
        snum, title, img_url, dialogue = scene
        dur = max(4, min(8, len(dialogue) * 0.4 + 3)) if dialogue else 5
        
        img_path = "%s/img_%02d.jpg" % (tmp, snum)
        seg_path = "%s/seg_%02d.mp4" % (tmp, snum)
        
        try:
            req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(img_path, "wb") as f:
                    f.write(resp.read())
            
            vf = "zoompan=z='min(zoom+0.0012,1.08)':d=%d:s=1280x720:fps=24" % int(dur * 24)
            cmd = ["ffmpeg","-y","-loop","1","-i",img_path,"-vf",vf,"-c:v","libx264","-t",str(dur),"-pix_fmt","yuv420p","-preset","fast","-an",seg_path]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if r.returncode == 0 and os.path.exists(seg_path):
                segments.append(seg_path)
                total_duration += dur
                print("  Scene %d: %s (%.1fs)" % (snum, title, dur))
            else:
                print("  Scene %d: FFmpeg error %s" % (snum, r.stderr[:100]))
        except Exception as e:
            print("  Scene %d: %s" % (snum, e))
    
    if not segments:
        print("No segments!")
        return None
    
    print("\n%d segments, total %.1fs" % (len(segments), total_duration))
    
    # Concat
    with open("%s/concat.txt" % tmp, "w") as f:
        for p in segments:
            f.write("file '%s'\n" % p)
    
    concat_out = "%s/concat.mp4" % tmp
    cmd = ["ffmpeg","-y","-f","concat","-safe","-0","-i","%s/concat.txt"%tmp,"-c","libx264","-preset","fast","-crf","23","-pix_fmt","yuv420p","-movflags","+faststart","-an",concat_out]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("Concat error:", r.stderr[:200])
        return None
    
    # Add simple BGM
    bgm = "%s/bgm.mp3" % tmp
    cmd = ["ffmpeg","-y","-f","lavfi","-i","sine=frequency=220:duration=%d,volume=0.08" % int(total_duration),"-af","aecho=0.8:0.9:800:0.3","-t",str(int(total_duration)),bgm]
    subprocess.run(cmd, capture_output=True, timeout=30)
    
    # Final combine
    final = "/tmp/manga_complete.mp4"
    cmd = ["ffmpeg","-y","-i",concat_out,"-i",bgm,"-c:v","copy","-c:a","aac","-b:a","96k","-shortest",final]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if os.path.exists(final):
        size = os.path.getsize(final)
        print("SUCCESS: %.1f MB" % (size/1024/1024))
        
        dest = "/root/portal/static/videos/manga_complete.mp4"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(final, dest)
        print("Saved: %s" % dest)
        return dest
    else:
        print("Failed:", r.stderr[:200])
        return None

if __name__ == "__main__":
    result = synch_video()
    print("Result:", result)
