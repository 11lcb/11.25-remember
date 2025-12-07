import csv
import re


def first():
    print("作业1:")
    with open ('task1-en.txt','r',encoding="utf-8") as file_EN:
        content_EN = file_EN.read()
    with open ('task1-ru.txt','r',encoding="utf-8") as file_RU:
        content_RU = file_RU.read()

    pattern_C = r'\b[cC]\w*'
    pattern_the = r'\b[tT]he\s+[a-zA-Z]+'
    pattern_И = r'\b[иИ]\s+[а-яА-ЯёЁ]+'
    text_en = content_EN
    text_ru = content_RU

    match_c = re.findall(pattern_C,text_en)
    match_the = re.findall(pattern_the,text_en)
    match_И = re.findall(pattern_И,text_ru)
    
    print('以c/C开头的单词:','有',len(match_c),'个单词,for example:',match_c[:5])
    print('"the"后面的单词:','有',len(match_the),'个单词,for example:',match_the[:5])
    print('"И"后面的单词：','有',len(match_И),'个单词,for example:',match_И[:5])

def second():
    print("\n","作业2:")
    with open ('task2.html','r',encoding='utf-8') as a:
        text = a.read()
        pattern_1= r"font-family:\s*'.*?'"
        match_1 = re.findall(pattern_1,text)
        Match_1 = [i[14:22] for i in match_1]
        pattern_2= r'font-style:\s.*?;'
        match_2 = re.findall(pattern_2,text)
        Match_2 = [i[12:18] for i in match_2]
        pattern_3= r'font-weight:\s.*?;'
        match_3 = re.findall(pattern_3,text)
        Match_3 = [i[13:16] for i in match_3]
        pattern_4= r"font-display:\s.*?;"
        match_4 = re.findall(pattern_4,text)
        Match_4 = [i[14:18] for i in match_4]

        print("font-family:",Match_1 if match_1 else 'not found')
        print("font-style:",Match_2 if match_2 else 'not found')
        print("font-weight:",Match_3 if match_3 else 'not found')
        print("font-display:",Match_4 if match_4 else 'not found')
    
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
    third()
    extra()
