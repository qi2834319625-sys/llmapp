import json, urllib.request, time

k = open(".agnes_key").read().strip()
H = {"Authorization": "Bearer " + k, "Content-Type": "application/json"}

# Test 1: Submit video
print("Submitting video task...")
data = json.dumps({
    "model": "agnes-video-v2.0",
    "prompt": "anime manga style, smooth camera movement, a young man walking in ancient Chinese town, cinematic",
    "num_frames": 81,
    "frame_rate": 24
}).encode()

req = urllib.request.Request("https://apihub.agnes-ai.com/v1/videos", headers=H, data=data)
try:
    resp = urllib.request.urlopen(req, timeout=180)
    result = json.loads(resp.read().decode())
    print("Submit OK:")
    print(json.dumps(result, indent=2)[:600])
    
    tid = result.get("task_id") or result.get("id")
    if tid and not tid.startswith("task_"):
        tid = "task_" + tid
    
    print("\nTask ID: %s" % tid)
    
    # Poll after 10 seconds
    print("\nPolling in 10 seconds...")
    time.sleep(10)
    
    for i in range(5):
        try:
            req2 = urllib.request.Request("https://apihub.agnes-ai.com/v1/videos/" + tid, headers={"Authorization": "Bearer " + k})
            resp2 = urllib.request.urlopen(req2, timeout=30)
            r2 = json.loads(resp2.read().decode())
            status = r2.get("status", "?")
            print("Poll %d: status=%s" % (i+1, status))
            
            # Check for URL
            def find(obj, d=0):
                if d > 6: return None
                if isinstance(obj, str) and obj.startswith("http") and any(x in obj.lower() for x in ["storage","output","video","mp4"]):
                    return obj
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, str) and v.startswith("http"): return v
                        r = find(v, d+1)
                        if r: return r
                if isinstance(obj, list):
                    for item in obj:
                        r = find(item, d+1)
                        if r: return r
                return None
            
            url = find(r2)
            if url:
                print("VIDEO URL: %s" % url)
                break
                
        except Exception as e:
            print("Poll %d error: %s" % (i+1, e))
        
        time.sleep(30)
        
except Exception as e:
    print("Submit error: %s" % e)
