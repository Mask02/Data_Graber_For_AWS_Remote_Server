import datetime
import json
import os
from time import sleep
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class ShopDetails:
    def __init__(self, order_number, url):

        # initialized a dictionary to store the dara

        self.order_number = order_number
        self.DATA_DICT = {"Shop Name": [], "ShopAddress": [], "Phone Number": [], "Shop URL": [],
                          "Description": []}

        self.URL = f"{url}"
        self.BaseURL = "https://www.northpointcity.com.sg/"

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
        # getting Shops URLs by calling the url extractor Description
        data = self.getShopData()
        res_urls = data[0]
        names = data[1]
        for url, name in zip(res_urls, names):
            print(f'Scrapping data of "{name}"')
            response = requests.get(url)
            # making soap of every url page getting from Description of Shops

            urlSoap = BeautifulSoup(response.text, 'html.parser')
            # print(urlSoap)
            if urlSoap is not None:

                # Finding Description of Restaurants

                description_div = urlSoap.find('div', class_="textbody")

                if description_div is not None:

                    description = description_div.text.replace("\n", " ").replace("  ", "").replace('\u00a0',
                                                                                                    " ").replace('\r',
                                                                                                                 "").replace(
                        "\"", "")

                    shop_description_list.append(description)
                else:
                    shop_description_list.append("Not available")
            else:

                shop_description_list.append("Not Available")

        self.DATA_DICT['Description'] = shop_description_list

    def getShopData(self):

        soap = self.getShopSoap()

        shop_urls_list = []
        shop_name_list = []
        shop_address_list = []
        shop_number_list = []
        # Shop URLs
        if soap is not None:
            list_of_restaurants = soap.findAll('div', class_="storename")
            for index, shopurl in enumerate(list_of_restaurants):
                url = shopurl.find('a')
                if url is not None:
                    shop_urls_list.append(self.BaseURL + url['href'])
                    # print(f"{index} Scrapping Details FOR  {self.BaseURL + url['href']}")
                else:
                    shop_urls_list.append("Not Available")
                    print("Info Not Available")
                # Shop Names
                shop_name = shopurl.text.replace('\n', "")
                if shop_name is not None:
                    shop_name_list.append(shop_name)
                else:
                    shop_name_list.append("Not Available")
            # print(len(shop_name_list))
            # Shop Address
            list_of_shop_address = soap.findAll('div', class_="col findus")
            for shopAddress in list_of_shop_address:
                if shopAddress is not None:
                    shop_address_list.append(shopAddress.findNext('div', class_='info').text)
                else:
                    shop_address_list.append("Not Available")
            list_of_shop_number = soap.findAll('div', class_='col callus')
            for shopNumbar in list_of_shop_number:
                if shopNumbar is not None:
                    shop_number_list.append(shopNumbar.findNext('div', class_="info").text)
                else:
                    shop_number_list.append("Not Available")
        else:
            shop_address_list.append("Not Available")
            shop_urls_list.append("Not Available")
            shop_name_list.append("Not Available")

        self.DATA_DICT['Shop Name'] = shop_name_list
        self.DATA_DICT['ShopAddress'] = shop_address_list
        self.DATA_DICT['Phone Number'] = shop_number_list
        self.DATA_DICT['Shop URL'] = shop_urls_list
        return shop_urls_list, shop_name_list

    def getShopSoap(self):
        print("Scrapping Process start")
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.URL)
        print("Loading....")
        print("Loading website All data")
        while True:
            driver.implicitly_wait(10)
            try:
                driver.find_element(By.XPATH, "/html/body/div[2]/section/a").click()
            except:
                break
        driver.implicitly_wait(10)
        sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.close()
        return soup
