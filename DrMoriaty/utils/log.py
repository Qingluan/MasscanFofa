from termcolor import cprint, colored

def gprint(args, **kargs):
    cprint(colored("[+] ",'green') + args, **kargs)

def rprint(args, **kargs):
    cprint(colored("[!] ",'red') + args, **kargs)


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