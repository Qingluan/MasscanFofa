import requests
import re
import os
import time
from .lib import Panel
from DrMoriaty.utils.log import SwordPrint, colored, gprint

class Sender(Panel):

    def __init__(self, target, key, prefix="->|", tail="|<-", headers=None, proxy=None, encoding='UTF-8'):
        super().__init__()
        self.set_on_keyboard_listener('c', Panel.CMD_MODE, self.on_cmd)
        self.set_on_keyboard_listener('s', Panel.CMD_MODE, self.on_preview)
        
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
        self.op = ''
        self.sub_dir = {}
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

    def preview(self):
        if not self.if_is_dir(self.select_now):
            
            content = self.readfile(os.path.join(self.pwd, self.select_now))
            self.show_file(content)

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

        self.show(now_dirs = dirs, sub_dir=sub_dir, op=now)
        
    def show(self, cmd_result=None, pwd=None, now_dirs=None, select_now=None, sub_dir=None, op=None):
        if not cmd_result:
            cmd_result = self.cmd_result
        if not pwd:
            pwd = self.pwd
        if not now_dirs:
            now_dirs = list(self.now_dirs.keys())
        if not select_now:
            select_now = self.select_now
            if not self.select_now:
                select_now = list(self.now_dirs.keys)[0]

        if not sub_dir:
            sub_dir = list(self.sub_dir.keys())

        if not op:
            op = self.op

        SwordPrint(cmd_result, pwd=pwd, dir=now_dirs, select=select_now, sub_dir=sub_dir, op=op)

    def show_file(self, content):
        self.flush()
        s = str(time.time())
        with open("/tmp/%s" % s , 'w') as fp:
            fp.write(content)
        os.system("vi /tmp/%s" % s)


    def do_cmd(self):
        local_server = 'server'
        self.show()
        while 1:
            self.prompt = colored("(%s)" % local_server, 'blue') + colored(self.pwd, 'red', attrs=['underline'])
            os.system('tput cup %d 0' % self.SIZE[0])
            res = input(self.prompt).strip()
            
            if res == 'exit':
                return True
            elif res == 'local':
                local_server = 'local'
                self.flush()
                continue
            elif res == 'server':
                local_server = 'server'
                self.flush()
                continue
            elif res.startswith("upload"):
                files = res.split()[1:]
                for file in files:
                    if os.path.exists(file):
                        self.upload(file)
                self.flush()
                self.ls(self.pwd)
                self.show()
                continue

            self.flush()
            if local_server == 'local':
                try:
                    res = os.popen(res).read()
                    err = ''
                except Exception as e:
                    err = str(e)
            else:
                res,err = self.cmd(res)


            if err:
                self.cmd_result = err
            else:
                self.cmd_result = res
            self.show()
