"""
Seed demo manga project with popular novel content
"""
import sqlite3, json, urllib.request, urllib.parse, time

AGNES_API_KEY = "sk-gScQfsupCor8Cp6O7pHS8IhxdbttANFlgLNQ3plVNWSToZ8R"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

NOVEL_TEXT = """第一章：陨落的天才

"斗之气，三段！"

测验碑之上，闪亮得甚至有些刺眼的五个大字，让得广场上的少年面无表情，唇角有着一抹自嘲，紧握的手掌，因为大力，而导致略微尖锐的指甲深深的刺进了掌心之中，带来一阵阵钻心的疼痛…

"萧炎，斗之气，三段！级别：低级！"测验碑之旁，一位中年男子，看了一眼碑上所显示出来的信息，语气漠然的将之公布了出来…

中年男子话刚刚脱口，便是在周围引起了一阵窃窃私语，一些人看向少年的目光中，充满了同情与惋惜。

"三段？嘿嘿，果然不出我所料，这个"天才"这一年又是在原地踏步！"

"哎，这废物真是把家族的脸都给丢光了…"

"要我说，族长就应该把他赶出家族，免得继续丢人现眼！"

周围传来的不屑议论声，令得少年的拳头越握越紧，尖锐的指甲刺进掌心，鲜血顺着指缝滴落。

少年缓缓抬起头来，露出一张有些清秀的年轻脸庞，漆黑的眸子木然的在周围那些嘲讽的面庞上扫过，最后停留在了不远处，一位正幸灾乐祸的蓝衣少年身上。

"萧宁…"少年喃喃了一声，嘴角牵起一抹自嘲的弧度。

"下一个，萧薰儿！"

随着测验师的声音响起，广场上的议论声戛然而止，所有人的目光都投向了人群前方，一位身着紫色衣裙的少女身上。

少女年龄不过十四左右，然而那已经初具规模的娇躯，却是让得在场不少男子暗中咽了一口口水。

少女行到测验碑之前，小手伸出，镶着黑金丝的紫袖滑落而下，露出一截雪白娇嫩的皓腕，然后轻触着测验碑…

微微沉静，测验碑之上，刺眼的光芒再次绽放。

"斗之气：九段！级别：高级！"

"九段！竟然九段！萧家年轻一辈中，恐怕只有萧炎哥哥当年能与之相比了吧…"

"嘘，别提那个废物了…"

少女听着周围的赞叹声，却并未表现出太多的喜悦，反而将目光投向了人群后方，那个孤独站立的少年身上。

"炎哥哥…"少女心中轻叹了一声。

少年名叫萧炎，乌坦城萧家历史上空前绝后的斗气修炼天才。四岁就开始修炼斗之气，十岁拥有了九段斗之气，十一岁突破十段斗之气，成功凝聚斗之气旋，成为家族百年之内最年轻的斗者！

然而，在其十二岁那年，他却"丧失"了修炼能力，只拥有三段斗之气。整整三年时间，他的斗之气始终停留在三段，再也无法进步。

从天才跌落成废物，这种落差，让得少年受尽了冷嘲热讽。

"下一个，萧宁！"

蓝衣少年萧宁大摇大摆的走到测验碑前，手掌触碑，光芒闪耀。

"斗之气：七段！级别：中级！"

萧宁收回手掌，瞟了一眼旁边的萧炎，嘴角掀起一抹嘲讽。

"三段…嘿嘿，萧炎，你现在还有什么资格让我重视？"

萧炎面无表情，转身向广场外走去。

"炎哥哥。"一道清雅的声音在身后响起，萧炎脚步一顿，转过头来，望着那快步跑来的紫裙少女，脸上终于露出了一丝笑容。

"薰儿。"

"炎哥哥，你没事吧？"少女跑到近前，清澈的眸子中满是担忧。

"没事。"萧炎笑了笑，伸手揉了揉少女的脑袋，"走吧，回家。"

夕阳西下，两道身影在落日余晖中渐行渐远。"""

SCENES = [
    {
        "scene_number": 1,
        "title": "测验广场",
        "description": "萧炎站在测验碑前，碑上显示'斗之气，三段'，周围传来嘲讽声",
        "characters": "萧炎,测验师,围观群众",
        "dialogue": "萧炎，斗之气，三段！级别：低级！",
        "image_prompt": "anime manga style, young man standing in front of a glowing stone monument in an ancient Chinese martial arts plaza, the monument shows glowing text 'Level 3', crowd of people watching and whispering, dramatic lighting, the young man has a pained expression, wearing traditional Chinese martial arts robes, cinematic composition, highly detailed"
    },
    {
        "scene_number": 2,
        "title": "嘲讽与屈辱",
        "description": "周围人的嘲讽声此起彼伏，萧炎紧握拳头，指甲刺入掌心",
        "characters": "萧炎,萧宁,围观者",
        "dialogue": "三段？嘿嘿，果然不出我所料，这个'天才'这一年又是在原地踏步！",
        "image_prompt": "anime manga style, close-up of a young man's clenched fist with blood dripping from his palm, surrounded by sneering faces in the background, dark moody lighting, tears of blood, dramatic shadows, emotional intensity, Chinese martial arts setting"
    },
    {
        "scene_number": 3,
        "title": "萧薰儿登场",
        "description": "紫裙少女萧薰儿走向测验碑，全场寂静，她轻触碑面",
        "characters": "萧薰儿,萧炎",
        "dialogue": "下一个，萧薰儿！",
        "image_prompt": "anime manga style, beautiful young girl in purple dress walking confidently toward a glowing monument in a martial arts plaza, all eyes on her, wind blowing her hair, elegant and graceful, golden light around her, cinematic wide shot, highly detailed"
    },
    {
        "scene_number": 4,
        "title": "天才少女",
        "description": "测验碑绽放耀眼光芒，显示'斗之气：九段'，全场震惊",
        "characters": "萧薰儿,围观群众",
        "dialogue": "斗之气：九段！级别：高级！",
        "image_prompt": "anime manga style, brilliant golden light erupting from a stone monument, a beautiful purple-robed girl standing before it with her hand touching the surface, the monument displays 'Level 9' in glowing characters, crowd gasping in amazement, dramatic light rays, magical atmosphere, cinematic"
    },
    {
        "scene_number": 5,
        "title": "萧宁的挑衅",
        "description": "萧宁测试出七段斗之气，得意洋洋地嘲讽萧炎",
        "characters": "萧宁,萧炎",
        "dialogue": "萧炎，你现在还有什么资格让我重视？",
        "image_prompt": "anime manga style, a smug young man in blue robes pointing and laughing at another young man, the target young man standing alone with a cold expression, tension between them, martial arts plaza background, dramatic lighting, confrontation scene"
    },
    {
        "scene_number": 6,
        "title": "薰儿的关怀",
        "description": "萧薰儿追上萧炎，清澈的眸子中满是担忧，萧炎露出笑容",
        "characters": "萧炎,萧薰儿",
        "dialogue": "炎哥哥，你没事吧？",
        "image_prompt": "anime manga style, a beautiful purple-robed girl looking up at a young man with concern in her eyes, the young man smiling gently and patting her head, warm sunset lighting, emotional and tender moment, cherry blossoms falling, romantic atmosphere"
    },
    {
        "scene_number": 7,
        "title": "夕阳同行",
        "description": "夕阳西下，萧炎和萧薰儿并肩走在回家的路上，影子被拉得很长",
        "characters": "萧炎,萧薰儿",
        "dialogue": "（旁白）从天才跌落成废物，这种落差，让得少年受尽了冷嘲热讽。",
        "image_prompt": "anime manga style, two young figures walking side by side on a path toward the sunset, long shadows stretching behind them, warm orange and purple sky, ancient Chinese town in the background, melancholic yet hopeful atmosphere, beautiful landscape, cinematic wide shot"
    },
    {
        "scene_number": 8,
        "title": "回忆·天才少年",
        "description": "闪回画面：四岁开始修炼，十岁九段斗之气，十一岁成为最年轻斗者",
        "characters": "萧炎(少年)",
        "dialogue": "（旁白）萧炎，萧家历史上空前绝后的斗气修炼天才。",
        "image_prompt": "anime manga style, montage of a young boy training in martial arts, progressing from age 4 to 11, each scene showing him growing stronger, golden aura surrounding him, family members cheering, dramatic training sequences, time-lapse effect, inspirational and epic"
    },
]

CHARACTERS = [
    ("萧炎", "男主角，萧家天才少年，十二岁时突然丧失修炼能力，从天才跌落成废物。性格坚韧不屈，内心强大。", "约15岁，面容清秀，黑发黑眸，身穿灰色布衣，眼神深邃而坚毅", "坚韧不屈，重情重义，内心强大，不向命运低头"),
    ("萧薰儿", "萧家养女，天才少女，斗之气九段。对萧炎始终不离不弃，温柔体贴。", "约14岁，紫裙，黑发如瀑，肌肤雪白，眸子清澈如秋水", "温柔善良，聪慧过人，对萧炎情深意重"),
    ("萧宁", "萧家子弟，嫉妒萧炎曾经的天才地位，经常嘲讽萧炎。", "约16岁，蓝衣，面容英俊但神情傲慢", "傲慢自负，嫉妒心强，欺软怕硬"),
    ("测验师", "萧家测验广场的负责人员，负责公布测验结果。", "中年男子，面容严肃，身穿萧家长老服饰", "公正无私，冷漠客观"),
]


def generate_image(prompt, retries=3):
    """Generate image using Agnes AI"""
    for attempt in range(retries):
        try:
            data = json.dumps({
                "model": "agnes-image-2.1-flash",
                "prompt": prompt[:500],
                "size": "1024x768"
            }).encode()
            
            req = urllib.request.Request(
                f"{AGNES_BASE_URL}/images/generations",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                data=data
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode())
                url = result.get("data", [{}])[0].get("url", "")
                if url:
                    return url
        except Exception as e:
            print(f"  Image gen attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
    return ""


def seed_demo_project():
    conn = sqlite3.connect("/root/portal/data/portal.db")
    
    # Check if demo project exists
    existing = conn.execute("SELECT id FROM manga_projects WHERE title = '斗破苍穹：斗之气篇'").fetchone()
    if existing:
        print("Demo project already exists, updating scenes...")
        pid = existing[0]
        # Clear old scenes
        conn.execute("DELETE FROM manga_scenes WHERE project_id=?", (pid,))
        conn.execute("DELETE FROM manga_characters WHERE project_id=?", (pid,))
    else:
        # Create project
        conn.execute("""INSERT INTO manga_projects (title, description, novel_text, style, status) VALUES (?,?,?,?,?)""", [
            "斗破苍穹：斗之气篇",
            "《斗破苍穹》是天蚕土豆创作的经典玄幻小说。讲述天才少年萧炎从废物逆袭的故事。本漫剧改编自小说第一章《陨落的天才》。",
            NOVEL_TEXT,
            "anime",
            "processing"
        ])
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        print(f"Created demo project ID: {pid}")
    
    # Add characters
    for name, desc, appear, pers in CHARACTERS:
        conn.execute("INSERT INTO manga_characters (project_id, name, description, appearance, personality) VALUES (?,?,?,?,?)",
                     (pid, name, desc, appear, pers))
    print(f"Added {len(CHARACTERS)} characters")
    
    # Add scenes with image generation
    for i, scene in enumerate(SCENES):
        print(f"Generating image for scene {scene['scene_number']}: {scene['title']}...")
        image_url = generate_image(scene["image_prompt"])
        status = "image_done" if image_url else "pending"
        if image_url:
            print(f"  ✓ Image generated: {image_url[:60]}...")
        else:
            print(f"  ✗ Image generation failed, will be pending")
        
        conn.execute("""INSERT INTO manga_scenes 
            (project_id, scene_number, title, description, characters, dialogue, image_prompt, image_url, status) 
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (pid, scene["scene_number"], scene["title"], scene["description"],
             scene["characters"], scene["dialogue"], scene["image_prompt"], image_url, status))
        time.sleep(2)  # Rate limiting
    
    conn.commit()
    conn.close()
    print("Demo project seeded successfully!")


if __name__ == "__main__":
    seed_demo_project()
