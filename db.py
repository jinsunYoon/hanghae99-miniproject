import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('mongodb://3.34.252.62', 27017, username = "test", password = "test")

db = client.music_list


## 이미지링크
imgs = [
            "https://musicmeta-phinf.pstatic.net/album/004/673/4673490.jpg?type=r480Fll&v=20210303150028",
            "https://musicmeta-phinf.pstatic.net/album/004/614/4614746.jpg?type=r480Fll&v=20210802045022",
            "https://musicmeta-phinf.pstatic.net/album/004/613/4613637.jpg?type=r480Fll&v=20210530095023",
            "https://musicmeta-phinf.pstatic.net/album/004/707/4707332.jpg?type=r480Fll&v=20210530105523",
            "https://musicmeta-phinf.pstatic.net/album/004/616/4616999.jpg?type=r480Fll&v=20210530100022",
            "https://musicmeta-phinf.pstatic.net/album/004/733/4733872.jpg?type=r480Fll&v=20210530111026",
            "https://musicmeta-phinf.pstatic.net/album/002/288/2288765.jpg?type=r480Fll&v=20210529053510",
            "https://musicmeta-phinf.pstatic.net/album/004/550/4550593.jpg?type=r480Fll&v=20210303143526",
            "https://musicmeta-phinf.pstatic.net/album/004/642/4642242.jpg?type=r360Fll&v=20210303145528",
            "https://musicmeta-phinf.pstatic.net/album/004/535/4535336.jpg?type=r480Fll&v=20210530074519",
            "https://musicmeta-phinf.pstatic.net/album/004/498/4498641.jpg?type=r480Fll&v=20210530064521",
            "https://musicmeta-phinf.pstatic.net/album/004/701/4701143.jpg?type=r480Fll&v=20210530105022",
            "https://musicmeta-phinf.pstatic.net/album/004/738/4738967.jpg?type=r480Fll&v=20210530111522",
            "https://musicmeta-phinf.pstatic.net/album/004/614/4614748.jpg?type=r480Fll&v=20210303145027",
            "https://musicmeta-phinf.pstatic.net/album/004/738/4738967.jpg?type=r480Fll&v=20210530111522",
            "https://musicmeta-phinf.pstatic.net/album/004/535/4535336.jpg?type=r480Fll&v=20210530074519",
            "https://musicmeta-phinf.pstatic.net/album/003/137/3137158.jpg?type=r480Fll&v=20210529223021",
            "https://musicmeta-phinf.pstatic.net/album/004/477/4477123.jpg?type=r480Fll&v=20210303141530",
            "https://musicmeta-phinf.pstatic.net/album/004/574/4574324.jpg?type=r480Fll&v=20210913230538",
            "https://musicmeta-phinf.pstatic.net/album/003/198/3198839.jpg?type=r480Fll&v=20210802055026",
            "https://musicmeta-phinf.pstatic.net/album/004/686/4686872.jpg?type=r480Fll&v=20210303150027"
        ]
## 유튜브링크
urls = [
            "https://www.youtube.com/embed/ESKfHHtiSjs",
            "https://www.youtube.com/embed/tDukIfFzX18",
            "https://www.youtube.com/embed/ioNng23DkIM",
            "https://www.youtube.com/embed/Arciqhs4aj0",
            "https://www.youtube.com/embed/oKUEbsJDvuo",
            "https://www.youtube.com/embed/tJQaUW36pMw",
            "https://www.youtube.com/embed/3yST4DBZ8aE",
            "https://www.youtube.com/embed/TgOu00Mf3kI",
            "https://www.youtube.com/embed/xCVqH32p4MA",
            "https://www.youtube.com/embed/SvWidiKtj6U",
            "https://www.youtube.com/embed/3DOkxQ3HDXE",
            "https://www.youtube.com/embed/erVnNhFOHl4",
            "https://www.youtube.com/embed/LKPsNcuQcQY",
            "https://www.youtube.com/embed/H8YW1tlsmE8",
            "https://www.youtube.com/embed/KCKSETmf2EA",
            "https://www.youtube.com/embed/iDjQSdN_ig8",
            "https://www.youtube.com/embed/q0hyYWKXF0Q",
            "https://www.youtube.com/embed/rVXeArOQIs4",
            "https://www.youtube.com/embed/rOCymN-Rwiw",
            "https://www.youtube.com/embed/SlPhMPnQ58k",
            "https://www.youtube.com/embed/d2ytH5mymWY"
       ]

# 멜론사이트 제목,가수,앨범명 크롤링
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.melon.com/chart/month/index.htm?classCd=GN0000&moved=Y&rankMonth=202008',headers=headers)
soup = BeautifulSoup(data.text, 'html.parser')
trs = soup.select('#frm > div > table > tbody >tr ')

count = 0
for tr in trs:
    if count > 20:
        break
    img = imgs[count]
    title = tr.select_one('td:nth-child(6) > div > div > div.ellipsis.rank01 > span > a').text.strip()
    artist = tr.select_one('td:nth-child(6) > div > div > div.ellipsis.rank02 > a').text.strip()
    album = tr.select_one('td:nth-child(7) > div > div > div > a').text.strip()
    url = urls[count]
    like = 0
    doc = {'img': img, 'title': title, 'artist': artist, 'album': album, 'url': url, "like": like}
    db.music_list.insert_one(doc)
    count += 1


