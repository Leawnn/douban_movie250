
import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import sqlite3


conn = sqlite3.connect('movie.db')
cur = conn.cursor()
sql = 'select introduction from movie250'
data = cur.execute(sql)
text = ""
for item in data:
    text = text + item[0]

#print(text)
cur.close()
conn.close()

cut = jieba.cut(text)
string = ' '.join(cut)
print(len(string))


img = Image.open(r'.\static\assets\img\tree.jpg')
img_array = np.array(img)#将图片转换为数组
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path="msyh.ttc"#这里字体可以在自己电脑里C盘下\windows\Font可以查看
)
wc.generate_from_text(string)

#绘制图片
fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off')#是否显示坐标轴

plt.savefig(r'.\static\assets\img\word.jpg',dpi=500)

#plt.show()









