import socket
import threading
import random
import hashlib

class Server:

    def __init__(self, port: int) -> None:
        self.host = '127.0.0.1'
        self.port = port
        self.clients = []
        self.username_lookup = {}
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(100)

        self.public_key, self.private_key = generate_keypair(61, 53)

        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
           
            self.username_lookup[c] = username
            self.clients.append(c)

            # send public key to the client
            c.send(str(self.public_key).encode())

            # receive client's public key
            client_pk = eval(c.recv(1024).decode())
            self.client_keys[c] = client_pk

            # encrypt the secret with the clients public key
            secret = random.randint(1, 255)
            self.session_keys[c] = secret

            e, n = client_pk
            encrypted_secret = pow(secret, e, n)

            # send the encrypted secret to a client
            c.send(str(encrypted_secret).encode())
            self.broadcast(f'new person has joined: {username}')
            threading.Thread(target=self.handle_client,args=(c,addr,)).start()

    
    def broadcast(self, msg: str):
    
        for client in self.clients:
            msg_hash = hashlib.sha256(msg.encode()).hexdigest()
    
            client_pk = self.client_keys[client]
            encrypted_msg = encrypt(client_pk, msg)
    
            packet = f"{msg_hash}::{encrypted_msg}"
    
            client.send(packet.encode())


    def handle_client(self, c: socket, addr): 
        while True:
            msg = c.recv(1024)

            for client in self.clients:
                if client != c:
                    client.send(msg)

if __name__ == "__main__":
    s = Server(9001)
    s.start()
