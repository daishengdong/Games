""" monkey patched version of asynchat to allow map argument on all version of Python, and the best version of the poll function. """
from sys import version

import asynchat
import asyncore

if float(version[:3]) < 2.5:
	from asyncore import poll2 as poll
else:
	from asyncore import poll

# monkey patch older versions to support maps in asynchat. Yuck.
if float(version[:3]) < 2.6:
	def asynchat_monkey_init(self, conn=None, map=None):
		self.ac_in_buffer = ''
		self.ac_out_buffer = ''
		self.producer_fifo = asynchat.fifo()
		asyncore.dispatcher.__init__ (self, sock=conn, map=map)
	asynchat.async_chat.__init__ = asynchat_monkey_init

