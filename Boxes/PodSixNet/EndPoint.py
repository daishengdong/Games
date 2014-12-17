# coding=utf-8
import socket
import sys

from async import poll
from Channel import Channel

class EndPoint(Channel):
	"""
	The endpoint queues up all network events for other classes to read.
	"""
	def __init__(self, address=("127.0.0.1", 31425), map=None):
		self.address = address
		self.isConnected = False
		self.queue = []
		if map is None:
			self._map = {}
		else:
			self._map = map
	
	def DoConnect(self, address=None):
		if address:
			self.address = address
		try:
			Channel.__init__(self, map=self._map)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			self.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			self.connect(self.address)
		except socket.gaierror, e:
			self.queue.append({"action": "error", "error": e.args})
		except socket.error, e:
			self.queue.append({"action": "error", "error": e.args})
	
	def GetQueue(self):
		return self.queue
	
	def Pump(self):
		Channel.Pump(self)
		self.queue = []
		poll(map=self._map)
	
	# methods to add network data to the queue depending on network events
	
	def Close(self):
		self.isConnected = False
		self.close()
		self.queue.append({"action": "disconnected"})
	
	def Connected(self):
		self.queue.append({"action": "socketConnect"})
	
	def Network_connected(self, data):
		self.isConnected = True
	
	def Network(self, data):
		self.queue.append(data)
	
	def Error(self, error):
		self.queue.append({"action": "error", "error": error})
	
	def ConnectionError(self):
		self.isConnected = False
		self.queue.append({"action": "error", "error": (-1, "Connection error")})

if __name__ == "__main__":
	import unittest
	from time import sleep, time
	
	class FailEndPointTestCase(unittest.TestCase):
		def setUp(self):
			print
			print "Trying failed endpoint"
			print "----------------------"
			class FailEndPoint(EndPoint):
				def __init__(self):
					EndPoint.__init__(self, ("localhost", 31429))
					self.result = ""
				
				def Error(self, error):
					print "Received error message:", error
					self.result = error
				
				def Test(self):
					self.DoConnect()
					start = time()
					while not self.result and time() - start < 10:
						self.Pump()
						sleep(0.001)
			
			self.endpoint_bad = FailEndPoint()
		
		def runTest(self):
			self.endpoint_bad.Test()
			want = (61, 'Connection refused')
			self.assertEqual(list(self.endpoint_bad.result), list(want), "Socket got %s instead of %s" % (str(self.endpoint_bad.result), str(want)))
			print
		
		def tearDown(self):
			del self.endpoint_bad
			print "FailEndPointTestCase complete"
	
	from Server import Server
	class EndPointTestCase(unittest.TestCase):
		def setUp(self):
			self.outgoing = [
				{"action": "hello", "data": {"a": 321, "b": [2, 3, 4], "c": ["afw", "wafF", "aa", "weEEW", "w234r"], "d": ["x"] * 256}},
				{"action": "hello", "data": [454, 35, 43, 543, "aabv"]},
				{"action": "hello", "data": [10] * 512},
				{"action": "hello", "data": [10] * 512, "otherstuff": "hello\0---\0goodbye", "x": [0, "---", 0], "y": "zäö"},
			]
			self.count = len(self.outgoing)
			self.lengths = [len(data['data']) for data in self.outgoing]
			
			print
			print "Trying successful endpoint"
			print "--------------------------"
			class ServerChannel(Channel):
				def Network_hello(self, data):
					print "*Server* received:", data
					self._server.received.append(data)
					self._server.count += 1
					self.Send({"action": "gotit", "data": "Yeah, we got it: " + str(len(data['data'])) + " elements"})
			
			class TestEndPoint(EndPoint):
				received = []
				connected = False
				count = 0
				
				def Network_connected(self, data):
					self.connected = True
				
				def Network_gotit(self, data):
					self.received.append(data)
					self.count += 1
					print "gotit:", data
			
			class TestServer(Server):
				connected = False
				received = []
				count = 0
				
				def Connected(self, channel, addr):
					self.connected = True
			
			self.server = TestServer(channelClass=ServerChannel)
			self.endpoint = TestEndPoint(("localhost", 31425))
		
		def runTest(self):
			self.endpoint.DoConnect()
			for o in self.outgoing:
				self.endpoint.Send(o)
			
			print "polling for half a second"
			for x in range(50):
				self.server.Pump()
				self.endpoint.Pump()
				
				# see if what we receive from the server is what we expect
				for r in self.server.received:
					self.failUnless(r == self.outgoing.pop(0))
				self.server.received = []
				
				# see if what we receive from the client is what we expect
				for r in self.endpoint.received:
					self.failUnless(r['data'] == "Yeah, we got it: %d elements" % self.lengths.pop(0))
				self.endpoint.received = []
				
				sleep(0.001)
			
			self.assertTrue(self.server.connected, "Server is not connected")
			self.assertTrue(self.endpoint.connected, "Endpoint is not connected")
			
			self.failUnless(self.server.count == self.count, "Didn't receive the right number of messages")
			self.failUnless(self.endpoint.count == self.count, "Didn't receive the right number of messages")
			
			self.endpoint.Close()
			print self.endpoint.GetQueue()
			print
		
		def tearDown(self):
			del self.server
			del self.endpoint
			print "EndPointTestCase complete"
	
	unittest.main()
	
