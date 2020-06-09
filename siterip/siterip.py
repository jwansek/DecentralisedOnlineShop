import xml.etree.ElementTree as etree
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
import urllib.request
import imagehash
import time
import json
import sys
import re
import os

sys.path.append(os.path.join("..", "serverSide"))
import serverDatabase

IMAGES_DIR = os.path.join("..", "serverSide", "images")

class Browser:
    def __enter__(self):
        self.browser = webdriver.Firefox()
        return self

    def __get_element_text(self, xpath):
        try:
            return self.browser.find_element(By.XPATH, xpath).text
        except selenium.common.exceptions.NoSuchElementException:
            return None

    def __get_imurl_from_css(self, css):
        return re.findall('\"(.*)\"', css)[0].split("?")[0]

    def __dl_img(self, imurl):
        req = urllib.request.Request(imurl, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_5_8) AppleWebKit/534.50.2 (KHTML, like Gecko) Version/5.0.6 Safari/533.22.3'})
        mediaContent = urllib.request.urlopen(req).read()
        with open(os.path.join(IMAGES_DIR, "temp.jpg"), "wb") as f:
            f.write(mediaContent)
        filename = str(imagehash.average_hash(Image.open(os.path.join(IMAGES_DIR, "temp.jpg")))) + ".jpg"
        os.rename(os.path.join(IMAGES_DIR, "temp.jpg"), os.path.join(IMAGES_DIR, filename))
        return filename

    def __get_images(self):
        elements = self.browser.find_elements(By.CLASS_NAME, 's7thumb')
        impaths = []

        if elements == []:
            # there's just one image so the HTML isnt there, so try fallback
            try:
                element = self.browser.find_element(By.CLASS_NAME, 's7staticimage').find_element_by_css_selector("*")
                return [self.__dl_img(element.get_attribute("src").split("?")[0])]
            except:
                #if it fails return [] which tells it to retry
                return []
        elif elements is None:
            return []
        else:
            try:
                for element in elements:
                    css = element.get_attribute("style")
                    imurl = self.__get_imurl_from_css(css)
                    impath = self.__dl_img(imurl)
                    impaths.append(impath)
            except:
                return []

        return impaths


    def __get_category(self):
        return self.browser.current_url.split("/")[4]

    def __get_related_products(self):
        return [get_id_from_url(i.get_attribute("href")) for i in self.browser.find_elements(By.CLASS_NAME, "co-product__anchor")]

    def rip_page(self, url, calls=0, maxcalls=3, title=None, category=None, impaths=None):
        id_ = get_id_from_url(url)
        if calls == maxcalls:
            append_to_errored(id_)
            print("Gave up on ", id_)
            return None

        self.browser.get(url)
        time.sleep(1)
        if category is None:
            category = self.__get_category()
        if impaths is None:
            impaths = self.__get_images()
        if title is None:
            title = self.__get_element_text("/html/body/div[4]/div[2]/section/main/div[2]/div[2]/div[1]/div[1]/h1")
            if title is None:
                title = self.__get_element_text('//*[@id="main-content"]/main/div[2]/div[2]/div[1]/div[1]/h1')

        objout = {
            "id": id_,
            "title": title,
            "impaths": impaths,
            "category": category,
            "weight":  self.__get_element_text("/html/body/div[4]/div[2]/section/main/div[2]/div[2]/div[1]/div[1]/div/div"),
            "price": self.__get_element_text("/html/body/div[4]/div[2]/section/main/div[2]/div[2]/div[1]/div[2]/div/strong"),
            "prod_info": self.__get_element_text("/html/body/div[4]/div[2]/section/main/div[2]/div[2]/div[3]/div/div[2]/div[1]/div[2]"),
            "nutritional_info": self.__get_element_text("/html/body/div[4]/div[2]/section/main/div[2]/div[2]/div[3]/div/div[2]/div[4]/div[2]"),
            "storage_info": self.__get_element_text("/html/body/div[4]/div[2]/section/main/div[2]/div[2]/div[3]/div/div[2]/div[6]/div[2]"),
            "related": self.__get_related_products()
        }

        if id_ == category or impaths == [] or title is None:
            print("Trying again on ", id_)
            # print(json.dumps(objout, indent = 4))
            return self.rip_page(url, calls=calls+1, title=title, category=category, impaths=impaths)
        else:
            append_to_completed(id_)
            print("Successfully got data on ", id_)
            # print(json.dumps(objout, indent = 4))
            return objout

    def __exit__(self, type, value, traceback):
        self.browser.quit()

def get_id_from_url(url):
    return re.findall(r"\d+", url)[0]

def get_product_urls():
    out = []
    tree = etree.parse("sitemap-products.xml")
    root = tree.getroot()

    for child in reversed(list(root)):
        out.append(child[0].text)
    return out

def append_to_completed(id_):
    with open("completed.csv", "a") as file:
        file.write(id_ + "\n")

def append_to_errored(id_):
    with open("failed.csv", "a") as file:
        file.write(id_ + "\n")

def get_completed():
    with open("completed.csv", "r") as f:
        return f.read().splitlines()

def main():
    with Browser() as browser:
        with serverDatabase.ServerDatabase() as db:
            for product_url in get_product_urls():
                if get_id_from_url(product_url) in get_completed():
                    print("Skipping id... Already processed")
                    continue

                pagedata = browser.rip_page(product_url)
                if pagedata is None:
                    continue

                try:
                    db.add_product(pagedata)
                except Exception as e:
                    print("ERROR", e)

if __name__ == "__main__":
    main()
    # with Browser() as browser:
    #     print(browser.rip_page("https://groceries.asda.com/product/1000000413919"))

