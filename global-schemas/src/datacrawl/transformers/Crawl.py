import time
import logging
from typing import List, Dict
import os
import stem.process
from queue import Queue
from threading import Thread
from pathlib import Path
from omegaconf import DictConfig

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path

from src.context import Context
from src.utils.step import Step
from src.utils.timing import timing

from src.utils.utils_crawler import encode_file_name, save_queue_to_file


class Crawl(Step):

    def __init__(
        self,
        context: Context,
        config: DictConfig,
        threads: int = 1,
        save_in_queue: bool = False,
        save_queue_size_step: int = 100,
        save_queue_path: str = None,
        **kwargs: Dict,
    ):

        super().__init__(context=context, config=config)

        self.threads = threads

        self.save_in_queue = save_in_queue
        self.save_queue_size_step = save_queue_size_step
        self.save_queue_path = self._context.paths["CRAWL"]
        self.tor_path = os.environ["TOR_PATH"]

        # kwargs args
        self._log.info(f"KWARGS = {kwargs}")
        self.proxy = kwargs["kwargs"].get("proxy", False)
        self.is_picture = kwargs["kwargs"].get("is_picture", True)
        self.is_cookie = kwargs["kwargs"].get("is_cookie", True)
        self.is_javascript = kwargs["kwargs"].get("is_javascript", True)

        if save_queue_path:
            self.save_queue_path = save_queue_path

        self.count_to_restart_driver = 8000 // threads

        self.missed_urls = []
        self.queues = {
            "drivers": Queue(),
            "urls": Queue(),
            "results": Queue(),
            "count": Queue(),
        }
        self._log.debug(
            f"SAVE QUEUE: {save_in_queue} | QUEUE SIZE SAVE {save_queue_size_step} | QUEUE PATH SAVE {save_queue_path}"
        )

    @timing
    def run(self, liste_urls: List, function_crawling):

        if len(liste_urls) != 0:
            # initialize the drivers
            self.initialize_queue_drivers()

            # initalize the urls queue
            self.initialize_queue_urls(liste_urls)

            # start the crawl
            self.start_threads_and_queues(function_crawling)

            t0 = time.time()
            self.queues["urls"].join()
            self._log.info("*** Done in {0}".format(time.time() - t0))

            self.close_queue_drivers()
        else:
            self._log.info("Already up to date")

    def initialize_driver_chrome(self):
        """
        Initialize the web driver with chrome driver as principal driver chromedriver.exe, headless means no open web page. But seems slower than firefox driver
        parameters are here to not load images and keep the default css --> make page loading faster
        """

        options = Options()

        prefs = {
            "disk-cache-size": 8000,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            "profile.managed_default_content_settings.popups": 2,
        }

        if not self.is_javascript:
            prefs["profile.managed_default_content_settings.javascript"] = 2
            prefs["profile.managed_default_content_settings.css"] = 2

        if not self.is_picture:
            prefs["profile.managed_default_content_settings.images"] = 2

        if not self.is_cookie:
            prefs["profile.managed_default_content_settings.cookies"] = 2

        options.add_experimental_option("prefs", prefs)

        # if self.text_only:
        # options.add_argument("--headless")  # Runs Chrome in headless mode.
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-gpu")  # applicable to windows os only
        options.add_argument(
            "--disable-dev-shm-usage"
        )  # Overcome limited resource problems
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-extensions")
        options.add_argument("--enable-javascript")
        options.add_argument("--window-size=1125,955")
        # options.add_argument("--remote-debugging-port=9222")

        svc = webdriver.ChromeService(executable_path=binary_path)
        driver = webdriver.Chrome(options=options, service=svc)
        driver.delete_all_cookies()
        driver.set_page_load_timeout(300)

        return driver

    def launch_tor(self):
        tor_process = stem.socket.launch_tor_with_config(
            config={
                "SocksPort": str(self._config.crawling.tor_config.SocksPort),
                "EntryNodes": self._config.crawling.tor_config.EntryNodes,
                "ExitNodes": self._config.crawling.tor_config.ExitNodes,
                "CookieAuthentication": self._config.crawling.tor_config.CookieAuthentication,
                "MaxCircuitDirtiness": self._config.crawling.tor_config.MaxCircuitDirtiness,
            },
            tor_cmd=self.tor_path,
        )

    def delete_driver(self, driver):
        driver.close()
        time.sleep(1)

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
            self.delete_driver(driver)

    def start_threads_and_queues(self, function):

        for _ in range(self.threads):
            t = Thread(
                target=self.queue_calls,
                args=(
                    function,
                    self.queues,
                ),
            )  # self.configs no longer used
            t.daemon = True
            t.start()

    def get_url(self, driver, url):

        try:
            driver.get(url)
        except Exception:
            pass

        return driver

    def queue_calls(self, function, queues, *args):

        #### extract all articles
        while True:
            driver = queues["drivers"].get()
            url = queues["urls"].get()

            try:
                driver = self.get_url(driver, url)
                driver, information = function(driver, *args)

                if self.save_in_queue:
                    queues["results"].put(information)
                    if queues["results"].qsize() == self.save_queue_size_step:
                        file_name = encode_file_name(url)
                        save_queue_to_file(
                            queues["results"],
                            path=self.save_queue_path / Path(f"{file_name}.pickle"),
                        )

                queues["count"].put(information)

                if queues["count"].qsize() % self.count_to_restart_driver == 0:
                    driver = self.restart_driver(driver)
                    with queues["count"].mutex:
                        queues["count"].queue.clear()

            except Exception as e:
                logging.error(url, e)

            queues["urls"].task_done()
            if queues["urls"].qsize() == 0:
                break
            else:
                queues["drivers"].put(driver)

            self._log.info(f"[OOF {queues['urls'].qsize()}] CRAWLED URL {url}")

            if queues["urls"].qsize() == 0 and self.save_in_queue:
                file_name = encode_file_name(url)
                save_queue_to_file(
                    queues["results"],
                    path=self.save_queue_path / Path(f"/{file_name}.pickle"),
                )

        # when all urls are done then kill the driver
        self.delete_driver(driver)
