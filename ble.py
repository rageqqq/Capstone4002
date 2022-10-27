
import time
import queue
import struct

from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from threading import Thread
from multiprocessing import Queue
import csv


HELLO = 'H'
ACK = 'A'
NAK = 'N'

start_time = time.time()


packet_size = 20
packet_size2 = 20
packet_size3 = 20


q = Queue()

class SensorDelegate(DefaultDelegate):

	def __init__(self, char):
		DefaultDelegate.__init__(self)
		self.char = char
		self.has_handshake = False
		self.seq_num = 0
		self.fail_counter = 0
		self.good_counter = 0

	def handleNotification(self, cHandle, data):

		# able to read 20 bytes maximum each time

		global is_reload

		if self.has_handshake:

			data_status = False
			is_good_msg = False
			msg = bytearray(data) # convert to byte array

			if len(msg) == packet_size:

				is_good_msg = calculate_checksum(msg)
						
				self.seq_num = (self.seq_num + 1) & 0xFF

				if is_good_msg:
					#self.good_counter += 1
					self.packetOne = bytearray(msg)
					data_status = True
				elif self.seq_num != msg[0]:
					#self.fail_counter += 1
					self.seq_num = msg[0]
					print('wrong seqno')
				else:
					print("Failed checksum")

			if data_status and is_good_msg:
				q.put(self.packetOne)


		elif len(data) == 1 and data == str.encode(ACK):
			self.has_handshake = True
			self.char.write(str.encode(ACK))

		else:
			self.char.write(str.encode(HELLO))

def bluno_connection(mac):

	service_uuid = 'dfb0' #0000dfb0-0000-1000-8000-00805f9b34fb
	characteristic_id = 'dfb1' #0000dfb1-0000-1000-8000-00805f9b34fb

	has_connected = False

	while has_connected == False:
		try:

			print('connecting...')

			bluno = Peripheral(mac)
			service = bluno.getServiceByUUID(service_uuid)
			char = service.getCharacteristics(characteristic_id)[0]
			aaa = SensorDelegate(char)
			bluno.setDelegate(aaa)

			print('bluno ' + mac + ' is connected')
			char.write(str.encode(HELLO))

			return bluno, char, aaa

		except Exception:
			print('error')
			pass


def handshake(bluno, char, mac):

	is_handshake_done = False
	print('doing handshake')
	while is_handshake_done == False:

		if bluno.waitForNotifications(1): # handleNotification
			is_handshake_done = True
		else:
			char.write(str.encode(HELLO))
			print('sent handshake')

	print('handshake done: ' + mac)
	return is_handshake_done


def bluno_thread(bluno, char, mac, aaa, t_count):

	has_handshake = False
	#running_time = time.time()
	#current_time = time.time()

	while True:
		current_time = time.time()
		try:
			#if current_time - running_time > 10:
						#print(str(t_count) + ' fail count is ' + str(aaa.fail_counter))
						#print(str(t_count) + ' good count is ' + str(aaa.good_counter))
						#running_time = current_time
			if has_handshake:
				if bluno.waitForNotifications(1): # handleNotification			
					pass
				else:
					# when reset is pressed or inactivity
					bluno.disconnect()
					print('disconnect due to inactivity')
					has_handshake = False
					bluno, char, aaa = bluno_connection(mac)
					pass
			else:
				has_handshake = handshake(bluno, char, mac)

		except KeyboardInterrupt:
			bluno.disconnect()
			break

		except BTLEDisconnectError:
			print('bluno: ' + mac + ' disconnected')
			has_handshake = False
			bluno, char, aaa = bluno_connection(mac)



def print_data(queue):
	global is_reload
	start_time = time.time()
	current_time = time.time()
	success_counter = 0
	count = 0
	write_list = []
	temp=[]
	while True:
		try:
			msg = queue.get()
			if len(msg) == packet_size:
				if msg[1] == 0 and msg[2] == 0:
					accX = struct.unpack('<f', msg[3:7])
					accY = struct.unpack('<f', msg[7:11])
					accZ = struct.unpack('<f', msg[11:15])
					temp = [accX[0] ,accY[0],accZ[0]]
					
					#print('x = %.2f' % struct.unpack('<f', msg[3:7]))   # little endian
					#print('y = %.2f' % struct.unpack('<f', msg[7:11]))
					#print('z = %.2f' % struct.unpack('<f', msg[11:15]))
				elif msg[1] == 0 and msg[2] == 1:
					gyroX = struct.unpack('<f', msg[3:7])
					gyroY = struct.unpack('<f', msg[7:11])
					gyroZ = struct.unpack('<f', msg[11:15])
					#print('gx = %.2f' % struct.unpack('<f', msg[3:7]))   # little endian
					#print('gy = %.2f' % struct.unpack('<f', msg[7:11]))
					#print('gz = %.2f' % struct.unpack('<f', msg[11:15]))
					'''
					if count < 1200: #csv code
						write_list.append(temp + [gyroX[0],gyroY[0],gyroZ[0]])
						print(*(temp + [gyroX[0],gyroY[0],gyroZ[0]]))
						count+=1
					elif count == 1200:
                                                with open('data.csv', 'a', newline = '') as myFile:
                                                        writer = csv.writer(myFile)
                                                        writer.writerows(write_list)
                                                        myFile.close()
                                                        count+=1
                                                        print('done')
                                        '''
						
					


				elif msg[1] == 1 and msg[2] == 0: #bullet shooting packet
					if msg[3] == 1:
						print('shot fired')
					else:
						print('no shoot')
				elif msg[1] == 1 and msg[2] == 1: #shot registered packet
					if msg[3] == 1:
						print('hit target')	
				#print('data received is %.2f' % struct.unpack('<f',msg[3:7]))
				#success_counter += 1
				#current_time = time.time()
			#if current_time - start_time > 10:
				#speed = success_counter * 20 / (1000 * (current_time - start_time))
				#print('speed is ' + str(speed) + 'kbps')
				#start_time = current_time

		except KeyboardInterrupt:
			break
		
def calculate_checksum(data):

	checksum = 0

	for i in range(len(data) - 1):
		checksum = (checksum ^ data[i]) & 0xFF
	if checksum == data[len(data) - 1]:
		return True
	else:
		return False



if __name__ == '__main__':

	mac_list = ['D0:39:72:BF:C8:B2']
	bluno_list = []
	char_list = []
	aaa_list = []

	for mac in mac_list:
		bluno, char, aaa = bluno_connection(mac)
		bluno_list.append(bluno)
		char_list.append(char)
		aaa_list.append(aaa)
	t_count = 1
	for (b, c, m, a) in zip(bluno_list, char_list, mac_list, aaa_list):
		t = Thread(target = bluno_thread, args = (b, c, m, a, t_count, ))
		t.start()
		t_count += 1
		
	t_print_data = Thread(target = print_data, args = (q,))
	t_print_data.start()


	# mac_list = ['D0:39:72:BF:C6:38', 'D0:39:72:BF:CA:CE','D0:39:72:BF:CD:51'] #1 player mpu, gun, vest
	# mac_list = ['D0:39:72:BF:CA:9E', 'D0:39:72:BF:CA:CE'] #mpu, gun, vest
