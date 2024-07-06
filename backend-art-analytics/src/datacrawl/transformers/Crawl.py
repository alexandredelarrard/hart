import time
import logging
from typing import List, Dict
import os
import stem.process
from queue import Queue
from threading import Thread
from omegaconf import DictConfig

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        self.save_queue_path = self._config.crawling.root_path
        self.tor_path = os.environ["TOR_PATH"]

        # kwargs args
        self._log.info(f"KWARGS = {kwargs}")
        self.proxy = kwargs["kwargs"].get("proxy", False)
        self.is_picture = kwargs["kwargs"].get("is_picture", True)
        self.is_cookie = kwargs["kwargs"].get("is_cookie", True)
        self.is_javascript = kwargs["kwargs"].get("is_javascript", True)

        if save_queue_path:
            self.save_queue_path = save_queue_path

        # if self.proxy:
        #     self.launch_tor()
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

    def initialize_driver_firefox(self):
        """
        Initialize the web driver with Firefox driver as principal driver geckodriver
        parameters are here to not load images and keep the default css --> make page loading faster
        """

        firefox_profile = webdriver.FirefoxProfile()

        firefox_profile.set_preference("permissions.default.stylesheet", 2)
        firefox_profile.set_preference(
            "dom.ipc.plugins.enabled.libflashplayer.so", "false"
        )
        firefox_profile.set_preference("disk-cache-size", 8000)
        firefox_profile.set_preference("http.response.timeout", 300)
        firefox_profile.set_preference("dom.disable_open_during_load", True)

        if self.text_only:
            firefox_profile.set_preference("permissions.default.image", 2)

        firefox_profile.set_preference("network.proxy.type", 1)
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)

        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities["marionette"] = True

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

        if self.proxy:
            PROXIES = {
                "http": "socks5://localhost:9050",
                "https": "socks5://localhost:9050",
            }
            # options.add_argument('--proxy-server=%s' % '127.0.0.1:8118')

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
        # options.add_argument("--headless") # Runs Chrome in headless mode.

        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-gpu")  # applicable to windows os only
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-extensions")
        options.add_argument("--enable-javascript")
        options.add_argument("--window-size=1125,955")
        # # options.add_argument('start-maximized')

        driver = webdriver.Chrome(options=options)
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

        queue_url = queues["urls"]
        self.missed_urls = []

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
                        save_queue_to_file(
                            queues["results"],
                            path=self.save_queue_path + f"/{file_name}.pickle",
                        )

                queues["count"].put(information)

                if queues["count"].qsize() % self.count_to_restart_driver == 0:
                    driver = self.restart_driver(driver)
                    with queues["count"].mutex:
                        queues["count"].queue.clear()

                queues["drivers"].put(driver)
                queue_url.task_done()

                self._log.info(f"[OOF {queue_url.qsize()}] CRAWLED URL {url}")

            except Exception as e:
                logging.error(url, e)
                self.missed_urls.append(url)
                queue_url.task_done()
                queues["drivers"].put(driver)

            if queue_url.qsize() == 0:
                file_name = encode_file_name(url)
                save_queue_to_file(
                    queues["results"],
                    path=self.save_queue_path + f"/{file_name}.pickle",
                )
