import re
with open ('task2.html','r',encoding='utf-8') as f:
    contents = f.read()

pattern = r'content\s*=\s*["\']([^"\']+)["\']'
match = re.findall(pattern,contents)

print(match if match else "no")
print(len(match))
       