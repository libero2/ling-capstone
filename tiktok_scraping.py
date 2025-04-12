import os
import requests
import shutil
import sqlite3

try:
    import requests
except ImportError:
    os.system('pip install -q requests')
    import requests

print("TikTok Comment Scraper".center(shutil.get_terminal_size().columns))
print('\n')

videoid = input('[?] TikTok link > ')
lang = input('Language (jp, kr, sp):  >')
age_group = input('Age Group (1: Younger, 2: Older): >')

if "vm.tiktok.com" in videoid or "vt.tiktok.com" in videoid:
    videoid = requests.head(videoid, allow_redirects=True, timeout=5).url.split("/")[5].split("?", 1)[0]
else:
    videoid = videoid.split("/")[5].split("?", 1)[0]

t = 0
comm_num = 0

while True:
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'referer': f'https://www.tiktok.com/@x/video/{videoid}',
        }

        response = requests.get(f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={videoid}&count=9999999&cursor={t}", headers=headers)
        response.raise_for_status()

        comments = response.json()["comments"]
        if not comments:
            break

        to_db_post = ['']
        to_db_lang = ['']
        to_db_age = []

        for comment in comments:
            print(comment["text"])
            to_db_post.append(comment["text"])
            to_db_lang.append(lang)
            to_db_age.append(int(age_group))
            comm_num += 1

        database = "tiktok.db"

        statements = [
            """CREATE TABLE IF NOT EXISTS tiktok (
            id INTEGER PRIMARY KEY, 
            post text NOT NULL,
            lang text NOT NULL, 
            age_group INTEGER NOT NULL
            );""",

        ]

        def add_to_db(conn, task):
            sql_statement = """INSERT INTO tiktok(post, lang, age_group)
                               VALUES(?,?,?)"""
            cur = conn.cursor()
            cur.execute(sql_statement, task)
            conn.commit()
            return cur.lastrowid


        with sqlite3.connect("tiktok.db") as conn:

            cursor = conn.cursor()
            for statement in statements:
                cursor.execute(statement)
            conn.commit()

            posts = []
            for x in range(len(to_db_post) - 1):
                posts.append((to_db_post[x], to_db_lang[x], to_db_age[x]))

            for post in posts:
                post = add_to_db(conn, post)
                print(f"Created post with id {id}")

            pass

        t += 50

    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"Error occurred: {e}")
        break

print(f"Total comments scraped: {comm_num}")