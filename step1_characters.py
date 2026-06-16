"""
Manga Pipeline Step 1: Character Design
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

NOVEL = open("/root/portal/novel_doupo.txt").read() if os.path.exists("/root/portal/novel_doupo.txt") else ""

# Step 1: Generate character sheets
def gen_char_sheet(name, appearance, role):
    prompt = "anime manga style character reference sheet, full body portrait, %s, white background, clean line art, detailed face, expressive eyes, highly detailed, vibrant colors" % appearance
    result = call("/images/generations", {"model": "agnes-image-2.1-flash", "prompt": prompt, "size": "1024x1024"})
    url = find_url(result)
    print("  %s: %s" % (name, url[:60] if url else "FAILED"))
    return url

print("=== Step 1: Character Design ===")

CHARACTERS = [
    {"name": "萧炎", "role": "主角", "gender": "男", "age": 15,
     "appearance": "handsome young man, black hair flowing, black eyes, determined expression, lean build, gray martial arts robes, black belt, long sword on back, ancient Chinese wuxia style"},
    {"name": "萧薰儿", "role": "女主角", "gender": "女", "age": 14,
     "appearance": "beautiful young girl, long flowing black hair to waist, violet eyes, fair skin, petite build, elegant purple dress with golden embroidery, white stockings, jade bracelet, gentle expression"},
    {"name": "萧宁", "role": "反派", "gender": "男", "age": 16,
     "appearance": "handsome young man, brown hair, brown eyes, tall strong build, arrogant expression, blue martial arts robes with silver trim, silver belt, jade pendant"},
]

char_sheets = {}
for c in CHARACTERS:
    print("Generating %s..." % c["name"])
    url = gen_char_sheet(c["name"], c["appearance"], c["role"])
    char_sheets[c["name"]] = {"url": url, "desc": c["appearance"]}
    time.sleep(2)

# Save to DB
conn = sqlite3.connect("/root/portal/data/portal.db")
for name, data in char_sheets.items():
    conn.execute("UPDATE manga_characters SET reference_url=? WHERE project_id=2 AND name=?", (data["url"], name))
conn.commit()
conn.close()

print("\nCharacter sheets generated:")
for name, data in char_sheets.items():
    print("  %s: %s" % (name, "OK" if data["url"] else "FAILED"))
