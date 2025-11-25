import xml.etree.ElementTree as file
tree = file.parse('currency.xml')
root = tree.getroot()

asked=[]
        
for i in root.findall('Valute'):
    nominal = i.find('Nominal').text
    Name = i.find('Name').text
    if i.find ("Nominal").text == '1':
        
        asked.append(Name)
        
print(f'Список Name, но только для валют с Nominal=1,have {len(asked)} names') 
print(f"{'\x1b[48;5;44m'}list:  {'\x1b[0m'}")
for name in asked:
    print(name)      



