import requests
from bs4 import BeautifulSoup as bs
import re
import pymysql

"""
第一页:https://movie.douban.com/top250?start=0&filter
第二页:https://movie.douban.com/top250?start=25&filter
第三页:https://movie.douban.com/top250?start=50&filter
...
"""
url = 'https://movie.douban.com/top250?start={}&filter'
prox = {
    "http":"202.154.27.132:8080"
}
sql = "insert into top250 values('%s', '%s', '%s', '%s', '%s', '%s') on duplicate key update name='%s'"
# sql = "update top250 set director='%s', actor='%s', year='%s', area='%s', genre='%s', name='%s' where name='%s'"
conn = pymysql.connect("localhost", "root", "root", "douban", charset="utf8")
cursor = conn.cursor()
for s_index in range(0, 226, 25):
    curr_url = url.format(s_index)
    print(curr_url)
    page = requests.get(url.format(s_index), proxies=prox).text
    soup_1 = bs(page, "lxml")
    infos = soup_1.find_all("div", attrs={"class": "info"})
    for info in infos:
        titles = info.find_all("span")
        title_zh = titles[0].get_text()
        print(title_zh)
        extra_infos = info.find("div", attrs={"class": "bd"}).find("p").get_text().strip().replace("'", "\\'").split("\n")  # 导演演员类别
        dir_actors = extra_infos[0].split("\xa0\xa0\xa0")
        director = dir_actors[0].split("/")[0][4:].strip()  # 导演
        if len(dir_actors) > 1:
            actor = dir_actors[1].split("/")[0][4:].strip()  # 演员
        year_area_genre = extra_infos[1].strip().replace("\xa0", "")
        year, area, genre = re.match("(.+)[/]{1}(.+)[/]{1}(.+)", year_area_genre).groups()  # 时间/地区/剧情
        cursor.execute(sql % (director, actor, year, area, genre, title_zh, title_zh))
        print(dir_actors)
        print(actor)
        print(year, area, genre)
        print("-" * 50)
print(cursor.rowcount)
conn.commit()
cursor.close()
conn.close()