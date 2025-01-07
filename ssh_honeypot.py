# Libraries
import logging 
from logging.handlers import RotatingFileHandler
import socket
import paramiko 
import threading

# Constants
logging_format = logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

#host_key = 'server.key' #NEED TO REDACT THIS BEFORE POSTING
host_key = paramiko.RSAKey(filename='server.key') #loads the RSA key from the file

# Loggers & Logging Files
funnel_logger = logging.getLogger('FunnelLogger') #captures username/password/ipaddress/etc.
funnel_logger.setLevel(logging.INFO) #provides the INFO level of logging
funnel_handler = RotatingFileHandler('audits.log', maxBytes=2000, backupCount=5) #rotates the log file after 2000 bytes and keeps 5 backup copies
funnel_handler.setFormatter(logging_format) #sets the format of the log file
funnel_logger.addHandler(funnel_handler) #adds the handler to the logger

creds_logger = logging.getLogger('CredsLogger') #captures username/password/ipaddress/etc.
creds_logger.setLevel(logging.INFO) #provides the INFO level of logging
creds_handler = RotatingFileHandler('cmd_audits.log', maxBytes=2000, backupCount=5) #rotates the log file after 2000 bytes and keeps 5 backup copies
creds_handler.setFormatter(logging_format) #sets the format of the log file
creds_logger.addHandler(creds_handler) #adds the handler to the logger

# Emulated Shell

def emulated_shell(channel, client_ip):
    channel.send(b"corporate-jumpbox2$ ") #sends the default dialogue box
    command = b"" #listens to the characters being put in
    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()

        command += char #adds all of the characters into one string

        if char == b'\r':
            if command.strip() == b'exit':
                response = b'\n Goodbye!\n'
                channel.close()
            elif command.strip() == b'pwd': #.strip strips formatting and gives raw input
                response = b"\n" +  b'\\usr\\local' + b'\r\n'
                creds_logger.info(f'Command {command.strip()} '+ f'executed by {client_ip}')
            elif command.strip() == b'whoami':
                response = b"\n" + b"corpuser1" + b"\r\n"
                creds_logger.info(f'Command {command.strip()} '+ f'executed by {client_ip}')
            elif command.strip() == b'ls':
                response = b'\n' + b"jumpbox1.conf" + b"\r\n" 
                creds_logger.info(f'Command {command.strip()} '+ f'executed by {client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                response = b'\n' + b"Go to crazy.com" + b"\r\n"
                creds_logger.info(f'Command {command.strip()} '+ f'executed by {client_ip}')
            else:
                response = b"\n" + bytes(command.strip()) + b"\r\n"
                creds_logger.info(f'Command {command.strip()} '+ f'executed by {client_ip}')

        #resets the default dialogue box and listens for the next command        
            channel.send(response)
            channel.send(b'corporate-jumpbox2$ ')
            command = b"" #resets the command to an empty string

# SSH Server & Sockets


class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def get_allowed_auths(self, username):
        return "password"   
    
    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with ' + f'username: {username}, ' + f'password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}')
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else: 
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL
        
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True
def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"Connection from {client_ip}")


    try:

        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        
        transport.add_server_key(host_key) 

        transport.start_server(server=server)   

        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.")
            
        standard_banner = "Welcome! You have successfully connected to the SSH server.\r\n\r\n"
        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)
    except Exception as error:
        print(error)
        print("Error occurred.")
    finally:
        try:
            transport.close()
        except Exception as error:
            print(error)
            print("Error occurred while closing transport.")
        client.close()

# Provision SSH-based Honeypot

def honeypot(address, port, username, password):
    
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(100)
    print(f"Listening on port {port}.")

    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
        except Exception as error:
            print(error)

#honeypot('127.0.0.1', 2223, username=None, password=None)