"""
Manga Pipeline v2 - Fixed storyboard generation with smaller batches
"""
import json, urllib.request, urllib.parse, time, sqlite3, os, subprocess

AGNES_API_KEY=open("/root/portal/.agnes_key").read().strip()
AGNES_BASE="https://apihub.agnes-ai.com/v1"

def api_call(endpoint, data, timeout=120):
    payload = json.dumps(data).encode()
    req = urllib.request.Request(AGNES_BASE + endpoint,
        headers={"Authorization": "Bearer " + AGNES_API_KEY, "Content-Type": "application/json"},
        data=payload)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def find_url(obj, depth=0):
    if depth > 6: return None
    if isinstance(obj, str) and obj.startswith("http") and ("storage" in obj.lower() or "output" in obj.lower() or "platform" in obj.lower() or "video" in obj.lower() or "mp4" in obj.lower()):
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

def chat(prompt, max_tokens=4000):
    result = api_call("/chat/completions", {
        "model": "agnes-2.0-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8
    }, timeout=120)
    return result.get("choices", [{}])[0].get("message", {}).get("content", "")

def gen_image(prompt, size="1024x768"):
    result = api_call("/images/generations", {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt[:500],
        "size": size
    }, timeout=120)
    return find_url(result)

def gen_video(prompt, frames=81, fps=24):
    result = api_call("/videos", {
        "model": "agnes-video-v2.0",
        "prompt": prompt[:400],
        "num_frames": frames,
        "frame_rate": fps
    }, timeout=180)
    vid_url = find_url(result)
    if vid_url:
        return ("direct", vid_url)
    task_id = result.get("task_id") or result.get("id")
    if task_id:
        return ("task", str(task_id))
    return (None, None)

def check_video(task_id):
    if task_id.startswith("direct:"): return "completed", task_id[7:]
    try:
        req = urllib.request.Request(AGNES_BASE + "/videos/" + task_id,
            headers={"Authorization": "Bearer " + AGNES_API_KEY})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            status = result.get("status", "processing")
            url = find_url(result)
            return status, url
    except:
        return "processing", None

def download_file(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(path, "wb") as f:
            f.write(resp.read())
    return os.path.getsize(path)

# ========== Novel ==========
NOVEL = open("/root/portal/novel_doupo.txt").read() if os.path.exists("/root/portal/novel_doupo.txt") else ""

# ========== Step 1: Character Design ==========
def generate_character_sheets():
    """Generate character design sheets"""
    print("[Step 1] Character design...")
    
    # Use fixed character definitions for consistency
    characters = [
        {
            "name": "萧炎",
            "gender": "男", "age": "15", "role": "主角",
            "appearance": "black hair, black eyes, lean build, handsome face with determined expression, about 170cm tall",
            "personality": "resilient, determined, kind-hearted",
            "outfit": "gray martial arts robes, black belt, black boots, long sword on back",
            "prompt": "anime style character sheet, full body portrait, front view, young male age 15, black hair, black eyes, lean build, handsome face, determined expression, gray martial arts robes, black belt, black boots, long sword on back, white background, clean line art, detailed face, expressive eyes, manga illustration, high quality",
            "color_palette": "black, gray, dark blue"
        },
        {
            "name": "萧薰儿",
            "gender": "女", "age": "14", "role": "女主角",
            "appearance": "long flowing black hair to waist, violet eyes, fair porcelain skin, petite build about 160cm, beautiful and elegant",
            "personality": "gentle, loyal, quietly protective",
            "outfit": "purple dress with golden embroidery, white stockings, purple shoes, jade bracelet",
            "prompt": "anime style character sheet, full body portrait, front view, young female age 14, long flowing black hair, violet eyes, fair skin, petite beautiful girl, elegant, purple dress with golden embroidery, white stockings, purple shoes, jade bracelet, white background, clean line art, detailed face, gentle expression, manga illustration, high quality",
            "color_palette": "purple, gold, white, black"
        },
        {
            "name": "萧宁",
            "gender": "男", "age": "16", "role": "反派",
            "appearance": "brown hair, brown eyes, tall strong build about 175cm, handsome but arrogant expression",
            "personality": "arrogant, jealous, insecure underneath",
            "outfit": "blue martial arts robes with silver trim, silver belt, leather boots, jade pendant",
            "prompt": "anime style character sheet, full body portrait, front view, young male age 16, brown hair, brown eyes, tall strong build, handsome face with arrogant expression, blue martial arts robes with silver trim, silver belt, leather boots, jade pendant, white background, clean line art, detailed face, manga illustration, high quality",
            "color_palette": "blue, silver, brown"
        }
    ]
    
    # Generate character sheet images
    for char in characters:
        print("  Generating sheet for %s..." % char["name"])
        url = gen_image(char["prompt"])
        char["sheet_url"] = url
        print("    -> %s" % (url[:60] if url else "FAILED"))
        time.sleep(3)
    
    return characters

# ========== Step 2: Storyboard (batch generation) ==========
def generate_storyboard_batch(characters, scene_range):
    """Generate storyboard for a batch of scenes"""
    char_desc = "\n".join(["- %s (%s): %s, wearing %s" % (c["name"], c["role"], c["appearance"], c["outfit"]) for c in characters])
    
    prompt = """You are a professional manga director. Generate storyboard scenes %d-%d for the following novel.

Novel excerpt:
%s

Character designs:
%s

Output JSON format (ONLY JSON, no other text):
{"scenes": [{"scene_number": N, "title": "Scene Title", "duration": 5, "camera": "close-up/medium/wide/pan/zoom-in/zoom-out", "mood": "emotion/atmosphere", "action": "detailed action description in English, 80 words max", "dialogue": "dialogue in Chinese", "speaker": "character name", "image_prompt": "full AI image generation prompt in English, include character appearance, clothing, scene, lighting, atmosphere, camera angle. Must match character design for consistency.", "video_prompt": "image-to-video prompt in English, describe motion and camera movement"}]}

Requirements:
1. Each scene 5-8 seconds
2. Camera variety: close-up, medium, wide, pan, zoom
3. Include character expressions, actions, scene details
4. image_prompt MUST include character appearance and clothing for consistency
5. Mood/atmosphere with lighting and color tone
6. Dialogue is character's line in Chinese""" % (scene_range[0], scene_range[1], NOVEL[:3000], char_desc)
    
    content = chat(prompt, max_tokens=6000)
    
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(content[start:end])
            return data.get("scenes", [])
    except Exception as e:
        print("  Parse error: %s" % e)
        print("  Content: %s..." % content[:200])
    return []

def generate_storyboard(characters):
    """Generate complete storyboard in batches"""
    print("[Step 2] Generating storyboard...")
    
    all_scenes = []
    # Generate in batches of 2 scenes to avoid JSON truncation
    for start in range(1, 9, 2):
        end = min(start + 1, 8)
        print("  Batch %d-%d..." % (start, end))
        scenes = generate_storyboard_batch(characters, (start, end))
        all_scenes.extend(scenes)
        time.sleep(2)
    
    # If batch generation failed, use fallback
    if not all_scenes:
        print("  Using fallback storyboard...")
        all_scenes = [
            {"scene_number": 1, "title": "刺眼的真相", "duration": 6, "camera": "close-up", "mood": "压抑、刺痛", "action": "Extreme close-up on the glowing stone monument showing 'Level 3', crowd whispering in background, Xiao Yan's pained expression", "dialogue": "萧炎，斗之气，三段！级别：低级！", "speaker": "测验师", "image_prompt": "anime manga style, extreme close-up of glowing stone monument with 'Level 3' text, young man with black hair and black eyes looking pained, gray martial arts robes, cold lighting, ancient Chinese martial arts plaza, crowd silhouettes in background, dramatic shadows, high detail", "video_prompt": "slow zoom out from the glowing monument to reveal the young man's face, crowd whispering, camera shake"},
            {"scene_number": 2, "title": "嘲讽声浪", "duration": 5, "camera": "medium", "mood": "屈辱、愤怒", "action": "Xiao Yan standing alone, fists clenched, blood dripping from palm, surrounded by sneering crowd, his expression a mix of pain and defiance", "dialogue": "三段？嘿嘿，果然不出你所料，这个'天才'这一年又是在原地踏步！", "speaker": "围观者", "image_prompt": "anime manga style, medium shot of young man in gray robes standing alone, clenched fists with blood drops, crowd of people sneering and pointing, dramatic side lighting, ancient Chinese plaza, emotional intensity, detailed face showing pain and defiance", "video_prompt": "camera slowly pans around the isolated young man, crowd moving and whispering, blood dripping in slow motion"},
            {"scene_number": 3, "title": "薰儿登场", "duration": 6, "camera": "wide", "mood": "惊艳、期待", "action": "Beautiful girl in purple dress walking confidently toward the stone monument, all eyes on her, wind blowing her long black hair, golden light around her", "dialogue": "下一个，萧薰儿！", "speaker": "测验师", "image_prompt": "anime manga style, wide shot of beautiful young girl in purple dress with golden embroidery walking confidently, long flowing black hair, violet eyes, fair skin, crowd watching in awe, golden light rays, ancient Chinese martial arts plaza, cinematic composition", "video_prompt": "slow motion walk toward the monument, hair and dress flowing in wind, camera tracking from behind then revealing her face"},
            {"scene_number": 4, "title": "天才之光", "duration": 5, "camera": "close-up", "mood": "震撼、惊叹", "action": "Xiao Xun'er's hand touching the monument, brilliant golden light erupting, her calm expression, crowd gasping", "dialogue": "斗之气：九段！级别：高级！", "speaker": "测验师", "image_prompt": "anime manga style, close-up of beautiful girl's hand touching glowing stone monument, brilliant golden light explosion, purple dress, long black hair, calm elegant expression, crowd gasping in background, magical atmosphere, dramatic lighting", "video_prompt": "hand touches monument, light erupts in slow motion, camera pulls back to show crowd reaction"},
            {"scene_number": 5, "title": "暗中关怀", "duration": 4, "camera": "medium", "mood": "温柔、担忧", "action": "Xiao Xun'er looking at Xiao Yan from the crowd, her violet eyes full of concern and unspoken feelings, soft lighting on her face", "dialogue": "（旁白）少女将目光投向了人群后方，那个孤独站立的少年身上。", "speaker": "旁白", "image_prompt": "anime manga style, medium shot of beautiful girl in purple dress looking at someone off-screen, violet eyes full of concern, soft gentle lighting on her face, crowd in background, emotional and tender moment, detailed expressive eyes", "video_prompt": "slow pan from her concerned face to reveal the lonely young man in the crowd"},
            {"scene_number": 6, "title": "萧宁挑衅", "duration": 5, "camera": "medium", "mood": "傲慢、挑衅", "action": "Xiao Ning in blue robes standing proudly, pointing and laughing at Xiao Yan, arrogant expression, silver trim gleaming", "dialogue": "萧炎，你现在还有什么资格让我重视？", "speaker": "萧宁", "image_prompt": "anime manga style, medium shot of handsome young man in blue martial arts robes with silver trim, arrogant expression, pointing and laughing, confident pose, ancient Chinese plaza, dramatic lighting, detailed face showing contempt", "video_prompt": "arrogant laugh, pointing gesture, camera slightly low angle to emphasize his arrogance"},
            {"scene_number": 7, "title": "孤独离场", "duration": 5, "camera": "wide", "mood": "孤独、决绝", "action": "Xiao Yan walking away alone through the crowd, his back straight despite the humiliation, gray robes fluttering, sunset light casting long shadows", "dialogue": "萧炎面无表情，转身向广场外走去。", "speaker": "旁白", "image_prompt": "anime manga style, wide shot of young man in gray robes walking away alone through crowd, back straight, sunset light casting long shadows, ancient Chinese plaza, melancholic atmosphere, cinematic composition, detailed back view", "video_prompt": "slow tracking shot following the young man walking away, crowd parting, sunset light fading"},
            {"scene_number": 8, "title": "夕阳同行", "duration": 6, "camera": "wide", "mood": "温暖、希望", "action": "Xiao Xun'er catching up to Xiao Yan, both walking together toward the sunset, their silhouettes side by side, warm orange light", "dialogue": "炎哥哥，你没事吧？走吧，回家。", "speaker": "萧薰儿", "image_prompt": "anime manga style, wide shot of two young figures walking side by side toward sunset, girl in purple dress and boy in gray robes, warm orange and purple sky, long shadows, ancient Chinese town in background, hopeful and tender atmosphere, beautiful landscape", "video_prompt": "slow motion walk into sunset, camera rising to show the vast sky, warm light enveloping the two figures"}
        ]
    
    print("  Total scenes: %d" % len(all_scenes))
    return all_scenes

# ========== Step 3: Generate Images ==========
def generate_scene_images(storyboard, characters):
    """Generate images with character consistency"""
    print("[Step 3] Generating scene images...")
    
    # Build character reference for consistency
    char_refs = []
    for c in characters:
        if c.get("sheet_url"):
            char_refs.append("%s: %s" % (c["name"], c["appearance"]))
    ref_text = "Character references: " + "; ".join(char_refs) if char_refs else ""
    
    images = []
    for scene in storyboard:
        snum = scene["scene_number"]
        print("  Scene %d: %s..." % (snum, scene["title"]))
        
        # Enhance prompt with character consistency
        enhanced_prompt = scene["image_prompt"]
        if ref_text:
            enhanced_prompt = enhanced_prompt + ". " + ref_text
        # Add consistency tags
        enhanced_prompt = enhanced_prompt + ", consistent character design, same art style throughout, anime manga illustration"
        
        url = gen_image(enhanced_prompt)
        images.append({
            "scene_number": snum,
            "title": scene["title"],
            "image_url": url,
            "dialogue": scene.get("dialogue", ""),
            "duration": scene.get("duration", 5),
            "camera": scene.get("camera", ""),
            "mood": scene.get("mood", ""),
            "video_prompt": scene.get("video_prompt", "")
        })
        print("    -> %s" % ("OK" if url else "FAILED"))
        time.sleep(3)
    
    return images

# ========== Step 4: Generate Videos ==========
def generate_scene_videos(images):
    """Generate videos from images"""
    print("[Step 4] Generating scene videos...")
    videos = []
    for img in images:
        snum = img["scene_number"]
        print("  Scene %d: %s..." % (snum, img["title"]))
        vtype, vid = gen_video(img.get("video_prompt", img["title"]))
        videos.append({
            "scene_number": snum,
            "title": img["title"],
            "image_url": img["image_url"],
            "video_url": vid if vtype == "direct" else None,
            "task_id": vid if vtype == "task" else None,
            "status": "done" if vtype == "direct" else "processing",
            "dialogue": img["dialogue"],
            "duration": img["duration"]
        })
        print("    -> %s" % ("direct" if vtype == "direct" else ("task:" + str(vid)[:20] if vtype == "task" else "FAILED")))
        time.sleep(5)
    return videos

# ========== Step 5: Poll videos ==========
def poll_videos(videos, max_rounds=15, wait=60):
    print("[Step 5] Polling for video completion...")
    for round_num in range(max_rounds):
        pending = [v for v in videos if v["status"] == "processing" and v.get("task_id")]
        if not pending:
            break
        print("  Round %d: %d pending..." % (round_num + 1, len(pending)))
        for v in pending:
            status, url = check_video(v["task_id"])
            if url:
                v["video_url"] = url
                v["status"] = "done"
                print("    Scene %d: COMPLETED" % v["scene_number"])
            time.sleep(2)
        if pending:
            time.sleep(wait)

# ========== Step 6: Synthesize ==========
def synthesize_video(videos, output_path):
    print("[Step 6] Synthesizing final video...")
    tmp_dir = "/tmp/manga_segments"
    os.makedirs(tmp_dir, exist_ok=True)
    
    segments = []
    for v in videos:
        if v["status"] != "done" or not v.get("video_url"):
            continue
        seg_path = "%s/scene_%02d.mp4" % (tmp_dir, v["scene_number"])
        try:
            size = download_file(v["video_url"], seg_path)
            if size > 1000:
                segments.append((seg_path, v))
                print("  Downloaded scene %d: %d bytes" % (v["scene_number"], size))
        except Exception as e:
            print("  Failed scene %d: %s" % (v["scene_number"], e))
    
    if not segments:
        print("No segments!")
        return None
    
    # Concatenate
    concat_file = "%s/concat.txt" % tmp_dir
    with open(concat_file, "w") as f:
        for path, v in segments:
            f.write("file '%s'\n" % path)
    
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
           "-c", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", output_path]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0 and os.path.exists(output_path):
        print("Final video: %s (%d bytes)" % (output_path, os.path.getsize(output_path)))
        return output_path
    else:
        print("FFmpeg error: %s" % result.stderr[:300])
        return None

# ========== Main ==========
def run_pipeline():
    print("=" * 60)
    print("MANGA GENERATION PIPELINE v2")
    print("=" * 60)
    
    characters = generate_character_sheets()
    storyboard = generate_storyboard(characters)
    images = generate_scene_images(storyboard, characters)
    videos = generate_scene_videos(images)
    poll_videos(videos)
    
    final_path = "/tmp/manga_final.mp4"
    result = synthesize_video(videos, final_path)
    
    if result:
        import shutil
        static_path = "/root/portal/static/videos/manga_complete.mp4"
        os.makedirs(os.path.dirname(static_path), exist_ok=True)
        shutil.copy2(result, static_path)
        print("Saved: %s" % static_path)
    
    done = len([v for v in videos if v["status"] == "done"])
    print("\nDONE: %d/%d videos, final=%s" % (done, len(videos), "OK" if result else "FAILED"))
    return result

if __name__ == "__main__":
    run_pipeline()
