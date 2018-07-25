from qlib.data import dbobj, Cache
from DrMoriaty.utils.setting import DB_FOFA

def get_db():
	return Cache(DB_FOFA)

class Info(dbobj):pass

# Info(title=ti,ip=ip,ports=ports,os=os,ctime=time,geo=geo,body=body)