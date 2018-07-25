from DrMoriaty.utils.log import lprint, gprint, rprint, colored, cprint
from DrMoriaty.datas.data import Cache, Info
from DrMoriaty.utils.setting import DB_FOFA

from .test import load,ls_mod


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
    ins = []
    def __init__(self, target):
        self.target = target
        self.__class__.ins.append(self)

    def __del__(self):
        if self in self.__class__.ins:
            self.__class__.ins.remove(self)


    @classmethod
    def run(cls, Obj):

        hs = [i.target for i in cls.ins]
        if hasattr(Obj, '__name__'):
            cls.log("use :" , Obj.__name__)
        res = Obj.test(hs)
        if res:
            cls.log(res)

    @classmethod
    def log(cls,*args, label='green', **kwargs):
        """
        l,g,bg
        """
        head = colored("[+]", 'red', attrs=['bold'])
        print(head, *args, **kwargs)


def load_and_run_test(prepare_test_info, *module_names):
    if not len(prepare_test_info) > 0:
        rprint("No targets")
        return

    for name in module_names:
        Obj = load(name)
        if not Obj:continue
        for info in prepare_test_info:
            t = TestBase(info)
        TestBase.run(Obj)
