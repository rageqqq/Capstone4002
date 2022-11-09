import socket
import data
import random
from aes import AESCipher
import queue
import threading
import time

import ble
import struct
from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError

HOST = "192.168.95.221"  
PORT = 5353     
q = queue.Queue()
generation_lock = threading.Lock()
SINGLE_PLAYER_MODE = False
data_types = {"mpu":data.MPU}
demo_types = {"mpu":data.MPU}

packet_size = 20
temp = []

class Laptop():
    def __init__(self) -> None:
        self.cipher = AESCipher("PLSPLSPLSPLSWORK")
        self.sock = None
        self.connected = False

    def run(self) -> None:
        while True:
            if not self.connected:
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("Try connecting to ultra96 server...")
                    time.sleep(5)
                    self.sock.connect((HOST, PORT))
                    print("Connected")
                    self.connected = True
                    generation_lock.release()
                except ConnectionRefusedError:
                    print("Connection refused")
                except Exception as e:
                    print(e)
            else:
                
                try:
                    #if ble.q.qsize() > 0:
                    msg = ble.q.get()
                    #print(msg)
                    if len(msg) == packet_size:
                        if msg[1] == 0: #only mpu data has msg[1] == 0,
                            if msg[2] == 0: #accel data
                                accX = struct.unpack('<f', msg[3:7])
                                accY = struct.unpack('<f', msg[7:11])
                                accZ = struct.unpack('<f', msg[11:15])
                                temp = [str(accX[0]), str(accY[0]), str(accZ[0])]
                            elif msg[2] == 1: #gyro data
                                gyroX = struct.unpack('<f', msg[3:7])
                                gyroY = struct.unpack('<f', msg[7:11])
                                gyroZ = struct.unpack('<f', msg[11:15])
                                temp = temp + [str(gyroX[0]), str(gyroY[0]), str(gyroZ[0])]
                                #print (temp)
                                d = 'mpu|1'
                                for item in temp:
                                    d += '|' + item
                                if self.cipher:
                                    enc = self.cipher.encrypt(d)
                                else:
                                    enc = bytes(d, "utf8")
                                self.sock.sendall((str(len(enc))+"_").encode("utf8"))
                                self.sock.sendall(enc)
                        else: #gun and vest data
                            if msg [1] ==1 and msg [2] ==0: #gun packet
                                if msg [3] == 1:
                                    d = 'gun|1'
                                    print("shoot")
                                    if self.cipher:
                                        enc = self.cipher.encrypt(d)
                                    else:
                                        enc = bytes(d, "utf8")
                                    self.sock.sendall((str(len(enc))+"_").encode("utf8"))
                                    self.sock.sendall(enc)                                        
                            elif msg [1] ==1 and msg [2] ==1: #vest packet
                                if msg [3] == 1:
                                    d = 'vest|1'
                                    if self.cipher:
                                        enc = self.cipher.encrypt(d)
                                    else:
                                        enc = bytes(d, "utf8")
                                    self.sock.sendall((str(len(enc))+"_").encode("utf8"))
                                    self.sock.sendall(enc)
                except OSError as ose:
                    print(ose)
                    self.connected = False
                    generation_lock.acquire()
                except Exception as e:
                    print(e)
        

# def generate_data() -> str:
#     while True:
#         if not generation_lock.locked():
#             data_type = random.choice(list(demo_types.keys()))
#             if SINGLE_PLAYER_MODE:
#                 player_id = "1"
#             else:
#                 player_id = random.choice(["1", "2"])
#             if data_type == "mpu":
#                 values = [random.uniform(0, 1) for _ in range(6)]
#                 d = data_types[data_type](player_id, *values)
#             q.put(str(d))
#         time.sleep(5)

if __name__ == "__main__":
	client = Laptop()
	#t1 = threading.Thread(target=generate_data, args=(), daemon=True)
	t2 = threading.Thread(target=client.run, args=(), daemon=True)
	generation_lock.acquire()
	mac_list = ['D0:39:72:BF:C8:B2', 'D0:39:72:BF:CD:51'] #, 'D0:39:72:BF:C6:38'
	bluno_list = []
	char_list = []
	aaa_list = []

	for mac in mac_list:
		bluno, char, aaa = ble.bluno_connection(mac)
		bluno_list.append(bluno)
		char_list.append(char)
		aaa_list.append(aaa)
	t_count = 1
	for (b, c, m, a) in zip(bluno_list, char_list, mac_list, aaa_list):
		t = threading.Thread(target = ble.bluno_thread, args = (b, c, m, a, t_count, ))
		t.start()
		t_count += 1
		
	#t_print_data = threading.Thread(target = ble.print_data, args = (ble.q,))
	#t_print_data.start()


	# mac_list = ['D0:39:72:BF:C8:B2', 'D0:39:72:BF:CD:51', 'D0:39:72:BF:C6:38'] #gun, vest, glove 
	#t1.start()
	t2.start()
	#t1.join()
	t2.join()
