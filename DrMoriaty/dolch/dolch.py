from cmd import Cmd
from DrMoriaty.utils.log import colored, gprint, rprint
from DrMoriaty.datas.data import Checken, get_db, use_db
from .php import Php
from .jsp import Jsp

class Dolch(Cmd):

    def __init__(self):
        super().__init__()
        self.prompt = colored('(Dolch)', 'red')

    def do_entry(self, args):
        che = None
        with use_db() as db:
            che = db.query_one(Checken, id=int(args))
        if che:
            if che.type == 'jsp':
                p = Jsp(che.target, che.passwd)
            else: 
                p = Php(che.target, che.passwd)
            p.run()

    def do_add(self, args):
        target = None
        passwd = 'chopper'
        encoding = 'UTF-8'
        type = None
        All = args.split()
        if len(All) < 3:
            rprint("at least [target] [passwd] | like  http://localhost/1.php chopper ")
            return
        for w in All:
            if w.startswith("http"):
                target = w
                if target.endswith(".php"):
                    type = 'php'
                elif target.endswith(".jsp"):
                    type = 'jsp'
                elif target.endswith(".asp"):
                    type = 'asp'
            elif w.lower() in ['utf-8', 'gbk']:
                encoding = w
            elif w in ['php', 'jsp', 'asp','aspx']:
                type = w
            else:
                passwd = w
        checken = Checken(target=target, passwd=passwd, encoding=encoding, type=type)
        with use_db() as db:
            checken.save(db)
        gprint(type, target, passwd, encoding)

    def do_delete(self, args):
        with use_db() as db:
            che = db.query_one(Checken, id=int(args))
            db.delete(che)


    def do_list(self, args):
        with use_db() as db:
            for che in db.query(Checken):
                gprint(che.type, che.id, che.target, che.passwd, che.encoding)


    def do_exit(self, args):
        return True