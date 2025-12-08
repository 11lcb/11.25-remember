import csv
import re


def first():
    print("作业1:")
    with open ('task1-en.txt','r',encoding="utf-8") as file_EN:
        content_EN = file_EN.read()
    pattern_number = r'\b\d+(?:\.\d+)?\b'
    pattern_letter_6 = r'\b[a-zA-Z]{6}\b'
    pattern_letter_8 = r'\b[a-zA-Z]{8}\b'
    match_letter_6 = re.findall(pattern_letter_6,content_EN)
    match_letter_8 = re.findall(pattern_letter_8,content_EN)
    match_number = re.findall(pattern_number,content_EN)

    print('所有6个字母的单词:','有',len(match_letter_6),'个单词,for example:',match_letter_6)
    print('所有8个字母的单词:','有',len(match_letter_8),'个单词,for example:',match_letter_8)
    print('所有数字:','有',len(match_number),'个数字,for example:',match_number)

def second():
    print("\n","作业2:")
    with open ('task2.html','r',encoding='utf-8') as a:
        text = a.read()
        pattern= r'content="(.*?)"'
        match = re.findall(pattern,text)
        print("所有的content后面一共有:",len(match),"个字符串")
        print("所有字符串:",match if match else 'not found')
        
    
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