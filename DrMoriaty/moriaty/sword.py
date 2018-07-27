import requests
import re
import os

from .lib import Panel
from DrMoriaty.utils.log import SwordPrint

class Sender(Panel):

    def __init__(self, target, key, prefix="->|", tail="|<-", headers=None, proxy=None, encoding='UTF-8'):
        super().__init__()
        self.target = target
        self.key = key
        self.prefix = prefix
        self.tail = tail
        self.encoding = encoding

        self.sess = requests.Session()
        if headers and isinstance(headers, dict):
            self.sess.headers.update(headers)

        if proxy:
            self.sess.proxies['http'] = proxy
            self.sess.proxies['https'] = proxy

        self.pwd = None

        ## some var in controll

        self.select_now = None
        self.cmd_result = ''
        self.now_dirs = {}
        self.last_select = ''
        self.init()

    def init(self):
        raise NotImplementedError("must implement")
        


    def cd(self, path):
        self.pwd = os.path.join(self.pwd, path)
        return self.ls(self.pwd)

    def ls(self, path):
        raise NotImplementedError("must implement")

    def index(self):
        raise NotImplementedError("must implement")

    def cmd(self):
        raise NotImplementedError("must implement")

    def send(self, **kargs):
        res = self.sess.post(self.target, data=kargs)
        return res.text[res.text.find(self.prefix) + len(self.prefix) :res.text.rfind(self.tail)].strip()


    def move(self, now):
        dirs = None

        
        if now == "right":
            if self.if_is_dir(self.select_now):
                dirs = self.cd(self.select_now)
                if len(dirs) > 0:
                    self.select_now = dirs[0]

        elif now == "left":
            if self.last_select:
                self.select_now = self.last_select
            if self.pwd.endswith("/"):
                self.pwd = self.pwd[:-1]
            self.pwd = os.path.dirname(self.pwd)
            dirs = self.ls(self.pwd)
            self.select_now = list(self.now_dirs.keys())[0]
            
            

        elif now == 'down':
            dirs = self.ls(self.pwd)
            if dirs.index(self.select_now) < len(dirs)-1:
                self.select_now = dirs[dirs.index(self.select_now) + 1]

        elif now == "up":
            dirs = self.ls(self.pwd)
            if dirs.index(self.select_now) > 0:
                self.select_now = dirs[dirs.index(self.select_now) - 1]

        if dirs == None:
            dirs = self.ls(self.pwd)
        sub_dir = []
        if not self.select_now:
            self.select_now = dirs[0]
        if self.if_is_dir(self.select_now):
            sub_dir = self.ls(os.path.join(self.pwd, self.select_now), no_cd=True)
        SwordPrint(self.cmd_result, pwd=self.pwd, dir=dirs, select=self.select_now, sub_dir=sub_dir, op=now)
