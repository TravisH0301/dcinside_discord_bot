from bs4 import BeautifulSoup
import requests, re
import sqlite3, time
from sqlite3 import Error
import pandas as pd
from multiprocessing import Process, Manager
from threading import Thread, Timer, Event
import os, discord, asyncio
from random import randint

# return gallery name and post information
def check_gallery(gallery):
    global gall_dict

    # convert gallery from Eng to Kor & define minor variable
    if gallery in gall_dict.keys():
        minor = gall_dict[gallery][1]
        gallery = gall_dict[gallery][0]
    else: 
        msg = "갤러리 이름을 확인해주세요."
        return msg
    
    if minor == 0:
        url = 'http://gall.dcinside.com/board/lists/?id={}'.format(gallery)
    elif minor == 1:
        url = 'http://gall.dcinside.com/mgallery/board/lists/?id={}'.format(gallery)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers = headers)
        html = response.text  # .text returns decoded string & .content returns bytes

        # create bs4 object using the html content
        soup = BeautifulSoup(html, 'html.parser')

        # gallery name
        gallery_name = soup.title.string
        # post information
        post_content = soup.find_all("tr", attrs={"class" : "ub-content us-post"})
        # define lists for post information
        list_number=[]; list_type=[]; list_title=[]; list_num_comment=[]; list_writer=[]; list_date=[]; list_view=[]; list_reco=[]
        # separate gallery with 말머리 and gallery without 말머리
        newline_count = post_content[0].text.count("\n")
        # gallery with 말머리
        if newline_count == 11:
            for i in post_content:
                post = i.text
                post_number = re.findall(r"^\n(.*?)\n", post)[0]
                list_number.append(int(post_number))
                post_type = re.findall(r"^\n.*?\n(.*?)\n", post)[0]
                list_type.append(post_type)
                post_title = re.findall(r"^\n.*?\n.*?\n\n(.*?)\n", post)[0]
                list_title.append(post_title)
                if re.findall(r"^\n.*?\n.*?\n\n.*?\n\[(.*?)\]", post):
                    post_num_comment = re.findall(r"^\n.*?\n.*?\n\n.*?\n\[(.*?)\]", post)[0]
                    list_num_comment.append(post_num_comment)
                else:
                    post_num_comment = 0
                    list_num_comment.append(post_num_comment)
                post_writer = re.findall(r"^\n.*?\n.*?\n\n.*?\n.*?\n\n(.*?)\n", post)[0]
                list_writer.append(post_writer)
                post_date = re.findall(r"^\n.*?\n.*?\n\n.*?\n.*?\n\n.*?\n(.*?)\n", post)[0]
                list_date.append(post_date)
                post_view = re.findall(r"^\n.*?\n.*?\n\n.*?\n.*?\n\n.*?\n.*?\n(.*?)\n", post)[0]
                list_view.append(post_view)
                post_reco = re.findall(r"^\n.*?\n.*?\n\n.*?\n.*?\n\n.*?\n.*?\n.*?\n(.*?)\n", post)[0]
                list_reco.append(post_reco)
   
            return gallery_name, list_number, list_type, list_title, list_num_comment, list_writer, list_date, list_view, list_reco

        elif newline_count == 10:
            for i in post_content:
                post = i.text
                post_number = re.findall(r"^\n(.*?)\n", post)[0]
                if post_number.isdigit():
                    list_number.append(int(post_number))
                    post_type = ""
                else:
                    list_number.append(0)
                    post_type = "공지"
                list_type.append(post_type)
                post_title = re.findall(r"^\n.*?\n\n(.*?)\n", post)[0]
                list_title.append(post_title)
                if re.findall(r"^\n.*?\n\n.*?\n\[(.*?)\]", post):
                    post_num_comment = re.findall(r"^\n.*?\n\n.*?\n\[(.*?)\]", post)[0]
                    list_num_comment.append(post_num_comment)
                else:
                    post_num_comment = 0
                    list_num_comment.append(post_num_comment)
                post_writer = re.findall(r"^\n.*?\n\n.*?\n.*?\n\n(.*?)\n", post)[0]
                list_writer.append(post_writer)
                post_date = re.findall(r"^\n.*?\n\n.*?\n.*?\n\n.*?\n(.*?)\n", post)[0]
                list_date.append(post_date)
                post_view = re.findall(r"^\n.*?\n\n.*?\n.*?\n\n.*?\n.*?\n(.*?)\n", post)[0]
                list_view.append(post_view)
                post_reco = re.findall(r"^\n.*?\n\n.*?\n.*?\n\n.*?\n.*?\n.*?\n(.*?)\n", post)[0]
                list_reco.append(post_reco)
   
            return gallery_name, list_number, list_type, list_title, list_num_comment, list_writer, list_date, list_view, list_reco
    except:
        pass
        # print("Error: 갤러리이름과 마이너 변수를 확인해주세요.")

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        print("Error: 데이터베이스 연결을 확인해주세요.")
    return conn

def create_table_sql(gallery_name):
    sql = """ CREATE TABLE IF NOT EXISTS {} (
                id integer PRIMARY KEY,
                post_number text,
                post_type text,
                post_title text,
                post_num_comment text,
                post_writer text,
                post_date text,
                post_view text,
                post_reco text
                ); """.format(gallery_name)
    return sql

def create_table_sql2(gallery_name):
    sql = """ CREATE TABLE IF NOT EXISTS {} (
                id integer PRIMARY KEY,
                post_number integer,
                post_title text,
                post_writer text,
                post_date text
                ); """.format(gallery_name)
    return sql

def create_table(conn, script):
    try:
        cur = conn.cursor()
        cur.execute(script)
        conn.commit()
    except:
        print("Error: 데이터베이스 연결을 확인해주세요.")

def create_instance(conn, gallery_name, instance_attrs):
    sql = '''INSERT INTO {}(post_number,post_type,post_title,post_num_comment,post_writer,post_date,post_view,post_reco)
            VALUES(?,?,?,?,?,?,?,?)'''.format(gallery_name)
    cur = conn.cursor()
    cur.execute(sql, instance_attrs)
    conn.commit()
    return cur.lastrowid

def create_instance2(conn, gallery_name, instance_attrs):
    sql = '''INSERT INTO {}(post_number,post_title,post_writer,post_date)
            VALUES(?,?,?,?)'''.format(gallery_name)
    cur = conn.cursor()
    cur.execute(sql, instance_attrs)
    conn.commit()
    return cur.lastrowid

def delete_instance(conn, gallery_name):
    sql = 'DELETE FROM {}'.format(gallery_name)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def show_gallery_list(conn):
    cur = conn.cursor()
    cur.execute('SELECT name from sqlite_master where type= "table"')
    gall_list = cur.fetchall()
    return gall_list

def drop_all(conn):
    cur = conn.cursor()
    cur.execute('SELECT name from sqlite_master where type= "table"')
    gall_list = cur.fetchall()
    for gall in gall_list:
        script = "DROP TABLE " + gall[0]
        cur.execute(script)

def add_gallery(gallery_name_Kor):
    global gallery_list
    gallery_list.append(gallery_name_Kor)

def remove_gallery(gallery_name_Kor):
    global gallery_list
    gallery_list.remove(gallery_name_Kor)

def new_content(gallery_name_Kor):
    global conn
    # web-crawl gallery
    """gallery contains gallery_name and lists of post_number, post_type, post_title,
                                                  post_num_comment,post_writer,post_date,
                                                  post_view,post_reco"""
    gallery = check_gallery(gallery_name_Kor)

    if gallery == "갤러리 이름을 확인해주세요.":
        msg = "갤러리 이름을 확인해주세요."
        return msg

    create_table(conn, create_table_sql(gallery_name_Kor))

    # load table
    df1 = pd.read_sql_query("SELECT * from {}".format(gallery_name_Kor), conn)
    df1.drop("id", axis=1, inplace=True)
    # print(df1.shape)

    # delete old instances
    delete_instance(conn, gallery_name_Kor)

    # update table
    try:
        for i in range(len(gallery[1])):
                script = (gallery[1][i],gallery[2][i],gallery[3][i],gallery[4][i],gallery[5][i],gallery[6][i],gallery[7][i],gallery[8][i])
                create_instance(conn, gallery_name_Kor, script)
                i += 1
    except:
        pass

    # return new content
    df2 = pd.read_sql_query("SELECT * from {}".format(gallery_name_Kor), conn)
    df2.drop("id", axis=1, inplace=True)
    df3 = pd.concat([df1,df2])
    df3 = df3.drop_duplicates(subset=["post_number"], keep=False)
    df3_announce = df3.loc[df3.post_type == "공지"]
    df3_content = df3.loc[df3.post_type != "공지"]
    df3_content = df3_content.sort_values(by=["post_number"], ascending=False)
    df3 = pd.concat([df3_announce, df3_content])
    if df1.empty == 0:
        df3 = df3.loc[df3.post_number > max(df1.post_number.tolist())]
    df3 = df3.loc[:,["post_number","post_title","post_writer","post_date"]]
    df3.style.set_properties(**{'text-align': 'left'})
    if (df3.empty) or (df1.empty):
        df3 = ""
    
    return gallery_name_Kor, df3

def crawl(gallery_list):
    global conn, first, content, add_dict
    
    # connect to database
    conn = create_connection("./DC_Gall.db")

    # drop all tables if first run
    if first == 1:
        drop_all(conn)
        first = 0

    # execute sql commands
    if conn is not None:
        if len(gallery_list) == 0:
            return
        for gall in gallery_list:
            content = new_content(gall)
            gall_table = content[0] + "_"
            create_table(conn, create_table_sql2(gall_table))
            if add_dict[gall] == 1:
                add_dict[gall] = 0
            else:
                try:
                    for i in range(content[1].shape[0]):
                        script = (content[1].iloc[i,0], content[1].iloc[i,1], content[1].iloc[i,2], content[1].iloc[i,3])
                        create_instance2(conn, gall_table, script)
                except:
                    pass  
    else:
        print("Error: 데이터베이스 연결을 확인해주세요.")
    # close connection
    conn.close()

class MyThread(Thread):
    def __init__(self, event, gallery_list):
        Thread.__init__(self)
        self.stopped = event
        self.gallery_list = gallery_list

    def run(self):
        while not self.stopped.wait(5):
            crawl(self.gallery_list)

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f'{guild} 서버와 연결되었습니다.')

@client.event
async def on_message(message):
    global gall_dict, minor_dict, gallery_list, start, delete, add_dict, on
    if message.author == client.user:
        return

    if message.content == '!도움말':
        ran_color = randint(0, 0xffffff)
        embed = discord.Embed(title="명령어 사용법", \
                description="시스템에 갤러리 등록하기: !등록 갤러리이름 영문링크 마이너변수\n \
                         예) !등록 블레이드&소울 bns 0 \n \
                         모니터할 갤러리 추가하기: !추가 갤러리이름\n \
                         모니터할 갤러리 삭제하기: !삭제 갤러리이름\n \
                         모니터하는 갤러리 리스트: !리스트\n \
                         모니터 시작하기: !시작\n \
                         모니터 중지하기: !중지\n \
                         현재 모니터상태: !상태\n", \
                color=ran_color) 
        msg = await message.channel.send(embed=embed,delete_after=3)
        await msg.add_reaction("✅")

    if message.content == '!리스트':
        if len(gallery_list) == 0:
            msg = "등록된 갤러리가 없습니다."
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")
        else:
            msg = str(gallery_list)
            msg = msg.replace('[','').replace(']','').replace("'",'')
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")    

    if '!추가' in message.content:
        try:
            gallery = re.findall(r'!추가\s(.*?)$',message.content)
            gallery = gallery[0]
            try:
                if gallery not in gall_dict:
                    msg = "갤러리 이름을 확인해주세요."
                    msg = await message.channel.send(msg,delete_after=3)
                    await msg.add_reaction("✅")
                    return
                if gallery in gallery_list:
                    msg = "갤러리가 이미 리스트에 존재합니다."
                    msg = await message.channel.send(msg,delete_after=3)
                    await msg.add_reaction("✅")
                    return
                add_gallery(gallery)
                add_dict[gallery] = 1
            except:
                msg = "갤러리 이름을 확인해주세요."
                msg = await message.channel.send(msg,delete_after=3)
                await msg.add_reaction("✅")
                return
            msg = f"{gallery} 갤러리가 추가되었습니다."
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")
        except:
            msg = '추가하실 갤러리를 입력해주세요. 예) !추가 HIT'
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")

    if '!등록' in message.content:
        try:
            gallery = re.findall(r'!등록\s(.*?)\s(.*?)\s(.*?)$',message.content)
            kor_name = gallery[0][0]
            eng_name = gallery[0][1]
            is_minor = gallery[0][2]

            if is_minor == '0':
                url = 'http://gall.dcinside.com/board/lists/?id={}'.format(eng_name)
            elif is_minor == '1':
                url = 'http://gall.dcinside.com/mgallery/board/lists/?id={}'.format(eng_name)
            
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = requests.get(url, headers = headers)
            html = response.text 
            soup = BeautifulSoup(html, 'html.parser')
            gallery_name = soup.title.string
            # raise error if no gallery found
            if gallery_name == '디시인사이드':
                raise_error

            if kor_name not in gall_dict:
                gall_dict[kor_name] = (eng_name,int(is_minor))
                msg = f'{kor_name} 갤러리가 등록되었습니다.'
                msg = await message.channel.send(msg,delete_after=3)
                await msg.add_reaction("✅")
            else:
                msg = '이미 등록된 갤러리입니다.'
                msg = await message.channel.send(msg,delete_after=3)
                await msg.add_reaction("✅")
        except:
            msg = '갤러리 정보를 확인해주세요. 예) !등록 다크에덴 darkeden 1'
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")

    if '!삭제' in message.content:
        try:
            gallery = re.findall(r'!삭제\s(.*?)$',message.content)
            gallery = gallery[0]
            try:
                if gallery not in gall_dict:
                    msg = "갤러리 이름을 확인해주세요."
                    msg = await message.channel.send(msg,delete_after=3)
                    await msg.add_reaction("✅")
                    return
                remove_gallery(gallery)
            except:
                msg = "갤러리 이름을 확인해주세요."
                msg = await message.channel.send(msg,delete_after=3)
                await msg.add_reaction("✅")
                await message.channel.send("ㅤ")
                return
            msg = f"{gallery} 갤러리가 삭제되었습니다."
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")
        except:
            msg = '삭제하실 갤러리를 입력해주세요. 예) !삭제 HIT'
            msg = await message.channel.send(msg,delete_after=3)
            await msg.add_reaction("✅")

    if message.content == '!시작':
        if on == 0:
            on = 1
            start = 1
            while start == 1:
                if len(gallery_list) == 0:
                    pass
                else:
                    try:
                        conn = create_connection("./DC_Gall.db")
                        for gall in gallery_list:
                            gall_table = gall + "_"
                            df = pd.read_sql_query("SELECT * from {}".format(gall_table), conn)
                            gall_name_Eng = gall_dict[gall][0]
                            if gall_dict[gall][1] == 0:
                                gall_url = 'http://gall.dcinside.com/board/view/?id={}'.format(gall_name_Eng)
                            elif gall_dict[gall][1] == 1:
                                gall_url = 'http://gall.dcinside.com/mgallery/board/view/?id={}'.format(gall_name_Eng)
                            if df.size == 0:
                                pass
                            else:
                                gall_name = gall + " 갤러리"
                                for i in range(df.shape[0]):
                                    ran_color = randint(0, 0xffffff)
                                    embed=discord.Embed(title="", description=df.iloc[i,2], color=ran_color)
                                    embed.set_author(name=gall_name, url=gall_url+'&no='+str(df.iloc[i,1]))
                                    embed.add_field(name="작성자", value=df.iloc[i,3], inline=True)
                                    embed.add_field(name="시간", value=df.iloc[i,4], inline=True)
                                    embed.set_footer(text=gall_url+'&no='+str(df.iloc[i,1]))
                                    msg = await message.channel.send(embed=embed,delete_after=3)
                                    await msg.add_reaction("✅")
                            delete_instance(conn, gall_table)
                        conn.close()
                    except:
                        pass
                await asyncio.sleep(5)
        
    if message.content == '!중지':
        start = 0 
        on = 0
        for k, v in add_dict.items():
            add_dict[k] = 1

    if message.content == '!상태':
        if on:
            if len(gallery_list) != 0:
                monitor_gall = str(gallery_list)
                monitor_gall = monitor_gall.replace('[','').replace(']','').replace("'",'')
            else:
                monitor_gall = "없음"
            msg = "현재 아래의 갤러리 모니터중:\n{}".format(monitor_gall)
        else:
            msg = "현재 모니터 중지상태"
        msg = await message.channel.send(msg,delete_after=3)
        await msg.add_reaction("✅")

@client.event
async def on_raw_reaction_remove(payload):
    try:
        channel = client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if bot_name in str(msg.author):
            await asyncio.sleep(5)
            await msg.delete()
    except:
        return

def get_gall_dict():
    url = 'https://gall.dcinside.com'
    url2 = 'https://gall.dcinside.com/m'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # main gallery
    response = requests.get(url, headers = headers)
    html = response.text  # .text returns decoded string & .content returns bytes
    soup = BeautifulSoup(html, 'html.parser')
    anchors = soup.findAll('a', href=True)
    eng_list = []
    kor_list = []
    for anchor in anchors:
        anchor = str(anchor)
        eng = re.findall(r'"https:\/\/gall\.dcinside\.com\/board\/lists\/\?id=(.*?)"',anchor)
        kor = re.findall(r'"https:\/\/gall\.dcinside\.com\/board\/lists\/\?id=.*?".*?>(.*?)<\/a>',anchor)
        if len(eng) == 0:
            pass
        else:
            if " " in kor[0]:
                kor[0] = kor[0].replace(" ", "_")
            eng_list.append(eng[0])
            kor_list.append(kor[0])

    # minor gallery
    response = requests.get(url2, headers = headers)
    html = response.text  # .text returns decoded string & .content returns bytes
    soup = BeautifulSoup(html, 'html.parser')
    anchors = soup.findAll('a', href=True)
    eng2_list = []
    kor2_list = []
    for anchor in anchors:
        anchor = str(anchor)
        eng2 = re.findall(r'"https:\/\/gall\.dcinside\.com\/mgallery\/board\/lists\/\?id=(.*?)"',anchor)
        kor = re.findall(r'"https:\/\/gall\.dcinside\.com\/mgallery\/board\/lists\/\?id=.*?".*?>(.*?)<\/a>',anchor)
        if len(eng2) == 0:
            pass
        else:
            if " " in kor[0]:
                kor[0] = kor[0].replace(" ", "_")
            eng2_list.append(eng2[0])
            kor2_list.append(kor[0])

    # defind gallery dictionary 
    gall_dict = {}
    for i in range(len(eng_list)):
        gall_dict[kor_list[i]] = (eng_list[i],0)
    for j in range(len(eng2_list)):
        gall_dict[kor2_list[j]] = (eng2_list[j],1)
    gall_dict['다크에덴'] = ('darkeden',1)
    gall_dict['블레이드&소울'] = ('bns',0)

    return gall_dict

if __name__ == "__main__":
    # define global variables
    first = 1
    start = 1
    on = 0 
    delete = 0
    gall_dict = get_gall_dict()
    add_dict = {}
    
    # define gallery_list
    gallery_list = Manager().list()
    gallery_list = []

    # define perpetual web crawler
    stopFlag = Event()
    thread = MyThread(stopFlag, gallery_list)
    thread.start()

    # define discord bot token
    token = 'NjU5NjUzNTEzMzA3MjI2MTQz.XgWQJQ.Q5QdHPJAlXjMgK6NdGihb9lCyrw'
    bot_name = 'cral'
    
    # run bot
    client.run(token)

