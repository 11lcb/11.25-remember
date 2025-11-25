import csv


def serch_accurate_years_book():
    asked_time = ["2014","2016","2017"]
    time_row = []
    for row in csv_reader:
        time = row[6]
        day,month,year = time.split('.')
        year_1,when_1 = year.split()
        if year_1 in asked_time:
            time_row.append(row)
    print(f'asked_time: {asked_time}.  have {len(time_row)} books')

with open ('books.csv','r',encoding="cp1251") as file:
    csv_reader = csv.reader(file,delimiter=';')

    firse_one = next(csv_reader)
    serch_accurate_years_book() 