# import json

from random import random, choice


MESSAGE_DELIMITER = "|"
# To eval server
EVAL_ACTIONS = ["shoot", "shield", "grenade", "reload"]
# To phone clients
GAME_ACTIONS = ["shoot", "shield", "grenade", "reload", "hit", "logout"]

# mapping device id to player, to be changed
# MAPPING = {
#     "1": "1",
#     "2": "1",
#     "3": "1",
#     "4": "2",
#     "5": "2",
#     "6": "2"
# }

class Data(object):
    
    def __init__(self, type, nfields) -> None:
        # nfields optional, can be used to check number of fields received is correct
        self.type = type
        self.nfields = nfields
        
    def __repr__(self) -> str:
        return self.delimited_string()
    
    def delimited_string(self) -> str:
        # FORMAT: "TYPE|NFIELDS|FIELD1|FIELD2..."
        string = ""
        for v in self.__dict__.values():
            string += str(v) + MESSAGE_DELIMITER
        return string[:-1]
    

class Eval_Action(Data):
    
    def __init__(self, action1, action2, type="eval", nfields=4) -> None:
        super().__init__(type, nfields)
        self.action1 = action1
        self.action2 = action2
    
    def __repr__(self) -> str:
        return "#" + self.action1.action + "|" + self.action2.action
        
class Game_Action(Data):
    
    def __init__(self, player, action, type="action", nfields=4) -> None:
        super().__init__(type, nfields)
        self.player = player
        self.action = action
        
    def get_action(self) -> str:
        return self.action
        

class MPU(Data):
    
    def __init__(self, player_id, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, type="mpu", nfields=9) -> None:
        super().__init__(type, nfields)
        self.player_id = player_id
        self.acc_x = acc_x
        self.acc_y = acc_y
        self.acc_z = acc_z
        self.gyro_x = gyro_x
        self.gyro_y = gyro_y
        self.gyro_z = gyro_z

        
class Trigger(Data):
    
    def __init__(self, player_id, type="trigger", nfields=3) -> None:
        super().__init__(type, nfields)
        self.player_id = player_id

class Receiver(Data):
    
    def __init__(self, player_id, type="receiver", nfields=3) -> None:
        super().__init__(type, nfields)
        self.player_id = player_id
        
class TurnAction():
    
    def __init__(self, sim=False) -> None:
        self.p1_action = None
        self.p2_action = None
        self.p1_hit = False
        self.p2_hit = False
        self.sim = sim
        
    def set_p1_action(self, p1_action):
        self.p1_action = p1_action
        if self.sim and self.p1_action in ("shoot", "grenade"):
            self.p2_hit = True
    
    def set_p2_action(self, p2_action):
        self.p2_action = p2_action
        if self.sim and self.p2_action in ("shoot", "grenade"):
            self.p1_hit = True
        
    def set_p1_hit(self):
        self.p1_hit = True
        
    def set_p2_hit(self):
        self.p2_hit = True
        
    def is_complete(self):
        return not (self.p1_action is None or self.p2_action is None)
    
    def reset(self):
        self.p1_action = None
        self.p2_action = None
        self.p1_hit = False
        self.p2_hit = False

    def force_action(self):
        # if the other player hit, guess opp shot
        if self.p1_hit and self.p2_action is None:
            self.p2_action = "shoot"

        if self.p2_hit and self.p1_action is None:
            self.p1_action = "shoot"

        if not self.p1_action:
            self.set_p1_action(choice(EVAL_ACTIONS))
        
        if not self.p2_action:
            self.set_p2_action(choice(EVAL_ACTIONS))
            
        
    
    def logout(self):
        self.p1_action = "logout"
        self.p2_action = "logout"
        self.p1_hit = False
        self.p2_hit = False
        
    
if __name__ == "__main__":
    ta = TurnAction()
    print(ta.is_complete())
    ta.p1_action = "abc"
    print(ta.is_complete())
    ta.p2_action = "bcd"
    print(ta.is_complete())

'''






'''    

    
