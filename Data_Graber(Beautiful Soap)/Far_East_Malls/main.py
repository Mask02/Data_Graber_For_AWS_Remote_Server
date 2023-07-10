import csv
from Far_East_Malls import FarEestShopDetails

if __name__ == "__main__":

    with open('Source/Grab Order.csv', 'r', encoding='utf-8') as file:
        # CSV reader
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            if len(row) >= 2:
                order_number = row[0]
                URL = row[1]
                bot = FarEestShopDetails(order_number=order_number, url=URL)
                bot.appendingDataInJSONfile()
