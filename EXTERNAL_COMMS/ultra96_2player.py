import socket
import threading
import queue
import sys
from GameState import GameState
from aes import AESCipher
import random
import time
from StateStaff import StateStaff
from Helper import ice_print_debug
import json
from paho.mqtt import client as mqtt_client
from overlay import fpga
#from activity_detect import activity
from activity_detect_v4 import activity

#classifier = fpga( "/home/xilinx/model_v1.1.bit",432 )
#classifier = fpga( "/home/xilinx/model_v2.0.bit",432 )
#classifier = fpga( "/home/xilinx/model_v2.1.1.bit",192 )
classifier = fpga( "/home/xilinx/model_v2.1.3.bit",372 )
reading_buffer_1 = activity()
reading_buffer_2 = activity()

broker = 'broker.emqx.io'
mqtt_port = 1883
topic = "python/mqtt/b14"
topic2 = "python/mqtt2/b14"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

HOST = "192.168.95.221" #"192.168.95.221" if sys.platform == "linux" else "127.0.0.1"   
PORT = 5353
EVAL_SERVER = "137.132.92.82"
EVAL_PORT = 9999
ACTIONS = ["shoot", "shield", "grenade", "reload"]

recv = queue.Queue()
recv2 = queue.Queue()
phone = queue.Queue()

game_state = GameState()
state_staff = StateStaff()

recv_lock = threading.Lock()
send_lock = threading.Lock()
send_lock2 = threading.Lock()

count2 = 0
old_act = 'none'
old_act2 = 'none'
MEASURE_TIME = False
start = time.time()
count = 0

# phone.put('{"p1": {"hp": 80, "action": "logout", "bullets": 5, "grenades": 1, "shield_time": 10, "shield_health": 0, "num_deaths": 0, "num_shield": 0}, "p2": {"hp": 60, "action": "grenade", "bullets": 3, "grenades": 1, "shield_time": 0, "shield_health": 0, "num_deaths": 0, "num_shield": 2}}')
MAP = {0:"grenade",
       1:"logout",
       2:"reload",
       3:"shield",
       4: "none"
       }
test_action = 'logout'
p1_actions = iter(['shield', 'grenade', 'reload', 'shoot', 'shoot', 'shield', 'shoot', 'shoot', 'reload', 'shield', 'grenade', 'shield', 'shoot', 'shield', 'shoot', 'shoot', 'reload', 'shoot', 'shoot', 'grenade', 'grenade', 'grenade', 'grenade', 'reload', 'shoot', 'shoot', 'reload', 'reload', 'shield', 'reload', 'shield', 'shoot', 'grenade', 'logout'])

p2_actions = iter(['reload', 'shield', 'shoot', 'grenade', 'grenade', 'shoot', 'shield', 'grenade', 'reload', 'reload', 'shoot', 'shoot', 'shoot', 'grenade', 'grenade', 'shoot', 'shield', 'shoot', 'shield', 'reload', 'shoot', 'shoot', 'shield', 'shoot', 'shield', 'reload', 'reload', 'shoot', 'reload', 'grenade', 'grenade', 'shield', 'shoot', 'logout'])

p1_pos = iter([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4])

p2_pos = iter([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2])

class DataServer():
    '''
    Receive data from laptop and put data to recv queue
    '''
    def __init__(self) -> None:   
        self.cipher = AESCipher("PLSPLSPLSPLSWORK")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))
        self.sock.listen()

    def receive_data(self, conn, addr) -> None:
        while True:
            try:
                # recv length followed by '_' followed by cypher
                data = b''
                while not data.endswith(b'_'):
                    _d = conn.recv(1)
                    if not _d:
                        data = b''
                        break
                    data += _d
                    
                if len(data) == 0:
                    raise Exception("stop")

                data = data.decode("utf8")
                length = int(data[:-1])

                recv_data = b''
                while len(recv_data) < length:
                    _d = conn.recv(length - len(recv_data))
                    if not _d:
                        recv_data = b''
                        break
                    recv_data += _d

                if recv_lock.locked():
                    continue
                
                if recv_data:
                    if self.cipher:
                        sensor_data = self.cipher.decrypt(recv_data)
                    else:
                        sensor_data = recv_data
                    #print(f"Received {sensor_data} from {addr}")
                    sensor_data = sensor_data.decode("utf8")
                    temp = sensor_data.split("|")
                    # for player 1
                    if temp [0] == 'mpu' and temp [1] == '1':
                        data_array = temp[2:] # string
                        v = [float(x) for x in data_array] # list of floats
                        #print (v)
                        data_1 = reading_buffer_1.update(v)
                        #print(type(sensor_data))
                        
                        if data_1 is not None:
                            #action1 = MAP.get(classifier.classify(data_1))
                            action1 = MAP.get(classifier.classify_v2(data_1))
                            print(action1 + "1")
                            if action1 != 'none':
                                recv.put(action1)
                    elif temp [0] == 'gun' and temp [1] == '1':
                        action1 = 'shoot'
                        print(action1 +"1")
                        recv.put(action1)
                    elif temp [0] == 'vest' and temp [1] == '1':
                        action1 = 'bullet_hit'
                        print(action1 +"1")
                        recv.put(action1)

                    # for player 2
                    elif temp [0] == 'mpu' and temp [1] == '2':
                        data_array = temp[2:] # string
                        v = [float(x) for x in data_array] # list of floats
                        #print (v)
                        data_2 = reading_buffer_2.update(v)
                        #print(type(sensor_data))
                    
                        if data_2 is not None:
                            action2 = MAP.get(classifier.classify_v2(data_2))
                            #action1 = MAP.get(classifier.classify_v2(data_1))
                            print(action2 + "2")
                            if action2 != 'none':
                                recv2.put(action2)
                    elif temp [0] == 'gun' and temp [1] == '2':
                        action2 = 'shoot'
                        print(action2 + "2")
                        recv2.put(action2)
                    elif temp [0] == 'vest' and temp [1] == '2':
                        action2 = 'bullet_hit'
                        recv2.put(action2)
                        print(action2 +"2")
                    if MEASURE_TIME:
                        global count
                        count += 1
                        print(f"Count: {count} \t Time elapsed: {time.time() - start}")

            except ConnectionResetError:
                print("Disconnected from laptop")
                self.sock.close()
            except Exception as e:
                print(f"Exception from data server: {e}")
                if e.args[0] == "stop":
                    return
                self.sock.close()
                    
    def run(self):
        while True:
            conn, addr = self.sock.accept()
            print(f"accepted connection from: {addr}")
            threading.Thread(target=self.receive_data, args=(conn, addr), daemon=True).start()

    



class EvalClient():
    '''
    Send and receive data from eval server
    '''
    
    def __init__(self) -> None:
        # From eval server
        self.cipher = AESCipher("PLSPLSPLSPLSWORK")
        self.secretkey = "PLSPLSPLSPLSWORK"
        self.sock = None
        self.connected = False

    def recv_and_update(self, remote_socket):
        success = False
        while True:
            # recv length followed by '_' followed by cypher
            data = b''
            while not data.endswith(b'_'):
                _d = remote_socket.recv(1)
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from', remote_socket)
                break

            data = data.decode("utf-8")
            length = int(data[:-1])

            data = b''
            while len(data) < length:
                _d = remote_socket.recv(length - len(data))
                if not _d:
                    data = b''
                    break
                data += _d
            if len(data) == 0:
                print('no more data from', remote_socket)
                break
            msg = data.decode("utf8")  # Decode raw bytes to UTF-8
            msg = msg.split('#')[0]
            game_state_received = json.loads(msg)

            ice_print_debug(game_state_received)
            game_state.player_1.initialize_from_dict(game_state_received['p1'])
            game_state.player_2.initialize_from_dict(game_state_received['p2'])
            success = True
            break
        return success


    def run(self) -> None:

        while True:
            if not self.connected:
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("Try connecting to eval server...")
                    time.sleep(5)
                    self.sock.connect((EVAL_SERVER, EVAL_PORT))
                    print("Connection established")
                    self.connected = True
                    recv_lock.release()

                except ConnectionRefusedError:
                    print("Connection refused")
                except Exception as e:
                    print(f"Exception from eval client: {e}")
            else:
                try:
                    
                    while True:

                        # time.sleep(10)
                            # pos_1 pos_2 action_p1, action_p2, action_p1_valid   
                        global old_act
                        global old_act2
                        if recv.qsize() > 0:
                            temp = recv.get()
                            action1 = temp
                        
                            if action1 == 'none':
                                continue                                    
                            if action1 == 'bullet_hit' :
                                
                                game_state.player_1.update(1,1,old_act, 'shoot' ,game_state.player_2.action_is_valid('shoot'))
                            elif action1 == 'grenade' :
                               
                                game_state.player_1.update(1,1,'grenade', old_act2 ,False)
                                phone.put(game_state._get_data_plain_text())   
                                old_act = action1                         
                            elif action1 == 'grenade hit p1' :
                                
                                game_state.player_1.update(1,1,old_act, 'grenade' ,game_state.player_2.action_is_valid('grenade'))
                            elif action1 != 'grenade miss p1':
                                
                                game_state.player_1.update(1,1, action1, old_act2,False)  
                                old_act = action1
                                
                            if send_lock.locked() and (action1 != 'grenade hit p1' and action1 != 'bullet_hit' and action1 != 'grenade miss p1'):
                                send_lock.release()
                                                      
                        if recv2.qsize() > 0:                           
                            temp = recv2.get()
                            action2 = temp
                            if action2 == 'none':
                                continue                                    
                            if action2 == 'bullet_hit' :
                                
                                game_state.player_2.update(1,1,old_act2, 'shoot' ,game_state.player_1.action_is_valid('shoot'))
                            elif action2 == 'grenade' :
                               
                                game_state.player_2.update(1,1,'grenade', old_act ,False)
                                phone.put(game_state._get_data_plain_text())
                                old_act2 = action2
                            elif action2 == 'grenade hit p2' :
                                
                                game_state.player_2.update(1,1,old_act2, 'grenade' ,game_state.player_1.action_is_valid('grenade'))                               
                            elif action2 != 'grenade miss p2':
                                
                                game_state.player_2.update(1,1,action2, old_act ,False)   
                                old_act2 = action2                   
                            if send_lock2.locked() and (action2 != 'grenade hit p2' and action2 != 'bullet_hit' and action2 != 'grenade miss p2'):
                                send_lock2.release()
                        
                        if (not send_lock.locked() and not send_lock2.locked()) and recv.empty() and recv2.empty():
                            global count2
                            if count2 > 5:
                                self.cipher.send_encrypted(game_state._get_data_plain_text(), self.sock, self.secretkey)
                                phone.put(game_state._get_data_plain_text())
                                _ = self.recv_and_update(self.sock) 
                                send_lock.acquire() 
                                send_lock2.acquire()
                                count2 = 0
                            else:
                                count2 +=1

                            
                                

                except OSError as ose:
                    print("eval server down")
                    self.connected = False
                    recv_lock.acquire()
                except Exception as e:
                    print(f"Exception from eval client: {e}")
                    time.sleep(5)

class MQTTHandler():

    def __init__(self) -> None:
        pass

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, mqtt_port)
        return client

    def publish(self, client):
        while True:
            if phone.qsize() > 0:
                msg = f"{phone.get()}"
                result = client.publish(topic, msg)
                # result: [0, 1]
                status = result[0]
                if status == 0:
                    print(f"Send `{msg}` to topic `{topic}`")
                else:
                    print(f"Failed to send message to topic {topic}")

    def subscribe(self, client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}`")
            if msg.payload.decode() == 'grenade hit p1':
                recv.put('grenade hit p1')
            if msg.payload.decode() == 'grenade hit p2':
                recv2.put('grenade hit p2')               
            if msg.payload.decode() == 'grenade miss p1':
                recv.put('grenade miss p1')
            if msg.payload.decode() == 'grenade miss p2':
                recv2.put('grenade miss p2')  
        client.subscribe(topic2)
        client.on_message = on_message

    def run(self) -> None:
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_start()
        self.publish(client)

if __name__ == "__main__":
    data_server = DataServer()
    eval_client = EvalClient()
    mqtt_handler = MQTTHandler()
    t1 = threading.Thread(target=eval_client.run, args=(), daemon=True)
    t2 = threading.Thread(target=data_server.run, args=(), daemon=True)
    t3 = threading.Thread(target=mqtt_handler.run, args=(), daemon=True)
    recv_lock.acquire()
    send_lock.acquire()
    send_lock2.acquire()
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
