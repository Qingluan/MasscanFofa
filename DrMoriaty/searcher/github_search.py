 
import requests
import getpass
import os
from bs4 import BeautifulSoup
import pickle, json
from qlib.net import to
from DrMoriaty.utils.log import Tprint,gprint,rprint, colored
from DrMoriaty.utils.setting import GITHUB_LOGIN, GITHUB_SESSION
from concurrent.futures.thread import ThreadPoolExecutor
from requestium import Session, Keys

class Github:
    def __init__(self, proxy=None):
        self.cookies = None
        self.sess = Session("/usr/local/phantomjs", "phantomjs", default_timeout=15)
        if proxy:
            self.sess.proxies['https'] = proxy
            self.sess.proxies['http'] = proxy
        self.proxy = proxy

    def save_session(self,name, password, cookie):
        gprint("save cred and session")
        with open(GITHUB_LOGIN,"wb") as fp:
            u = {"user":name, "pass":password}
            pickle.dump(u, fp)

        with open(GITHUB_SESSION, 'wb') as fp:
            pickle.dump(cookie, fp)

    def load_session(self):
        gprint("load seesion form github")
        if os.path.exists(GITHUB_SESSION):
            with open(GITHUB_SESSION, 'rb') as fp:
                self.cookies = pickle.load(fp)
                self.sess.cookies.update(self.cookies)
                self.sess.get("https://github.com")
                self.sess.transfer_session_cookies_to_driver()


        elif os.path.exists(GITHUB_LOGIN):
            with open(GITHUB_LOGIN,'rb') as fp:
                u = pickle.load(fp)
                self.login(name=u['user'], password=u['pass'])
        else:
            name = input('Github name:')
            passwd = getpass.getpass("Github pass:")
            self.login(name, passwd)

    def login(self, name=None, password=None):
        
        soup = BeautifulSoup(r1.text,features='lxml')
        s1 = soup.find(name='input',attrs={'name':'authenticity_token'}).get('value')
        r1_cookies = r1.cookies.get_dict()

        gprint("try login github")
        r1 = self.sess.driver.get('https://github.com/login') 
        self.sess.driver.find_element_by_css_selector("input[name=\"login\"]").send_keys(name)
        self.sess.driver.find_element_by_css_selector("input[name=\"password\"]").send_keys(password)
        self.sess.driver.find_element_by_css_selector("input[name=\"commit\"]").click()
        self.sess.transfer_driver_cookies_to_session()
        self.cookies = self.sess.cookies.get_dict()
        self.save_session(name, password, self.cookies)

    def weak_search(self,key):
        self.load_session()
        self.search(key,"smtp")
        self.search(key,"ssh")
        # with ThreadPoolExecutor(max_workers=10) as exe:
# 
            # for k in ['smtp', 'ssh', 'email']:
# 
                # s1 = exe.submit(self.search,key, k)
                # s1.add_done_callback(print)
            
            

    def search(self, *key):
        gprint(key[-1])
        if not self.cookies:
            self.load_session()
        url = "https://github.com/search?q={}&type=code".format("+".join(key))
        self.sess.driver.get(url)
        res = self.sess.driver.page_source
        b = BeautifulSoup(res, 'lxml')

        codes = b.select(".code-list-item")
        if len(codes) > 0:
            gprint("Found : %d" % len(codes))
        else:
            gprint("Not found:")
            gprint(b.text)
        ss = {}
        for code in codes:
            
            k = code.select(".text-bold")[0].text
            v = { colored(str(n),'green'):i.text.replace("\n","") for n,i in enumerate(code.select("td.blob-code"))}
            gprint(colored(k, "blue"))
            Tprint(v)
