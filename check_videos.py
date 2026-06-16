import json, urllib.request, time, sqlite3

AGNES_API_KEY = "sk-gScQfsupCor8Cp6O7pHS8IhxdbttANFlgLNQ3plVNWSToZ8R"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

def check_and_update_videos():
    conn = sqlite3.connect("/root/portal/data/portal.db")
    scenes = conn.execute("""
        SELECT ms.id, ms.scene_number, ms.title, ms.video_task_id, ms.status, ms.video_url
        FROM manga_scenes ms
        JOIN manga_projects mp ON ms.project_id = mp.id
        WHERE mp.title LIKE '%doupo%' AND ms.video_task_id IS NOT NULL
        ORDER BY ms.scene_number
    """).fetchall()
    
    print("Checking %d scenes with video tasks..." % len(scenes))
    
    for scene_id, scene_num, title, task_id, status, video_url in scenes:
        print("\n  Scene %d '%s' (current: %s)" % (scene_num, title, status))
        print("    Task ID: %s" % task_id)
        
        try:
            req = urllib.request.Request(
                AGNES_BASE_URL + "/videos/" + task_id,
                headers={"Authorization": "Bearer " + AGNES_API_KEY}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                print("    Keys: %s" % list(result.keys()))
                print("    Response: %s" % json.dumps(result, ensure_ascii=False)[:600])
                
                new_status = result.get("status", "processing")
                vid_url = None
                
                # Try all possible URL locations
                for key in ["url", "video_url", "videoUrl", "download_url"]:
                    if result.get(key):
                        vid_url = result[key]
                        break
                
                if not vid_url and "data" in result:
                    d = result["data"]
                    if isinstance(d, str):
                        vid_url = d
                    elif isinstance(d, dict):
                        for key in ["url", "video_url", "videoUrl"]:
                            if d.get(key):
                                vid_url = d[key]
                                break
                    elif isinstance(d, list) and d:
                        for item in d:
                            if isinstance(item, str):
                                vid_url = item
                                break
                            elif isinstance(item, dict):
                                for key in ["url", "video_url"]:
                                    if item.get(key):
                                        vid_url = item[key]
                                        break
                
                if not vid_url and "outputs" in result:
                    outs = result["outputs"]
                    if isinstance(outs, list) and outs:
                        for item in outs:
                            if isinstance(item, str):
                                vid_url = item
                            elif isinstance(item, dict):
                                vid_url = item.get("url") or item.get("video_url")
                            if vid_url:
                                break
                
                if not vid_url and "result" in result:
                    r = result["result"]
                    if isinstance(r, str):
                        vid_url = r
                    elif isinstance(r, dict):
                        vid_url = r.get("url") or r.get("video_url")
                
                print("    Status: %s, URL: %s" % (new_status, vid_url[:60] + "..." if vid_url else "None"))
                
                if vid_url:
                    conn.execute("UPDATE manga_scenes SET video_url=?, status='done' WHERE id=?", (vid_url, scene_id))
                    conn.commit()
                    print("    UPDATED!")
                else:
                    conn.execute("UPDATE manga_scenes SET status=? WHERE id=?", (new_status, scene_id))
                    conn.commit()
                    
        except Exception as e:
            print("    Error: %s" % e)
        
        time.sleep(2)
    
    print("\n=== Final Status ===")
    scenes = conn.execute("""
        SELECT ms.scene_number, ms.title, ms.status, 
               CASE WHEN ms.video_url IS NOT NULL THEN 'YES' ELSE 'NO' END as has_url
        FROM manga_scenes ms
        JOIN manga_projects mp ON ms.project_id = mp.id
        WHERE mp.title LIKE '%doupo%'
        ORDER BY ms.scene_number
    """).fetchall()
    
    for s in scenes:
        print("  Scene %d '%s': %s | Video: %s" % (s[0], s[1], s[2], s[3]))
    
    conn.close()

if __name__ == "__main__":
    check_and_update_videos()
