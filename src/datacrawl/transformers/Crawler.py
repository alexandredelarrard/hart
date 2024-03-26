import os
import time
import tqdm
import logging
import pickle
from datetime import datetime

from typing import List, Dict
from queue import Queue
from threading import Thread
from omegaconf import DictConfig

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.utils.utils_crawler import encode_file_name

class StepCrawling(Step):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int, 
                 text_only : bool = False,
                 save_in_queue : bool = False,
                 save_queue_size_step : int = 100):

        super().__init__(context=context, config=config)
        
        self.threads = threads
        self.text_only = text_only
        self.save_in_queue = save_in_queue
        self.save_queue_size_step = save_queue_size_step
        self.save_queue_path = "./data"

        self.missed_urls = []
        self.queues = {"drivers": Queue(), "urls" :  Queue(), "results": Queue()}

    @timing
    def run(self, liste_urls : List, function_crawling):

        # initialize the drivers 
        self.initialize_queue_drivers()

        # initalize the urls queue
        self.initialize_queue_urls(liste_urls)

        # start the crawl
        self.start_threads_and_queues(function_crawling)

        t0 = time.time()
        self.queues["urls"].join()
        self._log.info('*** Done in {0}'.format(time.time() - t0))

        self.close_queue_drivers()


    def initialize_driver_firefox(self):
        """
        Initialize the web driver with Firefox driver as principal driver geckodriver
        parameters are here to not load images and keep the default css --> make page loading faster
        """

        firefox_profile = webdriver.FirefoxProfile()

        firefox_profile.set_preference('permissions.default.stylesheet', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        firefox_profile.set_preference('disk-cache-size', 8000)
        firefox_profile.set_preference("http.response.timeout", 300)
        firefox_profile.set_preference("dom.disable_open_during_load", True)

        if self.text_only:
            firefox_profile.set_preference('permissions.default.image', 2)

        firefox_profile.set_preference("network.proxy.type", 1)
        self.current_proxy_index = (self.current_proxy_index +1)%len(self.proxies)

        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        driver = webdriver.Firefox(capabilities=firefox_capabilities)
        # log_path= os.environ["DIR_PATH"] + "/crawling/geckodriver.log" 
        driver.delete_all_cookies()
        driver.set_page_load_timeout(300) 

        return driver
    
    
    def initialize_driver_chrome(self):
        """
        Initialize the web driver with chrome driver as principal driver chromedriver.exe, headless means no open web page. But seems slower than firefox driver  
        parameters are here to not load images and keep the default css --> make page loading faster
        """
        
        options = Options()

        prefs = {
                'disk-cache-size': 8000,
                "profile.default_content_setting_values.notifications":2,
                "profile.managed_default_content_settings.stylesheets":2,
                "profile.managed_default_content_settings.cookies" : 2,
                "profile.managed_default_content_settings.plugins":2,
                "profile.managed_default_content_settings.geolocation":2,
                "profile.managed_default_content_settings.media_stream":2,
                }
        
        if self.text_only:
            prefs["profile.managed_default_content_settings.cookies"] = 2
            prefs["profile.managed_default_content_settings.javascript"] = 2
            prefs["profile.managed_default_content_settings.images"] = 2
            prefs["profile.managed_default_content_settings.css"] = 2
            prefs["profile.managed_default_content_settings.popups"] = 2
            
        options.add_experimental_option("prefs", prefs)

        # if self.text_only:
            # options.add_argument("--headless") # Runs Chrome in headless mode.
        
        options.add_argument("--incognito")
        options.add_argument('--no-sandbox') # Bypass OS security model
        options.add_argument('--disable-gpu')  # applicable to windows os only
        # options.add_argument('start-maximized') 

        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        options.add_argument("--enable-javascript")

        driver = webdriver.Chrome(options=options)
        driver.delete_all_cookies()
        driver.set_page_load_timeout(300) 

        return driver


    def delete_driver(self, driver):
        driver.close()

    def restart_driver(self, driver):

        try:
            self.delete_driver(driver)
        except Exception:
            self._log.info("ALREADY DELETED")
            pass

        driver = self.initialize_driver_chrome()

        return driver

    
    def initialize_queue_drivers(self):
        for _ in range(self.threads):
             self.queues["drivers"].put(self.initialize_driver_chrome())
        self._log.info(f"DRIVER QUEUE INITIALIZED WITH {self.threads} drivers")
    
    def initialize_queue_urls(self, urls=[]):
        for url in urls:
             self.queues["urls"].put(url)
        

    def close_queue_drivers(self):

        for i in range(self.queues["drivers"].qsize()):
            driver = self.queues["drivers"].get()
            driver.close()

    
    def start_threads_and_queues(self, function):

        for _ in range(self.threads):
            t = Thread(target= self.queue_calls, args=(function, self.queues, )) # self.configs no longer used
            t.daemon = True
            t.start()


    def get_url(self, driver, url):

        try:
            driver.get(url)
        except Exception:
            pass
        
        return driver


    def queue_calls(self, function, queues, *args):
        
        queue_url = queues["urls"]
        missed_urls = []
        
        #### extract all articles
        while True:
            driver = queues["drivers"].get()
            url = queue_url.get()

            try:
                driver = self.get_url(driver, url)
                driver, information = function(driver, *args)

                if self.save_in_queue:
                    queues["results"].put(information)

                    if queues["results"].qsize() == self.save_queue_size_step:
                        file_name = encode_file_name(url)
                        self.save_queue_to_file(queues["results"], 
                                                path=self.save_queue_path +
                                                f"/{file_name}.pickle")

                queues["drivers"].put(driver)
                queue_url.task_done()

                self._log.info(f"[OOF {queue_url.qsize()}] CRAWLED URL {url}")
            
            except Exception as e:
                logging.error(url, e)
                missed_urls.append(url)
                queue_url.task_done()
                queues["drivers"].put(driver)

            self.missed_urls = missed_urls

            if queue_url.qsize() == 0:
                file_name = encode_file_name(url)
                self.save_queue_to_file(queues["results"], 
                                        path=self.save_queue_path +
                                        f"/{file_name}.pickle")

    def save_queue_to_file(self, queue, path):
        infos = []
        while queue.qsize() !=0:
            infos.append(queue.get())
        self.save_infos(infos, path)
        
    def save_infos(self, df, path):

        if ".csv" in path:
            df.to_csv(path, index=False, sep=";")
        elif ".txt" in path or ".pickle" in path:
            with open(path, "wb") as f:
                pickle.dump(df, f)
        else:
            self._log.error("Extensions handled for saving files are .TXT / .PICKLE or .CSV only. Please try again")

    def scrowl_driver(self, driver, Y):
        driver.execute_script(f"window.scrollTo(0, window.scrollY + {Y});")

    def get_element_infos(self, element, attribute, attribute_desc, type="text"):
        try: 
            if type == "text":
                return element.find_element(eval(f"By.{attribute.upper()}"), attribute_desc).text
            else:
                return element.find_element(eval(f"By.{attribute.upper()}"), attribute_desc).get_attribute(type)
        except Exception:
            return ""
        
    def click_element(self, element, attribute, attribute_desc):
        try: 
            element.find_element(eval(f"By.{attribute.upper()}"), attribute_desc).click()
        except Exception:
            pass
        
    def send_keys_element(self, element, attribute, attribute_desc, key):
        try: 
            if key:
                element.find_element(eval(f"By.{attribute.upper()}"), attribute_desc).send_keys(key)
        except Exception:
            pass

    def get_value_of_css_element(self, element, attribute, attribute_desc, key):
        try: 
            if key:
               return element.find_element(eval(f"By.{attribute.upper()}"), attribute_desc).value_of_css_property(key)
        except Exception:
                return ""

    def get_elements(self, element, attribute, attribute_desc) -> List:
        try:
            return element.find_elements(eval(f"By.{attribute.upper()}"), attribute_desc)
        except Exception:
            return []
        
    def get_solo_element(self, element, attribute, attribute_desc) -> List:
        try:
            return element.find_element(eval(f"By.{attribute.upper()}"), attribute_desc)
        except Exception:
            return []
        
    def get_info_from_step_value(self, driver, step_values):

        if "by_type" not in step_values.keys():
            if "attribute" in step_values.keys():
                info = driver.get_attribute(step_values["attribute"])
            elif "value_of_css_element" in step_values.keys():
                info = driver.value_of_css_property(step_values["value_of_css_element"])
            else:
                info = driver.text
                
        else:
            if "value_of_css_element" in step_values.keys():
                info = self.get_value_of_css_element(driver, 
                                    step_values["by_type"], 
                                    step_values["value_css"],
                                    key=step_values["value_of_css_element"])
                
            elif "attribute" in step_values.keys():
                info = self.get_element_infos(driver, 
                                    step_values["by_type"], 
                                    step_values["value_css"],
                                    type=step_values["attribute"])
            else:
                info = self.get_element_infos(driver, 
                                    step_values["by_type"], 
                                    step_values["value_css"])
            
            if "replace" in step_values.keys():
                info = info.replace(step_values["replace"][0], 
                                    step_values["replace"][1]).strip()
            
            if "split" in step_values.keys():
                info = info.split(step_values["split"]["character"])

                if step_values["replace"]["id_split"]:
                    info = info[step_values["split"]["id_split"]]

        return info
    
    
    def extract_element_infos(self, driver, config):

        lot_info = {}

        # get infos 
        for step, step_values in config.items(): 
            lot_info[step] = self.get_info_from_step_value(driver, step_values)
        
        return lot_info
    

    def crawl_iteratively(self, driver, 
                          config : Dict):

        list_infos = []
        liste_lots = self.get_elements(driver, 
                                       config.liste_elements.by_type, 
                                       config.liste_elements.value_css)
        # save pict
        for lot in tqdm.tqdm(liste_lots):

            lot_info = {} 
            
            try:
                if "functions" in config.keys():
                    for function in config.functions:
                        eval(function)

                new_info = self.extract_element_infos(lot, config.per_element)
                lot_info.update(new_info)
                
                list_infos.append(lot_info)
            
            except Exception as e:
                self._log.warning(f"ERROR happened for URL {driver.current_url} - {e}")

        return list_infos