from time import sleep
import sshtunnel
PASSWORD = ''
SUNFIRE = 'sunfire.comp.nus.edu.sg'
ULTRA96 = '192.168.95.221'
LOOPBACK = '127.0.0.1'
SSHPORT = 22
PORT = 5353
def main():
    with sshtunnel.open_tunnel(
        ssh_address_or_host = (SUNFIRE, SSHPORT),
        remote_bind_address = (ULTRA96, SSHPORT),
        ssh_username='',
        ssh_password= PASSWORD,
    ) as tunnel1:
        print(f'Connect to tunnel1 {SUNFIRE}:{SSHPORT} OK...')
        print("LOCAL PORTS:", tunnel1.local_bind_port)
    tunnel1.start()
    with sshtunnel.open_tunnel(
            ssh_address_or_host = (LOOPBACK, tunnel1.local_bind_port),
            remote_bind_address = (ULTRA96, PORT),
            ssh_username='xilinx',
            ssh_password='xilinx',
            local_bind_address=(LOOPBACK, PORT)
        ) as tunnel2:
            print(f"Connect to tunnel2 {ULTRA96}:{PORT} OK...")
            print("LOCAL PORTS:", tunnel2.local_bind_port)
            
            while True:
                sleep(2)
        
if __name__ == "__main__":
    main()
