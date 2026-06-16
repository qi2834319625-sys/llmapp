"""
Manga Pipeline Step 3: Generate scene images with character consistency
"""
import json, urllib.request, urllib.parse, time, sqlite3, os

k = open("/root/portal/.agnes_key").read().strip()
BASE = "https://apihub.agnes-ai.com/v1"
H = {"Authorization": "Bearer " + k, "Content-Type": "application/json"}

def call(endpoint, data, timeout=120):
    req = urllib.request.Request(BASE + endpoint, headers=H, data=json.dumps(data).encode())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def find_url(obj, depth=0):
    if depth > 6: return None
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","platform","image"]):
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

# Load storyboard
with open("/tmp/storyboard.json") as f:
    scenes = json.load(f)

print("=== Step 3: Generate Scene Images ===")
print("Total scenes: %d" % len(scenes))

# Character reference prompts for consistency
CHAR_REFS = {
    "Xiao Yan": "young male, black hair, black eyes, gray martial arts robes, determined expression, handsome face",
    "Xiao Xun'er": "young female, long black hair, violet eyes, purple dress with gold embroidery, beautiful gentle face",
    "Xiao Ning": "young male, brown hair, blue robes, arrogant expression",
    "Xiao Yaner": "young female, long black hair, violet eyes, purple dress with gold embroidery, beautiful gentle face",
}

results = []
for scene in scenes:
    snum = scene.get("scene_number", 0)
    title = scene.get("title", "")
    prompt = scene.get("image_prompt", "")
    
    # Add character consistency
    for eng, desc in CHAR_REFS.items():
        if eng in prompt or eng.lower() in title.lower():
            prompt = desc + ". " + prompt
            break
    
    # Ensure consistent style prefix
    full_prompt = "anime manga style, high quality illustration, consistent character design, cinematic composition, " + prompt
    
    print("\n  Scene %d: %s..." % (snum, title))
    print("    Prompt: %s..." % full_prompt[:100])
    
    try:
        result = call("/images/generations", {
            "model": "agnes-image-2.1-flash",
            "prompt": full_prompt[:500],
            "size": "1024x768"
        })
        url = find_url(result)
        if url:
            print("    Image: %s" % url[:60])
        else:
            print("    FAILED: %s" % str(result)[:100])
    except Exception as e:
        url = None
        print("    Error: %s" % e)
    
    results.append({
        "scene_number": snum,
        "title": title,
        "image_url": url,
        "dialogue": scene.get("dialogue", ""),
        "video_prompt": scene.get("video_prompt", ""),
        "camera": scene.get("camera", ""),
        "mood": scene.get("mood", "")
    })
    
    time.sleep(3)

# Save to DB
conn = sqlite3.connect("/root/portal/data/portal.db")
for r in results:
    conn.execute("""UPDATE manga_scenes SET image_url=?, description=?, dialogue=? WHERE project_id=2 AND scene_number=?""",
        (r["image_url"], "%s %s" % (r["camera"], r["mood"]), r["dialogue"], r["scene_number"]))
conn.commit()
conn.close()

# Save results for next step
with open("/tmp/scene_images.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

ok = len([r for r in results if r["image_url"]])
print("\n=== Images: %d/%d generated ===" % (ok, len(results)))
