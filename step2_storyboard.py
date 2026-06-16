"""
Manga Pipeline Step 2: Storyboard Generation (small batch)
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
    if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","platform","video","image"]):
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
    result = call("/chat/completions", {"model": "agnes-2.0-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens})
    return result.get("choices", [{}])[0].get("message", {}).get("content", "")

NOVEL = open("/root/portal/novel_doupo.txt").read()

print("=== Step 2: Storyboard Generation ===")

# Generate storyboard in 3 batches to avoid truncation
ALL_SCENES = []

# Batch 1: Scenes 1-3
print("\n[Batch 1] Scenes 1-3...")
p1 = """You are a professional manga director. Based on this novel excerpt, generate detailed storyboard for scenes 1-3.

Novel (Chapter 1: Fallen Genius):
%s

Style: anime manga. Each scene 5-8 seconds. Camera variety: close-up, medium, wide, pan.

Output JSON only (no other text):
{"scenes": [{"scene_number": 1, "title": "Scene title", "camera": "close-up/medium/wide/pan", "mood": "atmosphere", "action": "detailed action description in English, 80 words max", "dialogue": "dialogue in Chinese", "speaker": "character name", "image_prompt": "full English image generation prompt including character appearance, clothing, scene, lighting, atmosphere, must match: Xiao Yan has black hair/black eyes/gray robes, Xiao Xun'er has long black hair/violet eyes/purple dress", "video_prompt": "English video prompt describing motion and camera movement"}, ...]}

Generate exactly 3 scenes (scene_number 1, 2, 3). Keep JSON compact.""" % NOVEL[:2000]

content1 = chat(p1, max_tokens=3000)
print("Response: %s..." % content1[:200])
try:
    start = content1.find('{')
    end = content1.rfind('}') + 1
    if start >= 0 and end > start:
        data = json.loads(content1[start:end])
        scenes = data.get("scenes", [])
        ALL_SCENES.extend(scenes)
        print("  Got %d scenes" % len(scenes))
except Exception as e:
    print("  Parse error: %s" % e)

time.sleep(2)

# Batch 2: Scenes 4-6
print("\n[Batch 2] Scenes 4-6...")
p2 = """Continue the manga storyboard from the same novel. Generate scenes 4-6.

Novel context: After Xiao Yan's embarrassing test result (Level 3), the crowd mocks him. Then Xiao Xun'er steps up and achieves Level 9, shocking everyone. Xiao Ning (arrogant cousin) mocks Xiao Yan. Finally, Xiao Xun'er comforts Xiao Yan as they walk home at sunset.

Output JSON only:
{"scenes": [{"scene_number": 4, "title": "...", "camera": "...", "mood": "...", "action": "...", "dialogue": "...", "speaker": "...", "image_prompt": "...", "video_prompt": "..."}, ...]}

Generate exactly 3 scenes (scene_number 4, 5, 6). Character consistency: Xiao Yan (black hair, gray robes), Xiao Xun'er (long black hair, violet eyes, purple dress), Xiao Ning (brown hair, blue robes, arrogant)."""

content2 = chat(p2, max_tokens=3000)
print("Response: %s..." % content2[:200])
try:
    start = content2.find('{')
    end = content2.rfind('}') + 1
    if start >= 0 and end > start:
        data = json.loads(content2[start:end])
        scenes = data.get("scenes", [])
        ALL_SCENES.extend(scenes)
        print("  Got %d scenes" % len(scenes))
except Exception as e:
    print("  Parse error: %s" % e)

time.sleep(2)

# Batch 3: Scenes 7-8
print("\n[Batch 3] Scenes 7-8...")
p3 = """Continue the manga storyboard. Generate the final 2 scenes (7-8).

Scene 7: Xiao Xun'er catches up to Xiao Yan, expresses concern. "Yan ge, are you okay?" Gentle moment, warm lighting.
Scene 8: They walk home together at sunset. Flashback montage of Xiao Yan's training from age 4-11. Hopeful ending.

Output JSON only:
{"scenes": [{"scene_number": 7, "title": "...", "camera": "...", "mood": "...", "action": "...", "dialogue": "...", "speaker": "...", "image_prompt": "...", "video_prompt": "..."}, {"scene_number": 8, "title": "...", "camera": "...", "mood": "...", "action": "...", "dialogue": "...", "speaker": "...", "image_prompt": "...", "video_prompt": "..."}]}

Character consistency: Xiao Yan (black hair, gray robes), Xiao Xun'er (long black hair, violet eyes, purple dress)."""

content3 = chat(p3, max_tokens=2000)
print("Response: %s..." % content3[:200])
try:
    start = content3.find('{')
    end = content3.rfind('}') + 1
    if start >= 0 and end > start:
        data = json.loads(content3[start:end])
        scenes = data.get("scenes", [])
        ALL_SCENES.extend(scenes)
        print("  Got %d scenes" % len(scenes))
except Exception as e:
    print("  Parse error: %s" % e)

print("\nTotal scenes: %d" % len(ALL_SCENES))
for s in ALL_SCENES:
    print("  Scene %d: %s [%s] %s" % (s.get("scene_number", "?"), s.get("title", "?"), s.get("camera", "?"), s.get("dialogue", "")[:40]))

# Save to DB
conn = sqlite3.connect("/root/portal/data/portal.db")
# Update existing scenes with new storyboard data
for s in ALL_SCENES:
    snum = s.get("scene_number", 0)
    conn.execute("""UPDATE manga_scenes SET 
        title=?, description=?, dialogue=?, image_prompt=? 
        WHERE project_id=2 AND scene_number=?""",
        (s.get("title", ""), "%s %s" % (s.get("camera", ""), s.get("mood", "")),
         s.get("dialogue", ""), s.get("image_prompt", ""), snum))
conn.commit()
conn.close()

# Save to file for next step
with open("/tmp/storyboard.json", "w") as f:
    json.dump(ALL_SCENES, f, ensure_ascii=False, indent=2)

print("\nStoryboard saved to /tmp/storyboard.json")
