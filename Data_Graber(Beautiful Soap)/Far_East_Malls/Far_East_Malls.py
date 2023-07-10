import datetime
import json
import os
import re
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class FarEestShopDetails:
    def __init__(self, order_number, url):

        # initialized a dictionary to store the dara

        self.DATA_DICT = {"Shop Name": [], "ShopAddress": [], "Phone Number": [], "Shop URL": [],
                          "Description": []}
        self.order_number = order_number
        self.URL = f"{url}"
        self.BaseURL = "https://www.fareastmalls.com.sg"

    def appendingDataInJSONfile(self):

        self.getShopDescription()
        names = self.DATA_DICT['Shop Name']
        locations = self.DATA_DICT['ShopAddress']
        urls = self.DATA_DICT['Shop URL']
        phone_numbers = self.DATA_DICT['Phone Number']
        descriptions = self.DATA_DICT['Description']

        data = {
            "Shops": []
        }

        for name, location, url, phone_number, description in zip(names, locations, urls, phone_numbers, descriptions):
            data['Shops'].append(
                {
                    'Shop Name': name,
                    'Shop Address': location,
                    'Shop URL': url,
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

    def getShopDescription(self):

        # in this function getting  description of Shops
        shop_description_list = []
        shop_number_list = []
        # getting Shops URLs by calling the url extractor Description
        data = self.getShopData()
        res_urls = data[0]
        names = data[1]
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=chrome_options)
        if res_urls:
            for url, name in zip(res_urls, names):
                # print(url)
                print(f'Scrapping data of "{name}"')
                # Finding Description of Restaurants
                driver.get(url)
                page = driver.page_source
                soap = BeautifulSoup(page, 'html.parser')
                description = soap.find('div', id='b-shop-description')
                phone_number_div = soap.find('div', id='b-shop-details')
                # print(description.text)
                phone_number = re.search(r'\d{4} \d{4}', phone_number_div.text)
                if phone_number:
                    extracted_number = phone_number.group().strip()
                    shop_number_list.append(extracted_number)
                if description is not None:
                    description = description.text.replace("\n", " ").replace("  ", "").replace('\u00a0', " ").replace(
                        '\r', "").replace("\"", "")
                    shop_description_list.append(description)
                else:
                    shop_description_list.append("Not available")
            driver.close()
        else:
            shop_description_list.append("Not Available")

        self.DATA_DICT['Description'] = shop_description_list
        self.DATA_DICT['Phone Number'] = shop_number_list
        # print(self.DATA_DICT)

    def getShopData(self):

        global list_of_shop
        soap = self.getShopSoap()

        shop_urls_list = []
        shop_name_list = []
        shop_address_list = []

        if soap is not None:
            list_of_shop = soap.findAll('section', class_="b-section shop-list")[0]
            # Shop URLs
            urls_of_shops = list_of_shop.findAll('a')
            for shopurl in urls_of_shops:
                if shopurl is not None:
                    shop_urls_list.append(self.BaseURL + shopurl['href'])
                else:
                    shop_urls_list.append("Not Available")
                    print("Info Not Available")

            # Shop Names
            names_of_shops = list_of_shop.findAllNext('span', class_="b-store-title")
            for name in names_of_shops:
                if name is not None:
                    shop_name_list.append(name.text.replace("\n", "").replace("  ", "").replace('\u00a0', " "))
                    shop_address_list.append("Not Available")
                else:
                    shop_name_list.append("Not Available")

        else:
            shop_address_list.append("Not Available")
            shop_urls_list.append("Not Available")
            shop_name_list.append("Not Available")
        shop_urls_list.pop()
        self.DATA_DICT['ShopAddress'] = shop_address_list
        self.DATA_DICT['Shop Name'] = shop_name_list
        self.DATA_DICT['Shop URL'] = shop_urls_list
        return shop_urls_list, shop_name_list

    def getShopSoap(self):
        print("Scrapping Process start")
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        driver.get(self.URL)
        print("Loading.....")
        while True:
            try:
                element = driver.find_element(By.XPATH, '//*[@id="b-store"]/div[2]')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                driver.implicitly_wait(10)
                button = driver.find_element(By.CLASS_NAME, 'b-load-more-shops')
                button.click()
            except:
                break
        driver.implicitly_wait(10)
        sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.close()
        return soup
