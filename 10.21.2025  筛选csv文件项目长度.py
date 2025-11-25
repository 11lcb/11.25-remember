import csv
with open('books.csv','r',encoding='cp1251') as file :
    csv_reader = csv.reader(file,delimiter=';')
    
    headers = next(csv_reader)
    print("Title:",headers)
    
    row_length=[]
    for row in csv_reader:
        books_title=row[1]
        if len(books_title)>30:
            print(f'title: {books_title}')
            row_length.append(books_title)

print(f"numbers whose length of title is over 30:{len(row_length)}")  


