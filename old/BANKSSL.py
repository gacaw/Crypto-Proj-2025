import socket
import ecc
import hmacFile
import desLarge

class Server:
    def __init__(self):
        self.curve = ecc.EllipticCurve(a=int(0xfffffffffffffffffffffffffffffffefffffffffffffffc),
                                       b=int(0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1),
                                       p=int(0xfffffffffffffffffffffffffffffffeffffffffffffffff))
        self.G = (int(0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012),
                  int(0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811))
        self.private_key = None
        self.public_key = None
        self.session_key = None
        self.hmac = hmacFile.Hmac()

    def generate_keys(self):
        self.private_key = 67890  # Replace with a secure random number
        self.public_key = self.curve.scalar_multiplication(self.private_key, self.G)

    def perform_handshake(self, client_socket):
        # Step 1: Receive client's public key
        client_public_key = eval(client_socket.recv(1024).decode())

        # Step 2: Send server's public key
        client_socket.sendall(str(self.public_key).encode())

        # Step 3: Compute shared secret
        shared_secret = self.curve.scalar_multiplication(self.private_key, client_public_key)

        # Step 4: Derive session key
        self.session_key = str(shared_secret[0])[:32]  # Use the x-coordinate as the session key

        # Step 5: Receive client's HMAC for verification
        client_hmac = client_socket.recv(1024)
        expected_hmac = self.hmac.hmac(str(shared_secret[0]).encode(), b"ClientHello", self.hmac.sha1)

        if client_hmac != expected_hmac:
            print("Handshake failed: HMAC verification failed.")
            client_socket.close()
            return False

        # Step 6: Send HMAC for authentication
        hmac_tag = self.hmac.hmac(str(shared_secret[0]).encode(), b"ServerHello", self.hmac.sha1)
        client_socket.sendall(hmac_tag)

        print("Handshake successful. Session key established.")
        return True


# for testing
if __name__ == "__main__":
    server = Server()
    server.generate_keys()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 12345))
        server_socket.listen(1)
        print("Server is listening...")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            server.perform_handshake(conn)