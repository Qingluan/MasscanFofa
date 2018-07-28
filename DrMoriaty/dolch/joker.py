from requestium import Session
from cmd import Cmd
from DrMoriaty.utils.log import Tprint, gprint,rprint, colored

class base(Cmd):

	def __init__(self, target):

		self.prompt = colored(">")
		