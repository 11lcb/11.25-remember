import re

with open ('task3.txt','r',encoding='utf-8') as f:
    content = f.read()
#ID、姓氏、电邮、注册日期和网站
#print(content)    

pattern_ID = r'\s\d+'
match_ID = re.findall(pattern_ID,content)
ID = []
for i in match_ID:
    if len(i)<5:
       ID.append(i)
#print(ID) 

pattern_NAME = r'[A-Z].*?\s' 
match_NAME = re.findall(pattern_NAME,content)
#print(match_NAME if match_NAME else "error")
#print(len(match_NAME))

pattern_EMAIL = r'\w+@.*?\s'
match_EMAIL = re.findall(pattern_EMAIL,content)
#print(match_email if match_email else "error")
#print(len(match_EMAIL))

pattern_DATE = r'\d+-\d+-\d+'
match_DATE = re.findall(pattern_DATE,content)
#print(match_date[:5] if match_date else "error")
#print(len(match_DATE))

pattern_WEBSITE = r'\w+://\w+..*?/'
match_WEBSITE = re.findall(pattern_WEBSITE,content)
#print(match_website[:5] if match_website else "error")
#print(len(match_WEBSITE))

new = []
for i in range(250):
    new.append(ID[i])
    new.append(match_NAME[i])
    new.append(match_EMAIL[i])
    new.append(match_DATE[i])
    new.append(match_WEBSITE[i])
print(new)    


