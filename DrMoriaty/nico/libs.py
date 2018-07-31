from io import StringIO
from io import BytesIO
from http.server import BaseHTTPRequestHandler

from DrMoriaty.datas.data import use_mem_db, saveRequest, saveResponse, Host, BPData
from DrMoriaty.utils.log import gprint, rprint, tprint, colored,TablePrint
from DrMoriaty.utils.daemon import Daemon
from DrMoriaty.dolch.lib import Panel
import os
import time
import signal
from multiprocessing import Process, Manager, Lock
from cmd import Cmd

from .proxy2 import main

lock = Lock()

class ParseRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


class BPServer(Daemon):

    def run(self):
        bp = Bp()
        main(bp)
        

class HttpsPanel(Panel):

    def __init__(self, req=True):

        super().__init__()
        if req:
            reqs = BPData.get_all_req()
        else:
            reqs = BPData.get_all_res()
        self.set_on_keyboard_listener('r', Panel.CMD_MODE, self.on_refresh)
        # self.set_on_keyboard_listener('b', Panel.CMD_MODE, self.on_brute)
        # self.set_on_keyboard_listener('s', Panel.CMD_MODE, self.on_switch)
                

        self.all_reqs = [i.decode().split("\n")[0] for i in reqs]
        self.all_reqs_detail = [i.decode() for i in reqs]
        self.select_num = -1
        if len(reqs) > 0:
            self.select_one = self.all_reqs[0]
            self.select_num = 0
        else:
            self.select_one = None

        self.show()

    def on_refresh(self, panel, ch):
        reqs_detail = [i.decode() for i in BPData.get_all_req()]
        reqs_head = [i.split("\n")[0] for i in reqs_detail]
        self.all_reqs_detail = reqs_detail
        if self.select_one in reqs_head:
            self.select_num = reqs_head.index(self.select_one)
        self.flush()
        self.show()

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
        self.show()

    def show(self):
        
        # gprint(self.all_reqs_detail)
        details = self.all_reqs_detail[self.select_num].split("\n")
        # print(details)
        TablePrint(self.all_reqs, details, select=self.select_one)





class Bp(Cmd):

    _targets = []
    _SERVER_PID = None

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.prompt = colored("(Bp)", 'red')

        BPData.add_target("Unknow")



    def do_add_target(self, host):
        BPData.add_target(host)
            

    def do_list_target(self, args):
        for h in BPData.get_hosts():
            gprint(h)

    def do_del_target(self, args):
        BPData.clear()        

    def do_list(self,args):
        if args == 'req':
            h = HttpsPanel()
        elif args == 'res':
            h = HttpsPanel(False)
        else:
            rprint("req/res")
            h = None
        if h:
            h.run()

    def complete_del_target(self,text,line,begidx,endid):
        res = []
        for i in Bp._targets:
            if text in i:
                res.append(i)
        return res



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
