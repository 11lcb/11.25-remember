import re

def extra():
    print("\n","附加作业:") 
    with open ("task_add.txt","r",encoding="utf-8") as t:
        content = t.read()
    #print(content)
    pattern_date = r'\s\d+[-/..]\d+[-/..]\d+'
    pattern_email =r' \w+@\w+[/..]\w+'
    pattern_website =r'\shttp[s:/]+\w+.[a-zA-Z]+'
    
    match_date = re.findall(pattern_date,content)
    print(match_date if match_date else "notfond")

    match_email = re.findall(pattern_email,content)
    print(match_email if match_email else "notfond")

    match_website = re.findall(pattern_website,content)
    print(match_website if match_website else "notfond")

extra()        