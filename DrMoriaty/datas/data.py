from qlib.data import dbobj, Cache
from DrMoriaty.utils.setting import DB_FOFA
import contextlib

@contextlib.contextmanager
def use_db():
    try:
        ca = Cache(DB_FOFA)
        yield ca

    finally:
        del ca

def get_db():
    return Cache(DB_FOFA)

class Info(dbobj):pass

class Checken(dbobj):pass
# Info(title=ti,ip=ip,ports=ports,os=os,ctime=time,geo=geo,body=body)