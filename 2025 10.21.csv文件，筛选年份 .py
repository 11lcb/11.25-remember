import csv


def serch_area_years_books(csv_reader):
    a= input("limitted year: ")
    asked_time_limitted = a
    books = []
    for row_2 in csv_reader:
        time = row_2[6]
        year = time[6:10]
        
        if int(year) <=  int(asked_time_limitted) :
            books.append(row_2)
    print(f'asked_time_limitted book to  {asked_time_limitted}, have {len(books)} books')

with open ('books.csv','r',encoding="cp1251") as file:
    csv_reader = csv.reader(file,delimiter=';')

    firse_one = next(csv_reader)
    #serch_accurate_years_book()
    print()
    serch_area_years_books(list(csv_reader))

