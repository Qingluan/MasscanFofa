from termcolor import cprint, colored
from tabulate import tabulate
from pandas import DataFrame
import re


def gprint(args, *others, **kargs):
    if not others:
        cprint(colored("[+] ",'green') + args, **kargs)
    else:
        print(colored('[+] ', 'green'), args, *others)

def L(*args, **kargs):
    print(colored("[+]", 'green'), *args, **kargs)

def rprint(args, *others, **kargs):
    
    if isinstance(args, Exception):
        args = str(args)
    if not others:
        cprint(colored("[!] ",'red') + args, **kargs)
    else:
        print(colored('[!] ', 'red'), args, *others)


def tprint(*args, **kargs):
    f = args[0]
    l = args[1:]
    C = lambda x,y : colored(' ' + x+ ' ', on_color='on_'+ y) if x.strip() else ''
    print(C(f, 'blue'), *l)


def SwordPrint(res, err=None, pwd='', dir=[], sub_dir=[], op="",select=None, if_dir=None):
    pwd = colored(pwd, 'blue', attrs=['bold', 'underline'])
    if select and select in dir:
        dir[dir.index(select)] = colored(select, "green", attrs=['underline'])
    if if_dir:
        for i in range(len(dir)):
            if if_dir(dir[i]):
                dir[i] = colored(dir[i], attrs=['bold'])

    dir = [select] + dir
    sub_dir = [err] + sub_dir 
    if err:
        res = colored(str(err), 'red')

    cmd_reslines = []
    if  res and isinstance(res, str):
        cmd_reslines = res.split("\n")
    t = DataFrame([[pwd] + cmd_reslines, dir, sub_dir, [op]]).T.values
    print(tabulate(t, headers='firstrow'))

def TablePrint(*lists, select_num=0):
    first = [i for i in lists[0]]

    if select_num < len(first) -1:
        # if len(first[0]) < 10:
        select_num += 1
    else:
        select_num = len(first) -1
    first[select_num] = colored(first[select_num], 'green', attrs=['underline'])

    t = DataFrame([first, *lists[1:]]).T.values
    print(tabulate(t, headers='firstrow'))

def tableprint(data, color=None,**kargs):
    res = data.items()


def lprint(title='', host="" ,ports='', ip='', time='', geo='', os='', body=''):
    C = lambda x,y : colored(' ' + x+ ' ', on_color='on_'+ y) if x.strip() else ''
    labels = [C(i, 'red') for i in title.split("|")]
    print(C(host, 'magenta'),
        C(ip, 'blue'),
        C(ports, 'cyan'),
        C(time, 'blue'),
        C(os, 'green'),
        C(geo, 'yellow'),
        *labels)
        # sep=colored("|",attrs=['blink','bold']))
    if body:
        if '<hr/>' in body:
            for i,b in enumerate(body.split("<hr/>")):
                if i % 2== 0:
                    cprint(b, 'green', attrs=['bold'])
                else:
                    cprint(b, 'blue', attrs=['bold'])
        else:
            cprint(body, 'green')

def print_info(i):
    lprint(title=i.title, os=i.os, ip=i.ip, ports=i.ports, time=i.ctime, geo=i.geo, body=i.body)
                
# def tablize(d, fmt=""):
#     items = d.items()
#     can_table = True
#     ss = []
#     for i in items:
#         if isinstance(i[1], dict):
#             can_tale = False        
#             now = tablize(i[1], fmt=fmt)
#             ss.append([i[0],now])
#         elif isinstance(i[1], list):
#             can_table = False
#             e = {str(i):i[1][i] for i in range(len(i[1]))}
#             now = tablize(e, fmt=fmt)
#             ss.append([i[0], now])
#         elif isinstance(i[1], str):
#             ss.append(i)
#         else:
#             ss.append([i[0], str(i[1])])
#     return tabulate(ss, fmt=fmt)


def tag2dict(res):
    ss = {}
    for i in re.findall(r'(\w+=\".+?\")', res):
        key ,v = i.split("=", 1)
        ss[key] = v[1:-1]
    return ss
    
def Tprint(d, fmt="", **kargs):
    s = [[i[0], tabulate(i[1].items(), tablefmt=fmt)] if isinstance(i[1], dict) else i for i in d.items()]
    r = tabulate(s, tablefmt=fmt)
    cprint(r, **kargs)