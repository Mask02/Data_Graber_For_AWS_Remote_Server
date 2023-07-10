import datetime
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class FarEestShopDetails:
    def __init__(self, url, order_number):
        # initialized a dictionary to store the dara
        self.order_number = order_number
        self.DATA_DICT = {"Shop Name": [], "ShopAddress": [], "Phone Number": [], "Shop URL": [],
                          "Description": []}
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.URL = f"{url}"
        self.BaseURL = "https://www.fareastmalls.com.sg"

    def appendingDataInJSONfile(self):

        self.getShopData()
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
        order_id = "1"
        folder_path = 'Data'
        current_utc_datetime = datetime.datetime.utcnow()
        file_name = f"{order_id} - {current_utc_datetime.strftime('%Y-%m-%d__%H-%M')}.json"
        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists('Data'):
            os.mkdir(folder_path)
        with open(file_path, 'w', encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print("All Data Scrapped Successfully")

    def getShopData(self):

        # Clicking on load more button

        print("Scrapping Process start")
        self.driver.maximize_window()
        self.driver.get(self.URL)
        print("Loading.....")
        while True:
            try:
                element = self.driver.find_element(By.XPATH, '//*[@id="b-store"]/div[2]')
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                self.driver.implicitly_wait(10)
                button = self.driver.find_element(By.CLASS_NAME, 'b-load-more-shops')
                button.click()
            except:
                break
        # Getting data from website
        shop_urls_list = []
        shop_name_list = []
        shop_number_list = []
        shop_description_list = []
        shop_address_list = []

        list_of_shop = self.driver.find_elements(By.XPATH, "//section[@id='b-store']/div/div/a")
        # Shop URLs
        for shopurl in list_of_shop:
            if shopurl is not None:
                shop_urls_list.append(shopurl.get_attribute('href'))
            else:
                shop_urls_list.append("Not Available")
                print("Info Not Available")

        # Shop Names

        names_of_shops = self.driver.find_elements(By.XPATH,
                                                   "//section[@id='b-store']/div/div/a//span[@class='b-store-title']")
        for names_of_shop in names_of_shops:
            if names_of_shop is not None:
                shop_name_list.append(names_of_shop.text)
            else:
                shop_name_list.append("Not Available")
        shop_urls_list.pop()

        # Number, Description and Address of Shops
        try:
            for url, name in zip(shop_urls_list, shop_name_list):
                self.driver.get(url)
                print(f'Scrapping data of "{name}"')
                shop_number_and_address = self.driver.find_elements(By.XPATH, "//div[@id='b-shop-details']/div/div")
                # print(shop_number_and_address)
                if len(shop_number_and_address) == 2:
                    shop_number = shop_number_and_address[1]
                    shop_address = shop_number_and_address[0]
                    shop_number_list.append(shop_number.text)
                    shop_address_list.append(shop_address.text)
                else:
                    shop_address_list.append(shop_number_and_address[0].text)
                    shop_number_list.append("Not Available")
                shop_description_div = self.driver.find_element(By.ID, "b-shop-description")
                shop_description_list.append(shop_description_div.text)
        except:
            print("Some error occurred while scrapping number and description")
        self.DATA_DICT['ShopAddress'] = shop_address_list
        self.DATA_DICT['Shop Name'] = shop_name_list
        self.DATA_DICT['Shop URL'] = shop_urls_list
        self.DATA_DICT['Phone Number'] = shop_number_list
        self.DATA_DICT['Description'] = shop_description_list
