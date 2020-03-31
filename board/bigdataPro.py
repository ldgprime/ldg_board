'''
Created on 2020. 3. 31.

@author: admin
'''
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import os
import folium
from folium import plugins
import pandas as pd
import requests
from konlpy.tag import Okt
from collections import Counter
import pytagcloud
from ldg_board.settings import STATIC_DIR, TEMPLATE_DIR


def movie_crawling(data):
    for i in range(100):
        url="https://movie.naver.com/movie/point/af/list.nhn?&page="
        url=url+str(i+1)
        req=requests.get(url)
        if req.ok:
            html=req.text
            soup=BeautifulSoup(html, 'html.parser')
            titles=soup.select(".title a.movie")
            points=soup.select(".title em")
            contents=soup.select(".title")
            n=len(titles)
            for i in range(n):
                title=titles[i].get_text()
                point=points[i].get_text()
                contentarr=contents[i].get_text().replace('신고','').split("\n\n")
                content=contentarr[2].replace("\t","").replace("\n","")
                data.append([title,point,content])

def makeGraph(titles, points):
    font_location = "c:/Windows/fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)

    plt.xlabel('영화제목')
    plt.ylabel('평균평점')
    plt.grid(True)
    #'int(), float() df['필드명'].astype(float32)'    
    plt.bar(range(len(titles)), points, align='center')
    plt.xticks(range(len(titles)), list(titles), rotation='70')
    plt.savefig(os.path.join(STATIC_DIR ,'images/fig01.png'), dpi=300)
    
    
def cctv_map():
    popup=[]
    data_lat_log=[]
    a_path='E:/pythonProject/data/'
    df=pd.read_csv(os.path.join(a_path,"cctv/CCTV_20190917.csv"),encoding="utf-8")
    for data in df.values:
        if data[4]>0:
            popup.append(data[1])
            data_lat_log.append([data[10],data[11]])
    
    m=folium.Map([35.1803305,129.0516257], zoop_start=11)
    plugins.MarkerCluster(data_lat_log,popups=popup).add_to(m)
    m.save(os.path.join(TEMPLATE_DIR,"map/map01.html"))
     
def saveWordCloud(contents):
    nlp = Okt()
    wordtext=""
    for t in contents:
        wordtext+=str(t)+" "
        
    nouns = nlp.nouns(wordtext)
    count = Counter(nouns)
    
    wordInfo = dict()
    for tags, counts in count.most_common(100):
        if (len(str(tags)) > 1):
            wordInfo[tags] = counts
    filename=os.path.join(STATIC_DIR,'images/wordcloud01.png')
    taglist = pytagcloud.make_tags(dict(wordInfo).items(), maxsize=80)
    pytagcloud.create_tag_image(taglist, filename, 
                                size=(640, 480), 
                                fontname='korean', rectangular=False)
    
    
    
                
                
                