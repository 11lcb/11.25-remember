import csv
with open ('books-en.csv','r',encoding='cp1251') as file:
    csv_reader = csv.reader(file, delimiter=';',quotechar='"')
    print(f" {'\x1b[48;5;88m'} use 'quorechar' for skipping delimiter in the asked_row {'\x1b[0m'}")
    first_sentence = next (csv_reader)
    
    limitted_year = []
    asked_year='1990'
    for row in csv_reader:
        time=row[3]
        if int(time) <=  int(asked_year):
            limitted_year.append(row)
         
    print(f"books_year to {int(asked_year)} , have {len(limitted_year)} books")

            