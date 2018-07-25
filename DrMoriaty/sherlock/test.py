import sys,os,importlib
from DrMoriaty.utils.log import rprint

TEST_MODULES_PATH = os.path.expanduser("~/.config/TestsModules")
sys.path.append(TEST_MODULES_PATH)


def load(name):
    if os.path.exists(os.path.join(TEST_MODULES_PATH ,"test_modules")):
        try:
            return importlib.import_module("test_modules." + name)
        except ModuleNotFoundError:
            rprint("not found module: %s" % name )
def ls_mod():
    for name in os.listdir(os.path.join(TEST_MODULES_PATH, 'test_modules')):
        if name.startswith('_'): continue
        if not name.endswith(".py"):continue
        name = name.replace('.py','')
        m = load(name)
        if hasattr(m, 'usage'):
            print(name , "  ------->")
            m.usage()


