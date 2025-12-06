import re

a= open ('task2.html','r',encoding='utf-8')
text = a.read()
a.close()
print("有：",len(text),"个字符")
print(text[:5000])