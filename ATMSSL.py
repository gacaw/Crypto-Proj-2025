import socket
from datetime import datetime

from des import Prng
from hmacFile import Hmac
from ecc import EllipticCurve


class Client:
    def __init__(self):
        self.curve = EllipticCurve(a=int(0xfffffffffffffffffffffffffffffffefffffffffffffffc),
                                       b=int(0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1),
                                       p=int(0xfffffffffffffffffffffffffffffffeffffffffffffffff))
        self.G = (int(0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012),
                  int(0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811))
        self.private_key = None
        self.public_key = None
        self.session_key = None
        self.hmac = Hmac()

    def generate_keys(self):
        # Get the current timestamp
        now = datetime.now()
        timestamp = now.timestamp()

        # Convert the timestamp to binary
        binary_timestamp = ''.join(format(ord(char), '08b') for char in str(timestamp))

        key1 = binary_timestamp[0:32] + binary_timestamp[-33:-1]
        key2 = binary_timestamp[1:33] + binary_timestamp[-33:-1]
        key3 = binary_timestamp[2:34] + binary_timestamp[-33:-1]
        seed = binary_timestamp[3:35] + binary_timestamp[-33:-1]

        # # Extract 10-bit keys and an 8-bit seed from the binary timestamp
        # key1 = binary_timestamp[0:10]
        # key2 = binary_timestamp[10:20]
        # key3 = binary_timestamp[20:30]
        # seed = binary_timestamp[30:38]

        prng = Prng(key1, key2, key3, seed)

        self.private_key = prng.nextInt()
        self.public_key = self.curve.scalar_multiplication(self.private_key, self.G)

    def perform_handshake(self, server_address):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(server_address)

            #send public key to server
            client_socket.sendall(str(self.public_key).encode())

            #receive server's public key
            server_public_key = eval(client_socket.recv(1024).decode())

            #compute shared secret
            shared_secret = self.curve.scalar_multiplication(self.private_key, server_public_key)

            #derive session key
            self.session_key = str(shared_secret[0])[:32]  # Use the x-coordinate as the session key

            #send HMAC for authentication
            hmac_tag = self.hmac.hmac(str(shared_secret[0]).encode(), b"ClientHello", self.hmac.sha1)
            client_socket.sendall(hmac_tag)

            #receive server's HMAC for verification
            server_hmac = client_socket.recv(1024)
            expected_hmac = self.hmac.hmac(str(shared_secret[0]).encode(), b"ServerHello", self.hmac.sha1)

            if server_hmac != expected_hmac:
                print("Handshake failed: HMAC verification failed.")
                return False

            print("Handshake successful. Session key established.")
            return True

#for testing
if __name__ == "__main__":
    client = Client()
    client.generate_keys()
    server_address = ('localhost', 12345)
    client.perform_handshake(server_address)