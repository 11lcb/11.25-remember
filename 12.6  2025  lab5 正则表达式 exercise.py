import re

pattern = r"hello1"
text = "hello world"
match = re.search(pattern,text)      #匹配
if match:
    print(match.group())

#用一条高效代码：
def gaoxiao():
    text_2 = ['pdlemsesa','gjondknsa']
    match_1 = re.search(r"sa",r"sdawds")
    print(match_1 if match_1 else 'not found')

    match = re.search(r"se",text_2[0])
    print(match[0],text_2 if match else 'not foung') 

gaoxiao()

#        ||
#       \||/  匹配任何字符，但是尽可能少地匹配
#        \/
print(" .*?  ")  # . <--匹配任意单个字符   * <-- 匹配前面的元素0次或者多次   ？<-- 跟在*和.后面表示废贪婪模式


all_matches = re.findall(r"\d+","a1b23c345",)    #查找所有
#通过每个字符形式匹配相应的“\m（或者其他的）”，一个一个字符向前推进，知道筛选出完全吻合的字符串


parts = re.split(r"\s+","a  b   c")     #分割

result = re.sub(r"\d+","#","a1b2")     #替换


#print(all_matches,parts,result)
