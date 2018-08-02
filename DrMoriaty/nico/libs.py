from io import StringIO
from io import BytesIO
from http.server import BaseHTTPRequestHandler

import os
import re
import time
import signal
from multiprocessing import Process, Manager, Lock
from cmd import Cmd
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from collections import Counter

import requests
from bs4 import BeautifulSoup as BS

from DrMoriaty.datas.data import use_mem_db, saveRequest, saveResponse, Host, BPData
from DrMoriaty.utils.log import gprint, rprint, tprint, colored,TablePrint, tabulate, L
from DrMoriaty.utils.daemon import Daemon
from DrMoriaty.dolch.lib import Panel
from DrMoriaty.setting import OPENER, BP_SESSION_DIR


from .proxy2 import main

lock = Lock()


class ParseRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        if isinstance(request_text, str):
            request_text = request_text.encode()
        assert isinstance(request_text, bytes) is True  
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
        if b'\r\n' in request_text: 
            self.req_body = request_text.split(b'\r\n')[-1]
        elif b'\n\r' in request_text:
            self.req_body = request_text.split(b'\n\r')[-1]
        else:
            self.req_body = b''

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


    def _replace_b(self, old, new):
        if isinstance(old, bytes):
            pre = old[:old.find(b'{{')]
            end = old[old.find(b'}}')+2:]
        else:
            pre = old[:old.find('{{')]
            end = old[old.find('}}')+2:]
        return pre + new + end

    def _replace_c(self, old, new):
        if isinstance(old, bytes):
            pre = old[:old.find(b'[[')]
            end = old[old.find(b']]')+2:]
        else:
            pre = old[:old.find('[[')]
            end = old[old.find(']]')+2:]
        return pre + new + end

    def _get_c(self, old):
        for i in re.findall(r'\[\[(.*)\]\]', old):
            if os.path.exists(i.strip()):
                w = []
                with open(i.strip()) as fp:
                    for l in fp:
                        w.append(l.strip())
                yield str(w).strip()

    def _eval_option(self, one):
        batch_words = []
        if os.path.exists(one.strip()):
            gprint("load file form : %s" % one)
            with open(one.strip()) as fp:
                for l in fp:
                    o = l.strip()
                    batch_words.append(o)
        else:
            try:
                if '[[' in one and ']]' in one:
                    # gprint("detect file in code")
                    tone = one
                    for d in self._get_c(tone):
                        # gprint("patch %s" % d)
                        one = self._replace_c(one, d)

                gprint("try parse from python code:\n %s" % colored(one, 'blue'))    
                w = eval(one)
                if isinstance(w, list):
                    batch_words = w
            except Exception as e:
                rprint(str(e))
                gprint("only as words")
                batch_words = one.split()
        return batch_words

    def _gen_map(self, data, now_da=[]):
        if isinstance(data, list) and len(data) > 1:
            f = data[0]
            for i in f:
                a = now_da + [i]
                yield from self._gen_map(data[1:], a)
        else:
            for i in data[0]:
                b = now_da + [ i]
                yield b


    def eval_and_replace(self):
        old = self.req_body.decode('utf8', 'ignore')
        gprint(old)
        options = re.findall(r'\{\{(.+?)\}\}', old)
        eval_res = []
        for op in options:
            pp =self._eval_option(op)
            eval_res.append(pp)
        if eval_res:
            for w in self._gen_map(eval_res):
                body_old = old
                for i in w:
                    body_old = self._replace_b(body_old, i)
                yield body_old,w


class BPServer(Daemon):

    def run(self):
        bp = Bp()
        main(bp)


def resender(req, data, args, proxy=None):
    s = requests.Session()
    if proxy:
        s.proxies['http'] = proxy
        s.proxies['https'] = proxy
    s.headers = dict(req.headers.items())
    method = getattr(s, req.command.lower())
    url = req.path
    if isinstance(data, str):
        data = data.encode()
    try:
        res = method(url, headers=s.headers, data=data)
        return res, args
    except Exception as e:
        return e, args

class HttpsPanel(Panel):

    def __init__(self):

        super().__init__()
        reqs = BPData.get_all_req()
        self.res = BPData.get_all_res()
        self.set_on_keyboard_listener('r', Panel.DIR_MODE, self.on_refresh)
        self.set_on_keyboard_listener('b', Panel.DIR_MODE, self.on_brute)
        # self.set_on_keyboard_listener('s', Panel.CMD_MODE, self.on_switch)
        self.mode = 'req' 

        self.all_reqs = [i.decode().split("\n")[0] for i in reqs]
        self.all_reqs_detail = [i.decode() for i in reqs]
        self.select_num = 0
        if len(reqs) > 0:
            self.select_one = self.all_reqs[0]
            self.select_num = 0
        else:
            self.select_one = "None"
            self.all_reqs = ['None']
            self.all_reqs_detail = ['None any reqeusts']

        self.show()

    def on_refresh(self, panel, ch):
        self.refresh()
        self.flush()
        self.show()

    def on_brute(self, panel, ch):
        bp = BPData.get_data(self.select_num)
        fname = os.path.join(BP_SESSION_DIR, str(time.time()))

        with open(fname, 'wb') as fp:
            fp.write(bp)
        os.system("%s %s" % (OPENER, fname))
        with open(fname, 'rb') as fp:
            content = fp.read()
            Bp._brute_req = content
        self.exit()


    def refresh(self):
        reqs_detail = [i.decode() for i in BPData.get_all_req()]
        self.res = BPData.get_all_res()
        reqs_head = [i.split("\n")[0] for i in reqs_detail]
        self.all_reqs_detail = reqs_detail
        self.all_reqs = reqs_head
        if self.select_one in reqs_head:
            self.select_num = reqs_head.index(self.select_one)
        
    def move(self, now):
        self.flush()
        if now == 'up':
            if self.select_num > 0:
                self.select_num -= 1
                self.select_one = self.all_reqs[self.select_num]
        elif now == 'down':
            if self.select_num < len(self.all_reqs) -1:
                self.select_num += 1
                self.select_one = self.all_reqs[self.select_num]
        elif now == 'right':
            self.mode = 'res'
        self.show()

    def show(self):
        if self.mode == 'req':
        # gprint(self.all_reqs_detail)
            al = len(self.all_reqs_detail)
            if al > self.SIZE[0] -3:
                if self.select_num > self.SIZE[0] -4:
                    st = self.select_num - self.SIZE[0] + 4
                    left_list = self.all_reqs[st:self.select_num+1]
                else:
                    left_list = self.all_reqs[:self.SIZE[0]-3]
            else:
                left_list = self.all_reqs

            # left_list.insert(0, str(len(self.all_reqs)))
            details = self.all_reqs_detail[self.select_num].split("\n")
            details[:self.SIZE[0]-4]
            # details.insert(0, "Requsts Detail")
        # print(details)
            TablePrint([ str(self.select_num)+"/"+ str(len(self.all_reqs)) + str(self.SIZE)] + left_list,['Request Detail']+ details, select_num=self.select_num)
        elif self.mode == 'res':
            res = self.res[self.select_num]
            fname = os.path.join(BP_SESSION_DIR, str(time.time())+".html")
            with open(fname, 'wb') as fp:
                fp.write(res)
            # self.stdin_normal()
            os.system("%s %s" %(OPENER, fname))
            # self.stdin_listenmode()
            self.mode = 'req'
            self.show()



class Bp(Cmd):

    _brute_req = None
    _targets = []
    _SERVER_PID = None

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.prompt = colored("(Bp)", 'red')
        self.thread = 10
        BPData.add_target("Unknow")
        self._exe = None
        self._res = []
        self._res_detail = []
        self.proxy = 'socks5://127.0.0.1:1080'
        self.futures = []
        self.finish_count = 0

    def summary(self, futu):
        res, args = futu.result()
        if isinstance(res, Exception):
            rprint(str(res))
            rprint(str(args))
        else:
            w = len(res.content)
            self._res.append(args + [w])
            self._res_detail.append(res.text)
        self.finish_count += 1
        if len(self.futures) == self.finish_count:
            # os.system("tput sc")
            # os.system("tput cup 0 0")
            print("\r%s" % colored(self.prompt, 'red') ,end='')
            # os.system("tput rc")
        else:
            # os.system("tput sc")
            # os.system("tput cup 0 0")
            if int(self.finish_count % 20) == 0: 
                print("\r%d/%d%s" %(self.finish_count, len(self.futures), colored(self.prompt, 'red')) ,end='')
            # os.system("tput rc")
    def do_stop(self, args):
        s = {'success': 0, 'fail': 0}
        for f in self.futures:
            w = f.cancel()
            if w:
                s['success'] +=1 
            else:
                s['fail'] += 1
        print(tabulate(s.items(), headers='firstrow'))

    def do_edit(self, args):
        fname = os.path.join(BP_SESSION_DIR, str(time.time()))
        with open(fname, 'wb') as fp:
            fp.write(Bp._brute_req)
        os.system("%s %s " %(OPENER, fname))
        with open(fname, 'rb') as fp:
            Bp._brute_req = fp.read()

    def do_clear(self ,args):
        self._res = []
        self._res_detail = []

    def do_brute(self, args):
        parse = ParseRequest(Bp._brute_req)
        self._exe = ThreadPoolExecutor(max_workers=self.thread)
        
        for data, args in parse.eval_and_replace():
            # gprint('use data: %s' % data)
            f = partial(resender, parse, data, args, proxy=self.proxy)
            futu = self._exe.submit(f)
            futu.add_done_callback(self.summary)
            self.futures.append(futu)

        gprint("run all")


    def do_load(self, path):
        if path == 'last':
            fs = sorted(os.listdir(BP_SESSION_DIR))
            if len(fs) > 0:
                path = os.path.join(BP_SESSION_DIR, fs[-1])            

        if os.path.exists(path):
            with open(path, 'rb') as fp:
                Bp._brute_req = fp.read()
            gprint("Load ok")
        else:
            rprint("Not found : %s" % path)

    def complete_load(self,text, line, begin, end):
        s = []
        # gprint(line)
        ds = line.split()
        if len(ds) > 1:
            d = os.path.dirname(ds[1])
            f = os.path.basename(ds[1])
            
            if os.path.exists(d):
                # gprint(d)
                for file in os.listdir(d):
                    if f in file:
                        s.append(file)
        if text in 'last':
            s.append('last')
        return s

    def do_preview(self, args):
        parse = ParseRequest(Bp._brute_req)
        for data, args in parse.eval_and_replace():
            gprint(data)

    def do_summary(self,args):
        if not args:
            t = [[i] + n for i,n in enumerate(self._res)]
            t.insert(0,['id']+ ['args' for i in range(len(t[0]) -2)]+['lens'])
            print(tabulate(t, headers='firstrow'))
            urgly = t[0]
            tc = Counter([i[-1] for i in t])
            v = min(tc, key=lambda x: tc[x])
            for i in t:
                if i[-1] == v:
                    if i != urgly:
                        gprint("---- focus on ---- ")
                        print(tabulate([urgly]))
                        break
        else:
            try:
                w = self._res_detail[int(args)]
                gprint(BS(w, 'lxml').text)
            except Exception as e:
                rprint(str(e))
                gprint("Must int ")
        # ===== 
        # parse options 
        # =====




    def do_set(self, args):
        k,v = args.split(" ", 1)
        if k == 'thread':
            v = int(v)


        setattr(self, k, v)

    # def _replace_b(self, )
    def complete_set(self, text, line, begin, end):
        s = []
        for op in ['thread', 'proxy']:
            if text in op:
                s.append(op)
        for i in ['socks5://' , 'http://', 'https://', '127.0.0.1']:
            if text in i:
                s.append(i)
        return s

    def eval_options(self):
        optins = re.findall(r'\{\{(.*)\}\}', self._brute_req)
        for nu,op in enumerate(optins):
            if os.path.exists(op):
                pass

    def do_show_options(self, args):
        optins = re.findall(r'\{\{(.*)\}\}', self._brute_req.decode())
        for nu,op in enumerate(optins):
            gprint(nu, op.strip())

    def do_show_brute_req(self, args):
        if self._brute_req:
            L(self._brute_req.decode())



    def do_list(self,args):
        h = HttpsPanel()
        h.run()


    def do_exit(self, args):
        return True

    def record(self, handler, res=False):
        req_id = int(time.time())
        if res:
            with use_mem_db() as db:
                saveResponse(req_id,handler.res, handler.res_body)
                r.save(db)
        else:
            with use_mem_db() as db:
                r = saveRequest(req_id, handler.req, handler.req_body)
                r.save(db)


    def do_stop_server(self, args):
        if Bp._SERVER_PID:
            os.kill(Bp._SERVER_PID, signal.SIGTERM)
            os.remove("/tmp/bpserver.pid")
        BPData.clear()

    def do_start_server(self, args):
        if os.path.exists("/tmp/bpserver.pid"):
            with open("/tmp/bpserver.pid") as fp:
                pid = int(fp.read().strip())
                os.kill(pid, signal.SIGTERM)
                os.remove("/tmp/bpserver.pid")
        os.popen("x-sehen --start-server bp").read()
        pid = int(open("/tmp/bpserver.pid").read().strip())
        Bp._SERVER_PID = pid
        gprint("bp server running")

    def __del__(self):
        self.do_stop_server(None)
