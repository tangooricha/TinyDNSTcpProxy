import dnslib
import threading
import socket

dnsServers = ["8.8.8.8"]

class ServerThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.workerThreads = []
	def run(self):
		global sockLock
		self.bindSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.bindSock.bind(("localhost", 53))
		while(True):
			self.recvData, self.clientAddr = self.bindSock.recvfrom(65536)
			sockLock.acquire()
			curThread = WorkerThread(self.bindSock, self.clientAddr, self.recvData)
			self.workerThreads.append(curThread)
			curThread.start()
			sockLock.release()

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
			except:
				pass
		sockLock.acquire()
		self.bindSock.sendto(self.dnsResponse, self.clientAddr)
		sockLock.release()

if __name__ == '__main__':
	global sockLock
	sockLock = threading.Lock()
	serverThread = ServerThread()
	serverThread.start()
	serverThread.join()

