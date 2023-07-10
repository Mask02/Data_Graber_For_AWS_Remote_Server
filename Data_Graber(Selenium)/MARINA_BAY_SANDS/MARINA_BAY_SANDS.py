import datetime
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class RestaurantsDetail:
    def __init__(self,url,order_number):
        # initialized a dictionary to store the dara
        self.order_number = order_number
        self.DATA_DICT = {"Restaurant Name": [], "ShopAddress": [], "Phone Number": [], "Restaurant URL": [],
                          "Description": []}
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.URL = f"{url}"
        self.BaseURL = "https://www.marinabaysands.com"

    def appendingDataInJSONfile(self):
        self.getRestaurantDetails()
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

    def getRestaurantDetails(self):

        restaurant_urls_list = []
        restaurant_number_list = []
        restaurant_location_list = []
        restaurant_names_list = []
        restaurant_description_list = []
        self.driver.get(self.URL)
        self.driver.maximize_window()
        list_of_restaurants = self.driver.find_elements(By.XPATH, "//div[@class='card-footer']")
        for res_url in list_of_restaurants:
            phone_and_url = res_url.find_elements(By.TAG_NAME, 'a')
            restaurant_urls_list.append(phone_and_url[0].get_attribute('href'))
            restaurant_number_list.append(phone_and_url[1].text)
            location_li = res_url.find_elements(By.XPATH, "//li[@class='card-text card-text-icon icon-location']")
            for location in location_li:
                restaurant_location_list.append(location.text)

        names_div = self.driver.find_elements(By.XPATH, "//h5[@class='card-title']")
        for name in names_div:
            restaurant_names_list.append(name.text)
        description_div = self.driver.find_elements(By.XPATH, "//div[@class='card-body']//p")
        for description in description_div:
            restaurant_description_list.append(description.text)
        self.DATA_DICT['Restaurant URL'] = restaurant_urls_list
        self.DATA_DICT['Phone Number'] = restaurant_number_list
        self.DATA_DICT['ShopAddress'] = restaurant_location_list
        self.DATA_DICT['Restaurant Name'] = restaurant_names_list
        self.DATA_DICT['Description'] = restaurant_description_list

