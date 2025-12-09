import csv
import re


def first():
    print("作业1:")
    with open ('task1-en.txt','r',encoding="utf-8") as file_EN:
        content_EN = file_EN.read()

    pattern_A_z = r'\b[A-Z]+[a-zA-Z]+\b'
    pattern_maohao = r'\b\w+:'
    text_en = content_EN

    match_a_z = re.findall(pattern_A_z,text_en)
    match_maohao = re.findall(pattern_maohao,text_en)

    
    print('所有大写字母开头的单词','有',len(match_a_z),'个单词:',match_a_z)
    print('后面有冒号的词','有',len(match_maohao),'个单词:',match_maohao)

def second():
    print("\n","作业2:")
    with open ('task2.html','r',encoding='utf-8') as a:
        text = a.read()
    pattern_1= r'</([a-zA-Z][a-zA-Z0-9]*)>'
    match_1 = re.findall(pattern_1,text)
    new_match = set(match_1)

    print("所有闭合标签:",new_match if match_1 else 'not found')
    print("有",len(new_match),"个标签")

    
def third():
    print('\n',"作业3:")
    with open ('task3.txt','r',encoding='utf-8') as f:
        content = f.read()    
    pattern_ID = r'\s\d+'
    match_ID = re.findall(pattern_ID,content)
    ID = []
    for i in match_ID:
        if len(i)<5:
            ID.append(i)
    pattern_NAME = r'[A-Z].*?\s' 
    match_NAME = re.findall(pattern_NAME,content)
    pattern_EMAIL = r'\w+@.*?\s'
    match_EMAIL = re.findall(pattern_EMAIL,content)
    pattern_DATE = r'\d+-\d+-\d+'
    match_DATE = re.findall(pattern_DATE,content)
    pattern_WEBSITE = r'\w+://\w+..*?/'
    match_WEBSITE = re.findall(pattern_WEBSITE,content)

    new = []
    for i in range(250):
        new.append(ID[i])
        new.append(match_NAME[i])
        new.append(match_EMAIL[i])
        new.append(match_DATE[i])
        new.append(match_WEBSITE[i])
    #print(new)
    print("已将内容写入csv文件:   12.6  2025  lab5 正则表达 .csv ")
    with open('12.6  2025  lab5 正则表达 .csv','w',newline='',encoding='utf-8') as c:
        table_csv = csv.writer(c)
        table_csv.writerow(['ID','姓氏','电邮','注册日期','网站'])
        for a in range(0, len(new), 5):
            item = new[a:a+5]
            table_csv.writerow(item)
           

def extra():
    print("\n","附加作业:") 
    with open ("task_add.txt","r",encoding="utf-8") as t:
        content = t.read()
    #print(content)
    pattern_date = r'\s\d+[-/..]\d+[-/..]\d{2,4}'
    pattern_email =r' \w+@\w+[/..][a-zA-Z]+'
    pattern_website =r'\shttp[s:/]+\w+.[a-zA-Z]+'
    
    match_date = re.findall(pattern_date,content)
    print("查询到的5个日期:","\n",match_date if match_date else "notfond")

    match_email = re.findall(pattern_email,content)
    print("查询到的5个邮箱地址:","\n",match_email if match_email else "notfond")

    match_website = re.findall(pattern_website,content)
    print("查询到的5个网址","\n",match_website if match_website else "notfond")


if __name__== '__main__':
    first()    
    second()
    #third()
    extra()