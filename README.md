# MasscanFofa
a little tools for report masscan and fofa , easy to extend plugin , use same data struct to save and use.



### Usage

```bash
$ x-sehen -h 
usage: x-sehen [-h] [-s [SEARCH [SEARCH ...]]] [--use USE] [-l] [-p PAGE] [-P]
               [-t [TEST [TEST ...]]] [--login] [--ls-mod] [--masServer]

optional arguments:
  -h, --help            show this help message and exit
  -s [SEARCH [SEARCH ...]], --search [SEARCH [SEARCH ...]]
                        search key : -s
  --use USE             can use fofa | masscan | db
  -l, --list            list local db.
  -p PAGE, --page PAGE  set page to search in web
  -P, --proxy           set proxy
  -t [TEST [TEST ...]], --test [TEST [TEST ...]]
                        use test module to test result
  --login               login in fofa
  --ls-mod              list module to use:
  --masServer           list module to use:

```

![](./use.png)



#### fofa

```bash
$ x-sehen -s title apach --use fofa  [--login]
```

#### masscan

```bash
$ x-sehen -s 8.8.8.8/24 --use masscan 
```

#### search in db

```bash
# Info is data struct in this tools
## has var :  Info.ip , Info.host, Info.title , Info.os , Info.ctime, Info.body
$ x-sehen -s apach [ip host title body .... var in Info ]
```



### use plugins

- alive [ default given]

  ```bash
  $ x-sehen -s apache -t alive 
  ```

  > alive plugin :

  ```python
  ### ~/.config/TestsModules/test_modules/alive.py
  from asynctools.servers import TcpTests
  from termcolor import colored
  
  
  def usage():
      print(colored("[+]", "blue"), " test if target 's ports all alive")
  
  
  def test(targets):
      hosts = []
      for i in targets:
          for ii in i.ports.split("/"):
              hosts.append(i.ip + ":" + ii)
      hosts = list(set(hosts))
      res = TcpTests(hosts)
      unalive = set(hosts) - set(res) 
      for i in res:
          if "443" in i[0]:
              print(colored("[+]", "green"), "https://" + i[0], " alive")
          else:
              print(colored("[+]", "green"), "http://" + i[0], " alive")
  
      for i in unalive:
          print(colored("[-]", "red"), i, " dead")
  
  ```

  

### Plugins extend



```bash
$ touch ~/.config/TestsModules/test_modules/xxxx.py

```

```python
## in ~/.config/TestsModules/test_modules/xxxx.py 
def usage():
    print(" some description ")

def test(targets):
    """
    targets has some attrs:
    	targets.ip
    	targets.host
    	targets.geo
    	targets.title
    	targets.os
    	targets.ports
    	targets.body
    this data is load from fofa or masscan.
    """
    pass
```

