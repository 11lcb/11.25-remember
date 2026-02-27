import requests

API_KEY = "6cd03555-cb42-4784-b416-f91b94cae408"

COUNTRY = input("选择要查询节假日的国家(比如： RU US CN AM ....) :")
YEAR = input("输入需要查询的年份：(免费用户只能查询限制到去年的数据)")

url = f"https://holidayapi.com/v1/holidays"
canshu = {
    "key": API_KEY,
    "country": COUNTRY,
    "year": YEAR,
}

def output():
    global i,h
    print(f"{i}. {h['name']}")
    print(f"   日期: {h['date']}")
    print(f"   星期: {h['weekday']['date']['name']}")
    if h['public']==True:
        print(f"   类型: Public")
    else:
        print(f"   类型：not public")    
    print(f"   国家: {h['country']}")
    print(f"   是否观察日: {h['observed']}")

try:
    response = requests.get(url, params=canshu)  #  ！最核心的请求网址，以及上传参数的代码 ！
    data = response.json()
    #  response.status_code == 200 用来判断API是否请求成功，200 是HTTP请求成功的状态码 
    if response.status_code == 200 :
        if data.get('holidays'):
            print(f" {YEAR}年 {COUNTRY} 的法定节假日（共{len(data['holidays'])}个）")
            #print(data['holidays'])    #查看输出格式
            A = input("是否查看所有节日(Y/N)：")
            if A== "Y":
                for i, h in enumerate(data['holidays'], 1):
                    output()  
            else:
                for i, h in enumerate(data['holidays'], 1):
                    output()
                    if i >3:
                        break
                print(".\n.\n.\n.")

        else:
            print("没有查询到节假日。。。")        
    else:
        print(f" API请求失败,获取数据失败")

except Exception as reason:
    print(f"程序出错: {reason}")


