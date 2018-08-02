import os
import random
import time

from DrMoriaty.datas.data import Info
from DrMoriaty.setting import ReportPATH, DB_FOFA, TmpReportPATH
from DrMoriaty.utils.daemon import Daemon
from DrMoriaty.datas.data import Cache
from DrMoriaty.utils.log import gprint
from bs4 import BeautifulSoup as BS 

if not os.path.exists(ReportPATH):
    os.mkdir(ReportPATH)

if not os.path.exists(TmpReportPATH):
    os.mkdir(TmpReportPATH)

class MasscanDaemon(Daemon):
    
    @staticmethod
    def scan():
        if not os.path.exists("/tmp/MasscanReports"):
            os.mkdir("/tmp/MasscanReports")
        
        ca = Cache(DB_FOFA)
        infos = []
        for i in os.listdir("/tmp/MasscanReports"):
            if not i.endswith(".mas"):continue
            s = os.path.join("/tmp/MasscanReports", i)
            downloaded = False
            gprint("Found file: %s" % i)
            with open(s, 'rb') as fp:
                res = fp.read().decode('utf-8', 'ignore')
                if '</nmaprun>' in res:
                    
                    info = Masscan.reportload(res)
                    for info_i in info:
                        infos.append(info_i)
                    downloaded = True
            if downloaded:
                os.rename(s, os.path.join(ReportPATH, i))
        ca.save_all(*infos)
        gprint("save : %d" % len(infos))
        return infos

    def run(self):
        while 1:
            MasscanDaemon.scan()
            time.sleep(10)

class Masscan:
    """
    target = xxx.x.x.x[/24/16/8]
    options = {
        "banners":true,

    }
    """

    def __init__(self, target, *ports, **options):
        self.target = target
        self.report_file = os.path.join(TmpReportPATH, self.target.replace("/","_") + ".mas")
        self.options = ""
        if options.get("banners", True):
            self.options += "  --banners"
        self.options += " -oX %s" % self.report_file
        self.ports = list(ports)
        self.ports_opt = "-p80,443,8080"+ ",".join(self.ports)
        self.cmd = self.ports_opt + " " + self.target + " " + self.options

    @staticmethod
    def reportload(res):
        if os.path.exists(res):
            res = open(res).read()
        Report = {}
        for host in BS(res, 'lxml').select("host"):
            addr = host.select("address")[0]
            for port in host.select("port"):

                for service in port.select("service"):
                    banner = service.attrs.get("banner")
                    title = service.attrs.get("name")
                    ip = addr.attrs.get("addr")
                    ports = port.attrs.get("portid")
                    yield Info(title=title, ip=ip, ports=ports, os='', ctime='', body=banner, geo='')

    def run(self):
        gprint("Run Masscan: "+ self.cmd)
        os.popen("masscan " + self.cmd).read()

        return MasscanDaemon.scan()
