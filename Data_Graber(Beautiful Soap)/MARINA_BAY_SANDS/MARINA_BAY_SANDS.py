import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup


class RestaurantsDetail:
    def __init__(self, url, order_number):
        # initialized a dictionary to store the dara
        self.DATA_DICT = {"Restaurant Name": [], "ShopAddress": [], "Phone Number": [], "Restaurant URL": [],
                          "Description": []}
        self.order_number = order_number
        self.URL = f"{url}"
        self.BaseURL = "https://www.marinabaysands.com"

    def appendingDataInJSONfile(self):
        self.getRestaurantsDetails()
        names = self.DATA_DICT['Restaurant Name']
        locations = self.DATA_DICT['ShopAddress']
        urls = self.DATA_DICT['Restaurant URL']
        phone_numbers = self.DATA_DICT['Phone Number']
        descriptions = self.DATA_DICT['Description']
        data = {
            "Restaurants": []
        }

        for name, location, url, phone_number, description in zip(names, locations, urls, phone_numbers, descriptions):
            data['Restaurants'].append(
                {
                    'Name': name,
                    'ShopAddress': location,
                    'URL': url,
                    'Phone Number': phone_number,
                    'Description': description

                }
            )
        order_id = self.order_number
        folder_path = 'Data'
        current_utc_datetime = datetime.datetime.utcnow()
        file_name = f"{order_id} - {current_utc_datetime.strftime('%Y-%m-%d__%H-%M')}.json"
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists('Data'):
            os.mkdir(folder_path)
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print("All Data Scrapped Successfully")

    def getRestaurantsDetails(self):
        # in this function getting details of location, phone number and description
        restaurant_location_list = []
        restaurant_phone_number_list = []
        restaurant_description_list = []
        # getting restaurant URLs by calling the url extractor function
        res_urls_and_names = self.getRestaurantUrls()
        res_urls = res_urls_and_names[0]
        res_names = res_urls_and_names[1]
        for url, name in zip(res_urls, res_names):
            print(f'Scrapping data of "{name}"')
            response = requests.get(url)
            # making soap of every url page getting from url of restaurants
            urlSoap = BeautifulSoup(response.text, 'html.parser')
            # print(urlSoap)
            if urlSoap is not None:
                # Finding div having details about phone number and location
                res_Location_div = urlSoap.find('div', class_="accordion__list--item panel")
                if res_Location_div is not None:
                    ul = res_Location_div.find('ul')
                    if ul is not None:
                        # Appending location data into a list
                        restaurant_location_list.append(ul.text.replace("\n", " ").replace('\u00a0', " "))
                    else:
                        # If location not available then it will append a empty string
                        restaurant_location_list.append(" ")
                    # print(res_Location_div.text)
                else:
                    print('soap not found')
                    restaurant_location_list.append(" ")
                # Finding Phone numbers
                phone_number = res_Location_div.text
                phone_numbers = re.findall(r"\+\d{2}\s?\d{4}\s?\d{4}", phone_number)
                if len(phone_numbers) != 0:
                    # Appending Phone Numbers data into a list
                    restaurant_phone_number_list.append(phone_numbers[0])
                else:
                    # If location not available then it will append a empty string
                    restaurant_phone_number_list.append("Not Available")
                # Finding Description of Restaurants
                description_div = urlSoap.find('div', class_="tagged-content-intro__content--info")
                description = " "
                if description_div is not None:
                    description_p = description_div.findAll('p')
                    for p in description_p:
                        description = description + p.text.replace("\n", " ").replace("  ", "").replace('\u00a0', " ")
                    restaurant_description_list.append(description)
                else:
                    restaurant_description_list.append(" ")
            else:
                restaurant_phone_number_list.append("Not Available")
                restaurant_description_list.append(" ")
                restaurant_location_list.append(' ')
        self.DATA_DICT['Description'] = restaurant_description_list
        self.DATA_DICT["ShopAddress"] = restaurant_location_list
        self.DATA_DICT['Phone Number'] = restaurant_phone_number_list
        # print(self.DATA_DICT)

    def getRestaurantUrls(self):
        soap = self.getRestaurantsSoap()
        restaurant_urls_list = []
        restaurant_names_list = []
        list_of_restaurants = soap.find('ul', class_="list-unstyled card-list card-box-list")
        urls_list = list_of_restaurants.findAll('a', class_="btn btn-secondary")
        restaurant_names = list_of_restaurants.findAll('h5', class_="card-title")
        for name in restaurant_names:
            if name is not None:
                restaurant_names_list.append(name.text.replace("\n", "").replace("\t", "").replace('\u00a0', " "))
            else:
                restaurant_names_list.append(" ")
        for url in urls_list:
            restaurant_url = self.BaseURL + url['href']
            restaurant_urls_list.append(restaurant_url)
        self.DATA_DICT['Restaurant URL'] = restaurant_urls_list
        self.DATA_DICT['Restaurant Name'] = restaurant_names_list
        # print(self.DATA_DICT)
        return restaurant_urls_list, restaurant_names_list

    def getRestaurantsSoap(self):
        response = requests.get(self.URL)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
