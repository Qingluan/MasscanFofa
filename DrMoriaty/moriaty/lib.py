import sys
import termios
import contextlib
import os


@contextlib.contextmanager
def on_keyboard_ready():
    file = sys.stdin
    old_attrs = termios.tcgetattr(file.fileno())
    new_attrs = old_attrs[:]
    new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
    try:
        termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
        yield
    finally:
        termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)



class Panel:
    DIR_MODE = 1
    CMD_MODE = 2
    SEARCH_MODE = 4

    def __init__(self):
        self.key_map = {}
        self.key_map_move = {}
        self.key_map_after = {}
        self.key_map_before = {}

        self.now = [0,0]
        [self.set_on_keyboard_listener(i, Panel.DIR_MODE, self.on_move) for i in 'hjkl' ]


    
    def to_left(self):
        if self.now[1] > 0:
            self.now[1] -= 1
        return self.now

    def init(self):
        return

    
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


        

    def move_call(self, k):   
        """
        special happend to 'hjkl' to handle move cursor.
        """
        events = self.key_map_move.get(k)
        return self._call(events, k)

    def run(self):
        os.system('tput cl  ')
        self.init()
        with on_keyboard_ready():

            try:
                cc = 1
                while 1:
                    os.system("tput cup 0 0  ")
                    ch = sys.stdin.read(1)
                    os.system("tput cl")
                    # self.clear()
                    if not ch or ch == chr(4):
                        break
                    # if self.mode & Pane.DIR_MODE:
                    
                    # if self.mode & Pane.DIR_MODE:
                    self.move_call(ch)
                    
                    
                    # show main content. 
                    # then to display other info.

                    # L(ord(ch), r=self.h+1, c=self.w-3,color='blue',end='')

            except (KeyboardInterrupt, EOFError):
                pass