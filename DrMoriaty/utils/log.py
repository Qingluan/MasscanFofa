from termcolor import cprint, colored
from tabulate import tabulate
import re


def gprint(args, *others, **kargs):
    if not others:
        cprint(colored("[+] ",'green') + args, **kargs)
    else:
        print(colored('[+] ', 'green'), args, *others)

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