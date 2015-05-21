import dnslib
import threading
import socket
import sys

dnsServers = ["8.8.8.8"]

class ServerThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global sockLock
		try:
			self.bindSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			self.bindSock.bind(("", 53))
		except:
			sys.exit()
		while(True):
			try:
				self.recvData, self.clientAddr = self.bindSock.recvfrom(65536)
				sockLock.acquire()
				curThread = WorkerThread(self.bindSock, self.clientAddr, self.recvData)
				curThread.start()
				sockLock.release()
			except:
				pass

class WorkerThread(threading.Thread):
	def __init__(self, bindSock, clientAddr, recvData):
		threading.Thread.__init__(self)
		self.bindSock = bindSock
		self.clientAddr = clientAddr
		self.recvData = recvData
	def run(self):
		global sockLock
		self.clientQuestionRecord = dnslib.DNSRecord.parse(self.recvData)
		for dnsSvr in dnsServers:
			try:
				self.dnsResponse = self.clientQuestionRecord.send(dnsSvr,tcp = True)
				sockLock.acquire()
				self.bindSock.sendto(self.dnsResponse, self.clientAddr)
				sockLock.release()
			except:
				pass

if __name__ == '__main__':
	global sockLock
	sockLock = threading.Lock()
	serverThread = ServerThread()
	serverThread.start()
	serverThread.join()

