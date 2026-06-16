"""
Seed data for Manga/Comic Generation System
"""
import sqlite3

def seed_manga(conn):
    """Seed manga generation system data"""
    count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='manga_projects'").fetchone()[0]
    if count == 0:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS manga_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                novel_text TEXT,
                style TEXT DEFAULT 'anime',
                status TEXT DEFAULT 'draft',
                cover_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS manga_scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                scene_number INTEGER NOT NULL,
                title TEXT,
                description TEXT,
                characters TEXT,
                dialogue TEXT,
                image_prompt TEXT,
                image_url TEXT,
                video_url TEXT,
                video_task_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES manga_projects(id)
            );
            CREATE TABLE IF NOT EXISTS manga_characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                appearance TEXT,
                personality TEXT,
                reference_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES manga_projects(id)
            );
        """)
    
    # Seed sample project
    if conn.execute("SELECT COUNT(*) FROM manga_projects").fetchone()[0] == 0:
        conn.execute("""INSERT INTO manga_projects (title, description, novel_text, style, status) VALUES (?,?,?,?,?)""",[
            "剑影江湖",
            "一部关于江湖恩怨、剑客情仇的武侠小说改编漫剧",
            """第一回：剑出鞘

江南三月，烟雨朦胧。

青石板路上，一袭白衣的少年缓步而行。他背负长剑，面容清秀，眉宇间却带着几分与年龄不符的沧桑。

"十年了……"少年喃喃自语，目光投向远处隐约可见的城池，"师父，弟子回来了。"

这座城，叫做临安。是他十年前被师父带走的地方，也是他一切恩怨的开始。

走入城中，少年径直向城北的"醉仙楼"走去。这座酒楼，是江湖中消息最灵通的地方。

"客官，打尖还是住店？"小二殷勤地迎上来。

"找人。"少年淡淡道，目光扫过酒楼中的人。

角落里，一个灰衣人独酌独饮。灰衣人抬起头，露出一张刀削般棱角分明的脸。

"你终于来了。"灰衣人放下酒杯，"等你很久了，沈惊寒。"

少年瞳孔微缩："你认识我？"

"江湖上谁不认识'白衣剑仙'的传人？"灰衣人冷笑，"不过，你师父已经死了。三年了。"

沈惊寒的手不自觉地握紧了剑柄。

灰衣人站起身，从怀中取出一块令牌，上面刻着一个"杀"字。

"有人要你的命。但我先告诉你——杀你师父的人，就在这临安城中。"

说罢，灰衣人转身消失在雨幕中。""",
            "anime",
            "processing"
        ])
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Seed characters
        conn.executemany("INSERT INTO manga_characters (project_id, name, description, appearance, personality) VALUES (?,?,?,?,?)", [
            (pid, "沈惊寒", "男主角，白衣剑客，师从'白衣剑仙'。十年前被师父带离临安，如今学成归来。背负血海深仇，性格沉稳内敛。", "约20岁，面容清秀，白衣胜雪，背负长剑，眼神深邃", "沉稳内敛，重情重义，剑术高超，内心藏有伤痛"),
            (pid, "灰衣人", "神秘信使，知晓沈惊寒的过去和师父之死的真相。立场不明，亦敌亦友。", "中年男子，灰衣，刀削般棱角分明的脸，眼神锐利", "神秘莫测，言语简洁，深不可测"),
            (pid, "白衣剑仙（回忆）", "沈惊寒的师父，十年前名震江湖的剑客，已去世三年。", "白发老者，仙风骨气，手持长剑", "慈祥和蔼，武功盖世，有未了的心愿"),
        ])
        # Seed scenes
        conn.executemany("INSERT INTO manga_scenes (project_id, scene_number, title, description, characters, dialogue, image_prompt, status) VALUES (?,?,?,?,?,?,?,?)", [
            (pid, 1, "烟雨临安", "江南三月，沈惊寒白衣胜雪走入临安城", "沈惊寒", "（旁白）江南三月，烟雨朦胧。白衣少年缓步而行。", "anime style, young man in white robes walking through ancient Chinese town in rainy spring, misty atmosphere, traditional architecture, cinematic lighting, highly detailed", "done"),
            (pid, 2, "醉仙楼", "沈惊寒走进醉仙楼，与灰衣人对峙", "沈惊寒,灰衣人", "灰衣人：你终于来了。等你很久了，沈惊寒。", "anime style, interior of ancient Chinese tavern, young white-robed man facing gray-robed man at a table, atmospheric lighting, dramatic tension, detailed faces", "done"),
            (pid, 3, "惊天消息", "灰衣人告知师父死讯", "沈惊寒,灰衣人", "灰衣人：你师父已经死了。三年了。", "anime style, close-up of young man's shocked expression, gray-robed man showing a dark token, tavern interior background, dramatic shadows, emotional intensity", "pending"),
            (pid, 4, "令牌", "灰衣人出示杀字令牌", "灰衣人", "灰衣人：有人要你的命。杀你师父的人，就在这临安城中。", "anime style, close-up of a dark token with '杀' character, held by gray-robed hand, dramatic lighting, mysterious atmosphere", "pending"),
            (pid, 5, "雨幕离别", "灰衣人消失在雨幕中", "灰衣人", "（灰衣人转身消失在雨幕中）", "anime style, silhouette of gray-robed man disappearing into rain and mist, dramatic backlighting, ancient Chinese street, melancholic atmosphere", "pending"),
        ])
