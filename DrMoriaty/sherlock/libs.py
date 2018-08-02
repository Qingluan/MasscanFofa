from DrMoriaty.utils.log import lprint, gprint, rprint, colored, cprint, Tprint
from DrMoriaty.datas.data import Cache, Info
from DrMoriaty.setting import DB_FOFA

from functools import partial
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from .test import load,ls_mod
from traceback import print_exception

C = lambda x,y : colored(' ' + x+ ' ', on_color='on_'+ y) if x.strip() else ''



def search_in_db(key=None, *show_options):
    prepare_test_info = []
    DB_Handle = Cache(DB_FOFA)
    if not key:
        for i in DB_Handle.query(Info):
            lprint(title=i.title, os=i.os, ip=i.ip, ports=i.ports, time=i.ctime, geo=i.geo, body=i.body)
    else:
        
        if not show_options:
            def printer(i):
                
                lprint(title=i.title, os=i.os, ip=i.ip, ports=i.ports, time=i.ctime, geo=i.geo, body=i.body)
                prepare_test_info.append(i)
        else:
            def printer(i):
                
                prepare_test_info.append(i)
                f = {}
                for show in show_options:
                    if hasattr(i,show):
                        f[show] = getattr(i, show)
                    elif show == 'time':
                        f[show] = getattr(i, 'c' + show)
                lprint(**f)
            
        for i in DB_Handle.fuzzy_search(Info, key, printer=printer):
            pass
        
    gprint("set target: %d" % len(prepare_test_info))
    return prepare_test_info




class TestBase:
    process_now = 0
    ins = []
    def __init__(self, target):
        self.target = target
        self.__class__.ins.append(self)

    def __del__(self):
        if self in self.__class__.ins:
            self.__class__.ins.remove(self)

    @staticmethod
    def process_add(all):
        TestBase.process_now += 1
        cprint("     %d / %d "% (TestBase.process_now, all),color="blue", on_color="on_white",end='\r')

    @classmethod
    def run(cls, Obj):
        TestBase.process_now = 0

        def try_run(*args, **kargs):
            try:
                return Obj.test(*args, **kargs)
            except Exception as e:
                rprint(e)
                print_exception(e)

        test_if_same = set()
        result_zusammen = dict()
        hs = []
        for i in cls.ins:
            if (i.target.ip + i.target.ports) in test_if_same: continue
            if '/' in i.target.ports:
                i.target.port = i.target.ports.split("/")[0].strip()
            else:
                i.target.port = i.target.ports.strip()
            test_if_same.add(i.target.ip + i.target.ports)
            hs.append(i.target)
        #hs = [i.target for i in cls.ins]
        process_len = len(hs)
        if hasattr(Obj, '__name__'):
            cls.log("use :" , Obj.__name__)
        if hasattr(Obj, "mode"):
            if Obj.mode == "thread":
                thread = 7
                if hasattr(Obj, 'thread'):
                    thread = int(Obj.thread)
                if hasattr(Obj, 'timeout'):
                    timeout = Obj.timeout
                else:
                    timeout = 12
                gprint("set mode : %s" % Obj.mode)
                gprint("set thread : %d" % thread)
                gprint("set timeout : %d" % timeout)
                with ThreadPoolExecutor(max_workers=thread) as exe:
                    if not hasattr(Obj, 'callback'):
                        if hasattr(Obj, 'log') and Obj.log == 'simple':

                            callback = lambda x: gprint(x, "\nfinish done | %s" % colored("-" * 5 + '\n',
                            'blue'))
                        else:
                            callback = lambda x: TestBase.process_add(process_len)
                    else:
                        callback = Obj.callback

                    def callback_out(future, url=''):
                        try:
                            r = future.result(timeout=timeout)
                            result_zusammen[url] = r
                            callback(r)
                        except futures.TimeoutError:
                            rprint('timeout:', url)

                    for h in hs:
                        future = exe.submit(try_run, h)
                        future.add_done_callback(partial(callback_out, url=h.ip))

                if 'has' in Obj.__name__ or 'if' in Obj.__name__:
                    Tprint(result_zusammen,color='green',attrs=['bold'])
        else:
            res = try_run(hs)
            if res:
                cls.log(res)

    @classmethod
    def log(cls,*args, label='green', **kwargs):
        """
        l,g,bg
        """
        head = colored("[+]", 'red', attrs=['bold'])
        print(head, *args, **kwargs)


def load_and_run_test(prepare_test_info, *module_names, **test_options):
    """
        thread: int (only use for plugin set)
    """
    if not len(prepare_test_info) > 0:
        rprint("No targets")
        return

    for name in module_names:
        Obj = load(name)
        if not Obj:continue
        for info in prepare_test_info:
            t = TestBase(info)
        TestBase.run(Obj)
