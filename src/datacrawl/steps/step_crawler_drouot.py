import os
import urllib
import re
import glob
from omegaconf import DictConfig

import pandas as pd 
import tqdm
import time

from selenium.webdriver.common.by import By

from src.context import Context
from src.datacrawl.transformers.Crawler import StepCrawling

class StepCrawlingDrouot(StepCrawling):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int, 
                 object : str):

        super().__init__(context=context, config=config, threads=threads)
        self.object = object.replace(" ", "_")
        self.seller = "drouot"        
        self.root_url = self._config.crawling[self.seller].webpage_url + f"{object}?query={object}&type=result"

        #TODO : a déduire directement de la page
        self.pages = {#'meuble' : 1285, #64 000 picts  all -> ok
                      #"tableau" : 4288, #260 000 picts all -> ok
                      #"sac_a_main": 98, # seulement ceux avec encheres -> ok
                      #"argenterie": 9469, # seulement ceux avec encheres ->ok
                      #"table" : 2255, # seulement ceux avec encheres -> ok
                      #"fauteuil" : 976, # seulement ceux avec encheres -> ok
                      "lampe" : 3794,#  TODO
                      #"vase" : 3113, #-> seulement ceux avec encheres -> ok
                      "arme" : 2778} 
                      # TABLE CHAISE FAUTEUIL ARME LAMPE VASE BUFFET CONSOLE GUERIDON MIROIR

    def get_urls(self):
        
        liste_urls = [self.root_url + f"&page={x}" for x in range(1,self.pages[self.object]+1)]
        files_already_done = glob.glob(self._config.crawling[self.seller].save_data_path + "/*.csv")
        files_already_done = [self.root_url + "&page=" + x.split("_")[-1].replace(".csv","") 
                                                for x in files_already_done if self.object in x]

        liste_urls = list(set(liste_urls) - set(files_already_done))
        self._log.info(f"ALREADY CRAWLED {len(files_already_done)} REMAINING {len(liste_urls)}")

        return liste_urls
    
    
    def check_loggedin(self, driver, counter=0):

        mdp = os.environ[f"{self.seller.upper()}_MDP"]
        email = os.environ[f"{self.seller.upper()}_EMAIL"]

        header= driver.find_element(By.TAG_NAME, "header")

        if "Abonnez-vous" in header.text:
            time.sleep(3)
            loggin_tool = header.find_element(By.CLASS_NAME, "menuLinkConnection")
            loggin_tool.click()
            time.sleep(2)

            driver.find_element(By.ID, "authenticate-email").send_keys(email)
            time.sleep(2)
            driver.find_element(By.ID, "password").send_keys(mdp)
            time.sleep(1)

            driver.find_element(By.ID, "menuLoginButton0").click()
            time.sleep(3)

            header= driver.find_element(By.TAG_NAME, "header")
            if "Le Magazine" in header.text:
                return driver
            else:
                if counter < 2:
                    self.check_loggedin(driver, counter+1)
                else: 
                    raise Exception("CANNOT LOG IN TO DROUOT")

        else:
            return driver
        
    def get_page_number(self, driver):
        # get page number
        try:
            page_nbr = re.search('&page=([0-9]*)', driver.current_url).group(1)
        except Exception:
            page_nbr = driver.current_url.split("page=")[1]

        return page_nbr
    
    def get_picture_url(self, lot, driver, counter=0):
        
        try:
            time.sleep(0.3)
            style_tagname_pict = lot.find_element(By.CLASS_NAME, "imgLot").get_attribute("style")
            url_picture = re.findall(r'\((.*?)\)', style_tagname_pict)[-1].replace("\"", "")
            picture_id = url_picture.split("path=")[1].replace("/", "_")
            
            return picture_id, url_picture
        
        except Exception as e:
            if counter <3:
                driver.execute_script("window.scrollTo(0, window.scrollY + 220);")
                time.sleep(0.5)
                self.get_picture_url(lot, driver, counter+1)
            else:
                raise Exception(e)
        
        return "", ""


    def crawling_function(self, driver, config):

        # log in if necessary
        driver = self.check_loggedin(driver)

        page_nbr = self.get_page_number(driver)

        # crawl infos 
        crawl_conf = config.crawling[self.seller]
        image_path = crawl_conf.save_picture_path
        infos_path = crawl_conf.save_data_path
        message = ""

        list_infos = []
        time.sleep(1)
        
        liste_lots = driver.find_elements(By.CLASS_NAME, "Lot")

        # save pict
        for i, lot in tqdm.tqdm(enumerate(liste_lots)):
            driver.execute_script("window.scrollTo(0, window.scrollY + 200);")
            time.sleep(0.3)
            
            try:
                driver_desc = lot.find_element(By.CLASS_NAME, "descriptionLot")
                
                # infos vente
                infos = driver_desc.text 
                lot_number = infos.split("\n")[0].replace("Lot n° ", "")

                # desc vente
                vente = lot.find_element(By.CLASS_NAME, "infoVenteLot").text

                # save 
                url_deep_details = lot.find_element(By.TAG_NAME, "a").get_attribute("href")
                picture_id, url_picture = self.get_picture_url(lot, driver)

                # save pictures & infos
                if not os.path.isfile(image_path + f"/{picture_id}.jpg"):
                    if "https" in url_picture:
                        urllib.request.urlretrieve(url_picture, image_path + f"/{picture_id}.jpg")

                list_infos.append([lot_number, picture_id, infos, vente, url_picture, url_deep_details])
            
            except Exception as e:
                message = e 

        df_infos = pd.DataFrame(list_infos, columns= ["NUMBER_LOT", "PICTURE_ID", "INFOS", 
                                                      "SALE", "URL_PICTURE", "URL_FULL_DETAILS"])
        self.save_infos(df_infos, path=infos_path + f"/{self.object}_page_{page_nbr}.csv")
        time.sleep(2)
        
        return driver, message

