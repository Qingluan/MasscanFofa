from setuptools import setup, find_packages
from setuptools.command.install import install
import os, sys
import time
class MyInstall(install):
    def run(self):
        install.run(self)
        name = os.path.join(os.path.dirname(__file__), "res/phantomjs") 
        if sys.platform.startswith('darw'):
            name = os.path.join(os.path.dirname(__file__), "res/mac/phantomjs")
        
        if os.path.exists(name):
            print("\n\n\n--- < install phantomjs > -------\n")
            time.sleep(1)
        os.popen("cp -v {} /usr/local/bin/ ".format(name)).read()
        # os.rename(os.path.join(os.path.dirname(__file__), "res/phantomjs"), "/usr/local/bin/phantomjs")
        
        TEST_MODULES_PATH = os.path.expanduser("~/.config/TestsModules")
        TEST_MODULES_ROOT = os.path.join(TEST_MODULES_PATH, 'test_modules')
        if not os.path.exists(TEST_MODULES_PATH):
            os.mkdir(TEST_MODULES_PATH)

        if not os.path.exists(TEST_MODULES_ROOT):
            
            os.mkdir(TEST_MODULES_ROOT)
            os.popen("touch %s" % os.path.join(TEST_MODULES_ROOT, "__init__.py"))
        
        for file in os.listdir("plugins"):
            if not file.endswith(".raw"): continue
            src = os.path.join("plugins", file)
            des = os.path.join(TEST_MODULES_ROOT, file.rsplit("raw", 1)[0] + "py")
            os.popen("cp -v {} {} ".format(src, des)).read()            
        


setup(name='x-mroy-1051',
    version='0.2.2',
    description='search in web',
    url='https://github.com//.git',
    author='mroy_qing',
    license='MIT',
    cmdclass={"install": MyInstall},
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=['mroylib-min','brotli','pandas','tabulate','FLowWork','requestium','termcolor'],
    entry_points={
        'console_scripts': ['x-sehen=DrMoriaty.cmd.main:main',]
    },

)
