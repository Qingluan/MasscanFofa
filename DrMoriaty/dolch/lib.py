
import sys
import termios
import contextlib
import os
from cmd import Cmd
import types

from DrMoriaty.utils.log import rprint, gprint

NEW_ATTRS = None
OLD_ATTRS = None
STDIN_FILE = None

@contextlib.contextmanager
def on_keyboard_ready():
    global NEW_ATTRS
    global OLD_ATTRS
    global STDIN_FILE

    file = sys.stdin
    old_attrs = termios.tcgetattr(file.fileno())
    new_attrs = old_attrs[:]
    new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
    NEW_ATTRS = new_attrs
    OLD_ATTRS = old_attrs
    STDIN_FILE = file
    try:
        termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
        yield
    finally:
        termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)


class Panel:
    DIR_MODE = 1
    CMD_MODE = 2
    FILE_MODE = 3
    SEARCH_MODE = 4
    SIZE = tuple([ int(i) for i in os.popen("tput lines && tput cols ").read().split()])

    def __init__(self):
        self.key_map = {}
        self.key_map_move = {}
        self.key_map_after = {}
        self.key_map_before = {}
        self.prompt = ">"
        self._if_exist = False
        self.DIS_MODE = self.DIR_MODE
        self.now = [0,0]
        [self.set_on_keyboard_listener(i, Panel.DIR_MODE, self.on_move) for i in 'hjkl' ]
        # self.set_on_keyboard_listener('q', Panel.FILE_MODE, self.exit_preview)


    
    def to_left(self):
        if self.now[1] > 0:
            self.now[1] -= 1
        return self.now

    def init(self):
        return
    
    def flush(self):
        s = " " * (self.SIZE[1])
        q = '\n'.join([s for i in range(self.SIZE[0])])
        os.system("tput cup 0 0")
        print(q)
        os.system("tput cup 0 0")


    def to_right(self):
        self.now[1] += 1
        return self.now

    
    def to_down(self):
        self.now[0] += 1
        return self.now

    
    def to_up(self):
        if self.now[0] > 0:
            self.now[0] -= 1
        return self.now
       
    def stdin_normal(self):
        termios.tcsetattr(STDIN_FILE.fileno(), termios.TCSADRAIN, OLD_ATTRS)

    def stdin_listenmode(self):
        termios.tcsetattr(STDIN_FILE.fileno(), termios.TCSADRAIN, NEW_ATTRS)        
 
    def on_move(self, pane, ch):
        if ch == "j":
            di = 'down'
            no = self.to_down()
        elif ch == 'k':
            di = 'up'
            no = self.to_up()
        elif ch == 'h':
            di = 'left'
            no = self.to_left()
        elif ch == 'l':
            di = 'right'
            no =  self.to_left()
        self.move(di)

    def on_cmd(self, pane, ch):
        self.flush()
        self.stdin_normal()
        self.do_cmd()
        self.show()
        self.stdin_listenmode()

    def on_preview(self, panel, ch):
        self.flush()
        self.stdin_normal()
        self.preview()
        self.show()
        self.stdin_listenmode()

    def exit_preview(self, panel, ch):
        self.flush()
        self.show()
        self.DIS_MODE = self.DIR_MODE

    def move(self, di):
        raise NotImplementedError

    def set_on_keyboard_listener(self, k, m, f):
        """
            set k ,f 
                f(self)
        """
        fun_map = self.key_map_move.get(k, set())
        fun_map.add((m,f))
        self.key_map_move[k] = fun_map

    def _call(self, events, k):
        """
         to call function which  map to key.
        """

        if events:
            for mode, func in events:
                # if func and mode & self.mode:
                if func:
                    return func(self, k)

    def on_call(self, k):
        """
        happend after pressdown but before change anything.
        """
        events =  self.key_map.get(k)
        return self._call(events, k)
        # return self._call(mode, f, k)

    def after_call(self,k):
        """
        happend after change something.
        """
        events = self.key_map_after.get(k)
        return self._call(events, k)

    def before_call(self, k):
        """
        happend before on_call
        """
        
        events = self.key_map_before.get(k)
        return self._call(events, k)

    def do_exit(self, q):
        return True
        

    def move_call(self, k):   
        """
        special happend to 'hjkl' to handle move cursor.
        """
        if self.DIS_MODE == self.DIR_MODE:
            events = self.key_map_move.get(k)
            return self._call(events, k)

    def exit(self):
        self._if_exist = True

    def run(self):
        
        self.init()
        os.system("tput sc")
        with on_keyboard_ready():

            try:
                cc = 1
                while 1:
                    if self._if_exist:
                        break
                    ch = sys.stdin.read(1)
                    self.flush()
                    # self.clear()
                    if not ch or ch == chr(4):
                        break

                    if ch == 'q':
                        self.exit()
                        continue
                    # if self.mode & Pane.DIR_MODE:
                    
                    # if self.mode & Pane.DIR_MODE:
                    self.move_call(ch)
                    
                    
                    # show main content. 
                    # then to display other info.

                    # L(ord(ch), r=self.h+1, c=self.w-3,color='blue',end='')

            except (KeyboardInterrupt, EOFError):
                pass
        os.system("tput rc")