# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 16:49:20 2020

@author: leawnn
"""


from bs4 import BeautifulSoup    #网页解析，获取数据
import re         #正则表达，进行文字匹配
import urllib.request,urllib.error      #制定URL，获取网页数据
import xlwt      #进行excel操作
import sqlite3


#查找<a href="https://movie.douban.com/subject/1849031/">
#影片详情链接的规则
#以<a href="开头，中间有很多字符，以.*表示（.表示一个字符，*表示0个到多个字符，?表示0到多次的重复出现）
findLink = re.compile(r'<a href="(.*?)">')  #创建正则表达式对象，表示规则（字符串的模式）
#影片图片
#对<img alt="怦然心动" class="" src="https://img1.doubanio.com/view/photo/s_IF NOT EXISTSratio_poster/public/p501177648.jpg" width="100"/>
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)   #r.S表示忽略这一行中出现的换行符,让换行符包含在字符中
#影片片名
#<span class="title">怦然心动</span>
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
#<span class="rating_num" property="v:average">9.1</span>
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
#<span>1384972人评价</span>
#(\d*)中，\d表示数字，\d*表示有0个多个数字
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#找到概况
#<span class="inq">真正的幸福是来自内心深处。</span>
findInq = re.compile(r'<span class="inq">(.*)</span>')
#找到影片的相关内容
#<p class="">
            #导演: 罗伯·莱纳 Rob Reiner   主演: 玛德琳·卡罗尔 Madeline Carroll / 卡...<br/>
            #2010 / 美国 / 剧情 喜剧 爱情
#</p>
findDb = re.compile(r'<p class="">(.*?)</p>',re.S)

#爬取网页
def getData(baseurl):
    datalist = []
    
    for i in range(0,10):
        url = baseurl + str(i*25)
        html = askURL(url)
        #2逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):#查找符合要求的字符串，形成列表         div,class=“item”在网页中查找的，每一步电影的描述都是这样
            #print(item)         #测试，查看电源item全部信息
            data =[]   #保存一部电源的所有信息
            item = str(item)
            
            #影片详情的链接
            link = re.findall(findLink,item)[0]    #re库用来通过正则表达式来查找指定的字符串
            #print(link)      #返回所有影片的详情链接
            data.append(link)
            
            imgSrc = re.findall(findImgSrc,item)
            data.append(imgSrc)
            
            titles = re.findall(findTitle,item)#片名可能只有中文名，没有外国名
            if (len(titles)==2):        #如果有两个电影名
                ctitle = titles[0]
                data.append(ctitle.strip())      #添加中文名
                otitle = titles[1].replace("/","")
                data.append(otitle.strip())       #添加外国名
            else :
                data.append(titles[0].strip())
                data.append(' ')     #即使没有外国名，也要留空，不然内容窜位了
            
            rating= re.findall(findRating,item)[0]
            data.append(rating.strip())         #添加评分
            
            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum.strip())       #添加评价人数
            
            inq = re.findall(findInq,item)
            if len(inq)!= 0:
                inq = inq[0].replace("。","")            #去掉句号
                data.append(inq.strip()) #添加概述
            else:
                data.append(' ')
            
            bd = re.findall(findDb,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+?)',"",bd)#去掉<br/>
            bd = re.sub('/',"",bd)#替换/
            data.append(bd.strip())#去掉前后的空格
            
            
            datalist.append(data)#把处理好的一部电影信息放入datalist
                       
            
    #print(datalist)        
            
            
    return datalist
#得到指定一个URl的网页内容
def askURL(url):
    head = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
    request = urllib.request.Request(url = url,headers=head)
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)
    return html
        
#保存数据
def saveData(datalist,savepath):
    print("save...")
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)#创建workbook对象
    sheet = book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True)#创建工作表
    col = ('电影详情链接',"图片链接","影片中文名","外国名","评分","评价数","概况","相关信息")
    for i in range(len(col)):
        sheet.write(0,i,col[i])#列名
    for i in range(0,250):
        print("第%d条"%i)
        data = datalist[i]
        for j in range(len(col)):
            sheet.write(i+1,j,data[j])#数据
    
    
    book.save(savepath)#保存

def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index ==4 or index ==5:
                continue
            data[index] = '"'+str(data[index])+'"'
        sql = '''
                insert into movie250
                (info_link,pic_link,cname,ename,score,rated,introduction,info)
                values (%s)
            '''%",".join(data)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()
    print("...")
#create table IF NOT EXISTS movie250
def init_db(dbpath):
    sql = '''
        
        create table movie250 
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar ,
        score numeric ,
        rated numeric ,
        introduction text,
        info text
        
        )
    '''#创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()

def main():
    #爬取网页、解析数据、保存数据
    baseurl = 'https://movie.douban.com/top250?start='
    #1爬取网页
    datalist = getData(baseurl)
    #savepath = '豆瓣电影Top250.xls'
    dbpath = "movie.db"
    #3保存数据
    #askURL(baseurl)
    #saveData(datalist,savepath)
    saveData2DB(datalist,dbpath)


#init_db("movietest.db")
main()