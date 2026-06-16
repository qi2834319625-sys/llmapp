"""
Synthesize complete manga video from images + BGM + subtitles using FFmpeg
No video generation API needed - uses Ken Burns effect on static images
"""
import json, subprocess, os, shutil, sqlite3

def get_db():
    conn = sqlite3.connect("/root/portal/data/portal.db")
    conn.row_factory = sqlite3.Row
    return conn

def synthesize_manga_video(output_path, with_subtitles=True):
    """Create a complete manga video from static images using Ken Burns effect"""
    
    conn = get_db()
    project = conn.execute("SELECT * FROM manga_projects WHERE id=2").fetchone()
    scenes = conn.execute("SELECT * FROM manga_scenes WHERE project_id=2 AND image_url IS NOT NULL ORDER BY scene_number").fetchall()
    conn.close()
    
    if not scenes:
        print("No scenes with images found!")
        return None
    
    tmp = "/tmp/manga_synth"
    os.makedirs(tmp, exist_ok=True)
    
    print("=== Manga Video Synthesis ===")
    print("Project: %s" % project["title"])
    print("Scenes: %d" % len(scenes))
    
    # Download images and create video segments with Ken Burns effect
    segments = []
    for i, scene in enumerate(scenes):
        snum = scene["scene_number"]
        title = scene["title"]
        img_url = scene["image_url"]
        dialogue = scene["dialogue"] or ""
        duration = max(4, min(8, len(dialogue) * 0.5 + 3))  # 4-8 seconds based on dialogue length
        
        img_path = "%s/scene_%02d.jpg" % (tmp, snum)
        
        # Download image
        try:
            import urllib.request
            req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(img_path, "wb") as f:
                    f.write(resp.read())
            print("  Scene %d: %s (%.1fs)" % (snum, title, duration))
        except Exception as e:
            print("  Scene %d: download failed - %s" % (snum, e))
            continue
        
        # Create video segment with Ken Burns zoom effect
        seg_path = "%s/segment_%02d.mp4" % (tmp, snum)
        
        # FFmpeg Ken Burns effect: slow zoom from 1.0 to 1.1 while panning slightly
        vf = "zoompan=z='min(zoom+0.0015,1.1)':d=%d:s=1280x720:fps=24" % int(duration * 24)
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-vf", vf,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-an",  # No audio yet
            seg_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and os.path.exists(seg_path):
            "title": title,
            "dialogue": dialogue,
            "duration": duration,
            "scene_number": snum
            })
        except Exception as e:
            print("  Scene %d: FFmpeg error - %s" % (snum, e.strerror[:200] if hasattr(e, 'stderr') else str(e)[:200]))
    
    if not segments:
        print("No segments created!")
        return None
    
    print("\n%d segments created" % len(segments))
    
    # Create concat file
    concat_file = "%s/concat.txt" % tmp
    with open(concat_file, "w") as f:
        for seg in segments:
            f.write("file '%s'\n" % seg["path"])
    
    # Add title card at the beginning
    title_card = "%s/title.mp4" % tmp
    title_vf = "drawtext=text='%s':fontsize=64:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=white:box=1:boxcolor=black@0.7:borderw=4" % project["title"]
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=3",
        "-vf", title_vf,
        "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p", "-an",
        title_card
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    
    if os.path.exists(title_card):
        with open(concat_file, "w") as f:
            f.write("file '%s'\n" % title_card)
            for seg in segments:
                f.write("file '%s'\n" % seg["path"])
    
    # Add ending card
    end_card = "%s/end.mp4" % tmp
    end_vf = "drawtext=text='Coming Soon...':fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=white:box=1:boxcolor=black@0.7"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=3",
        "-vf", end_vf,
        "-c:v", "libx264", "-t", "3", "-pix_fmt", "yuv420p", "-an",
        end_card
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    
    if os.path.exists(end_card):
        with open(concat_file, "a") as f:
            f.write("file '%s'\n" % end_card)
    
    # Concatenate all segments
    concat_output = "%s/concat.mp4" % tmp
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",
        concat_output
    ]
    print("\nConcatenating segments...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print("Concat error: %s" % result.stderr[:300])
        return None
    
    # Add background music (create a simple ambient track)
    bgm_path = "%s/bgm.mp3" % tmp
    # Generate 30 seconds of ambient music using FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=30,volume=0.1",
        "-af", "aecho=0.8:0.9:1000:0.3,stereotools=mlev=0.5",
        "-t", "30",
        bgm_path
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    
    # Combine video with BGM
    final_cmd = [
        "ffmpeg", "-y",
        "-i", concat_output,
        "-i", bgm_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output_path
    ]
    print("Adding background music...")
    result = subprocess.run(final_cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print("\n=== SUCCESS ===")
        print("Output: %s (%.1f MB)" % (output_path, size / 1024 / 1024))
        
        # Copy to static for web access
        static_dir = "/root/portal/static/videos"
        os.makedirs(static_dir, exist_ok=True)
        static_path = "%s/manga_complete.mp4" % static_dir
        shutil.copy2(output_path, static_path)
        print("Web access: %s" % static_path)
        
        return static_path
    else:
        print("Final combine error: %s" % result.stderr[:300])
        return concat_output if os.path.exists(concat_output) else None

if __name__ == "__main__":
    result = synthesize_manga_video("/tmp/manga_complete.mp4")
    if result:
        print("\nDone! Video at: %s" % result)
    else:
        print("\nFailed!")
