import tqdm
import base64
import re
from typing import List
from omegaconf import DictConfig

from selenium.webdriver.common.by import By
from src.context import Context
from src.datacrawl.transformers.Crawl import Crawl

class Crawling(Crawl):
    
    def __init__(self, 
                 context : Context,
                 config : DictConfig,
                 threads : int = 1, 
                 text_only : bool = False,
                 save_in_queue : bool = False,
                 save_queue_size_step : int = 100,
                 save_queue_path: str = None,
                 proxy: bool = False):

        super().__init__(context=context, 
                         config=config, 
                         threads=threads, 
                         text_only=text_only, 
                         save_in_queue=save_in_queue, 
                         save_queue_size_step=save_queue_size_step,
                         save_queue_path=save_queue_path,
                         proxy=proxy)

    def scrowl_driver(self, driver, Y):
        driver.execute_script(f"window.scrollTo(0, window.scrollY + {Y});")

    def get_page_number(self, driver, by_type, value_css, divider):

        page_nbr = self.get_element_infos(driver, by_type, value_css)
        count_pages = 1

        if page_nbr != "":
            page_nbr = re.findall("(\\d+)", page_nbr)
            if len(page_nbr) !=0:
                page_nbr = page_nbr[0]
                count_pages = (int(page_nbr) // divider) + 1

        self._log.debug(f"{count_pages} to crawl")
        return count_pages

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
        
    def get_picture_url_from_canvas(self, element, attribute, attribute_desc):
        try:
            canvas = self.get_solo_element(element, attribute, attribute_desc)
            canvas64 = element.execute_script("return arguments[0].toDataURL('image/png', 1.0).substring(21);", canvas)
            return base64.b64decode(canvas64)
        except Exception:
            return ""
        
    def get_info_from_step_value(self, element, step_values):

        if "by_type" not in step_values.keys():
            if "attribute" in step_values.keys() and "attribute" != "text":
                info = element.get_attribute(step_values["attribute"])
            elif "value_of_css_element" in step_values.keys():
                info = element.value_of_css_property(step_values["value_of_css_element"])
            else:
                info = element.text
                
        else:
            if "value_of_css_element" in step_values.keys():
                info = self.get_value_of_css_element(element, 
                                    step_values["by_type"], 
                                    step_values["value_css"],
                                    key=step_values["value_of_css_element"])
                
            elif "is_canvas" in step_values.keys():
                info = self.get_picture_url_from_canvas(element, 
                                    step_values["by_type"], 
                                    step_values["value_css"])
                
            elif "attribute" in step_values.keys():
                info = self.get_element_infos(element, 
                                    step_values["by_type"], 
                                    step_values["value_css"],
                                    type=step_values["attribute"])
            else:
                info = self.get_element_infos(element, 
                                    step_values["by_type"], 
                                    step_values["value_css"])
        if "split" in step_values.keys():
            info = info.split(step_values["split"]["character"])

            if step_values["split"]["id_split"]:
                info = info[step_values["split"]["id_split"]]

        if "replace" in step_values.keys():
            info = info.replace(step_values["replace"][0], 
                                step_values["replace"][1]).strip()

        return info
    
    def extract_element_infos(self, lot, config):

        lot_info = {}
        
        for step, step_values in config.items(): 
            self._log.debug(f"EXTRACT VALUE: {step_values}")
            if "liste_elements" in step_values.keys():
                liste_lots = self.get_elements(lot, 
                                                step_values.liste_elements.by_type, 
                                                step_values.liste_elements.value_css)
                lot_info[step] = []
                for sub_lot in liste_lots:
                    lot_info[step].append(self.get_info_from_step_value(sub_lot, step_values.per_element))
            else:
                lot_info[step] = self.get_info_from_step_value(lot, step_values)
        
        return lot_info
    
    def crawl_iteratively(self, driver, 
                          config : DictConfig):

        list_infos = []
        liste_lots = []

        if "liste_elements" in config.keys():
            liste_lots = self.get_elements(driver, 
                                        config.liste_elements.by_type, 
                                        config.liste_elements.value_css)
        # at least one run
        if len(liste_lots) ==0:
            liste_lots = [self.get_solo_element(driver, "TAG_NAME", "body")]

        # save pict
        for lot in tqdm.tqdm(liste_lots):

            lot_info = {} 

            try:
                # global info from driver level
                if "global_element" in config.keys():
                    new_info = self.extract_element_infos(driver, config.global_element)
                    lot_info.update(new_info)
            
                if "functions" in config.keys():
                    for function in config.functions:
                        eval(function)

                if "per_element" in config.keys():
                    new_info = self.extract_element_infos(lot, config.per_element)
                    lot_info.update(new_info)
                    
                lot_info["CURRENT_URL"] = driver.current_url
                list_infos.append(lot_info)
            
            except Exception as e:
                self._log.warning(f"ERROR happened for URL {driver.current_url} - {e}")

        return list_infos