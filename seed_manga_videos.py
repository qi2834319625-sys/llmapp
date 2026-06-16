"""
Generate videos for all scenes using Agnes AI Video V2.0
"""
import json, urllib.request, urllib.parse, time, sqlite3

AGNES_API_KEY = "sk-gScQfsupCor8Cp6O7pHS8IhxdbttANFlgLNQ3plVNWSToZ8R"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

def generate_video(prompt, num_frames=81, frame_rate=24, retries=2):
    """Generate video using Agnes AI Video V2.0"""
    for attempt in range(retries):
        try:
            data = json.dumps({
                "model": "agnes-video-v2.0",
                "prompt": f"anime manga style, smooth camera movement, cinematic, {prompt[:400]}",
                "num_frames": num_frames,
                "frame_rate": frame_rate
            }).encode()
            
            req = urllib.request.Request(
                f"{AGNES_BASE_URL}/videos",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                data=data
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode())
                print(f"  API Response: {json.dumps(result, ensure_ascii=False)[:200]}")
                
                # Try different response formats
                task_id = result.get("task_id") or result.get("id") or result.get("data", {}).get("task_id") or result.get("data", {}).get("id")
                if task_id:
                    return str(task_id)
                
                # Maybe it's synchronous and returns video directly
                video_url = result.get("url") or result.get("video_url") or result.get("data", {}).get("url")
                if video_url:
                    return f"direct:{video_url}"
                    
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(10)
    return None


def check_video_status(task_id):
    """Check video generation status"""
    if task_id.startswith("direct:"):
        return "completed", task_id[7:]
    
    try:
        req = urllib.request.Request(
            f"{AGNES_BASE_URL}/videos/{task_id}",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            status = result.get("status", "processing")
            video_url = result.get("url") or result.get("video_url") or result.get("data", {}).get("url") or result.get("data", {}).get("video_url")
            return status, video_url
    except Exception as e:
        print(f"  Status check error: {e}")
        return "processing", None


def generate_all_videos():
    conn = sqlite3.connect("/root/portal/data/portal.db")
    scenes = conn.execute("""
        SELECT ms.id, ms.scene_number, ms.title, ms.image_prompt, ms.description, ms.characters, ms.video_task_id, ms.status
        FROM manga_scenes ms
        JOIN manga_projects mp ON ms.project_id = mp.id
        WHERE mp.title LIKE '斗破苍穹%'
        ORDER BY ms.scene_number
    """).fetchall()
    
    print(f"Found {len(scenes)} scenes for video generation")
    
    for scene in scenes:
        scene_id, scene_num, title, img_prompt, desc, chars, existing_task, status = scene
        
        # Skip if already has video
        if status == 'done' or (existing_task and existing_task.startswith('direct:')):
            print(f"  Scene {scene_num} '{title}' - already has video, skipping")
            continue
        
        # Skip if already processing
        if status == 'video_processing' and existing_task:
            print(f"  Scene {scene_num} '{title}' - already processing (task: {existing_task}), checking status...")
            vid_status, video_url = check_video_status(existing_task)
            print(f"    Status: {vid_status}")
            if vid_status == "completed" and video_url:
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (video_url, scene_id))
                conn.commit()
                print(f"    ✓ Video completed!")
            continue
        
        # Generate new video
        prompt = img_prompt or desc or f"anime style, {chars}, cinematic scene"
        print(f"  Scene {scene_num} '{title}' - generating video...")
        print(f"    Prompt: {prompt[:80]}...")
        
        task_id = generate_video(prompt)
        
        if task_id:
            if task_id.startswith("direct:"):
                # Synchronous response
                video_url = task_id[7:]
                conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (video_url, scene_id))
                conn.commit()
                print(f"    ✓ Video generated directly: {video_url[:60]}...")
            else:
                # Async task
                conn.execute("UPDATE manga_scenes SET video_task_id=?, status='video_processing' WHERE id=?", (task_id, scene_id))
                conn.commit()
                print(f"    ✓ Video task submitted: {task_id}")
        else:
            print(f"    ✗ Video generation failed")
        
        time.sleep(5)  # Rate limiting between requests
    
    # Final status check
    print("\n--- Final Status ---")
    scenes = conn.execute("""
        SELECT ms.scene_number, ms.title, ms.status, ms.video_url, ms.video_task_id
        FROM manga_scenes ms
        JOIN manga_projects mp ON ms.project_id = mp.id
        WHERE mp.title LIKE '斗破苍穹%'
        ORDER BY ms.scene_number
    """).fetchall()
    
    for s in scenes:
        status_icon = "✓" if s[2] == "done" else ("⏳" if s[2] == "video_processing" else "○")
        print(f"  {status_icon} Scene {s[0]} '{s[1]}': {s[2]}")
        if s[3]:
            print(f"      Video: {s[3][:60]}...")
    
    conn.close()


if __name__ == "__main__":
    generate_all_videos()
