import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from GameState import GameState

game_state = GameState()

class AESCipher():

    def __init__(self, secret_key: str): 
        self.skey = bytes(secret_key, "utf8")

    def encrypt(self, data):
        enc = pad(data.encode("utf8"), 16)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.skey, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(enc))
    
    def encrypt_to_phone(self, data):
        enc = pad(bytes(data, "utf8"), 16)
        cipher = AES.new(self.skey, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(enc))

    def decrypt(self, enc):
        dec = base64.b64decode(enc)
        iv = dec[:AES.block_size]
        cipher = AES.new(self.skey, AES.MODE_CBC, iv)
        dec = cipher.decrypt(dec[AES.block_size:])
        return unpad(dec, 16)


    def send_encrypted(self, plaintext, remote_socket, secret_key_string):
        success = True
        print(f"Sending message to server: {plaintext} (Unencrypted)")
        plaintext_bytes = pad(plaintext.encode("utf-8"), 16)

        secret_key_bytes = secret_key_string.encode("utf-8")
        cipher = AES.new(secret_key_bytes, AES.MODE_CBC)
        iv_bytes = cipher.iv
        ciphertext_bytes = cipher.encrypt(plaintext_bytes)
        message = base64.b64encode(iv_bytes + ciphertext_bytes)

        m = str(len(message))+'_'
        try:
            remote_socket.sendall(m.encode("utf-8"))
            remote_socket.sendall(message)
        except OSError:
            print("Connection terminated")
            success = False
        return success