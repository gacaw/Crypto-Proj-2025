import socket
import select
import config
import ecc
import aes
import rng
import tunnel

def log(message):
    print(f"[SERVER] {message}")

MAX_UINT128 = 2**128 - 1

class ATM:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        if amount < 0:
            return -1
        if self.balance + amount > MAX_UINT128:
            return -1
        #self.balance += amount
        return 1

    def withdraw(self, amount):
        if amount < 0:
            return -1
        if amount > self.balance:
            return -1
        #self.balance -= amount
        return 1

def run_server():
    # Public key used for ECC by the server.
    ecc_public_key = config.ecc_server_public_key

    # Private key used for ECC by the server.
    # Note for black-hat team: assume this variable is unknown to outside adversaries.
    ecc_private_key = 87798100903066519588590744632561003404502293149715811333515161063468035673028

    # Initialize RNG using a secret factor constructed from the private key
    rng.init_bbs(((ecc_private_key & 0xFFFF) * 7) + 13)
    
    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind server to an ip and port and then listen for connections
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((config.server_ip, config.server_port))
    server.listen(0)

    log(f"Listening on {config.server_ip}:{config.server_port}")

    server_closed = False
    while not server_closed:
        log("Waiting for new connections")

        # Accept incoming connections until we find a valid client
        client_socket = None
        client_address = None
        found_valid_client = False
        nonce = None
        while not found_valid_client:
            client_socket, client_address = server.accept()
            log(f"Accepted connection from {client_address[0]}:{client_address[1]}")

            # Prevent complete DOS from bad clients
            client_socket.setblocking(0)
            ready = select.select([client_socket], [], [], 1)
            if not ready[0]:
                log("Connection timed out")
                client_socket.close()
                continue

            ecc_client_public_key_message = client_socket.recv(1024).decode("utf-8")
            ecc_client_public_key = ecc.Point(0, 0)
            ecc_client_public_key.set_from_message(ecc_client_public_key_message)
            if not ecc_client_public_key.equals(config.ecc_client_public_key):
                log("Failed to make secure connection with client; unknown public key")
                client_socket.close()
                continue

            # Calculate shared secret
            ecc_shared_secret = ecc.point_multiply(ecc_client_public_key, ecc_private_key)
            shared_aes_key = ecc_shared_secret.x & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

            # Send our public key to client now
            client_socket.send(ecc_public_key.to_message().encode("utf-8")[:1024])
            
            # Prevent complete DOS from bad clients
            ready = select.select([client_socket], [], [], 1)
            if not ready[0]:
                log("Connection timed out")
                client_socket.close()
                continue

            # Receive random_secret_1, and permute it using ((random_secret_1 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            random_secret_1_msg = aes.decrypt(client_socket.recv(16), shared_aes_key.to_bytes(16, "little"))
            random_secret_1 = int.from_bytes(random_secret_1_msg, "little")
            random_secret_2 = ((random_secret_1 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            client_socket.send(aes.encrypt(random_secret_2.to_bytes(16, "little"), shared_aes_key.to_bytes(16, "little"))[:16])

            # Challenge client to double verify we have a valid shared secret
            random_secret_3 = rng.generate_random_number(128)
            client_socket.send(aes.encrypt(random_secret_3.to_bytes(16, "little"), shared_aes_key.to_bytes(16, "little"))[:16])

            # Prevent complete DOS from bad clients
            ready = select.select([client_socket], [], [], 1)
            if not ready[0]:
                log("Connection timed out")
                client_socket.close()
                continue

            # Expect client to permute the secret using ((random_secret_3 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            random_secret_4_msg = aes.decrypt(client_socket.recv(16), shared_aes_key.to_bytes(16, "little"))
            random_secret_4 = int.from_bytes(random_secret_4_msg, "little")
            if random_secret_4 != (((random_secret_3 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF):
                log("Failed to verify random secret with client")
                client_socket.close()
                continue

            found_valid_client = True
            nonce = random_secret_4
        
        log("Successfully found valid client!")

        # receive data from the client
        while True:
            # Time out after 5 minutes
            ready = select.select([client_socket], [], [], 60 * 5)
            if not ready[0]:
                log("Connection timed out")
                client_socket.close()
                break

            msg = client_socket.recv(80)
            if not msg:
                break

            # Decrypt message
            msg_type, msg_data = tunnel.decrypt_message(shared_aes_key, msg, nonce)
            if not msg_type or not msg_data:
                continue
            nonce = tunnel.next_nonce(nonce)

            msg_str = msg_type[0:16].rstrip(b"\x00").decode("utf-8").strip()
            value = int.from_bytes(msg_data, "little")
            log(f"Client command: {msg_str} | Value: {value}")

            # Prepare response
            if msg_str == "deposit":
                result = atm.deposit(value)
                if result == -1:
                    response_type = "inv_deposit"
                else:
                    response_type = "deposit"

                response_data = atm.balance.to_bytes(16, "little")

            elif msg_str == "withdraw":
                result = atm.withdraw(value)
                if result == -1:
                    response_type = "inv_withdraw"
                else:
                    response_type = "withdraw"

                response_data = atm.balance.to_bytes(16, "little")

            elif msg_str == "balance":
                response_type = "balance"
                response_data = atm.balance.to_bytes(16, "little")

            elif msg_str == "disconnect":
                response_type = "disconnect"
                response_data = bytearray("Goodbye".encode())[:16].ljust(16, b'\x00')
                encrypted_response = tunnel.encrypt_message(
                    shared_aes_key,
                    nonce,
                    bytearray(response_type.encode())[:16].ljust(16, b'\x00'),
                    response_data
                )
                client_socket.send(encrypted_response)
                client_socket.close()
                break

            elif msg_str == "close":
                response_type = "close"
                response_data = bytearray("Goodbye".encode())[:16].ljust(16, b'\x00')
                encrypted_response = tunnel.encrypt_message(
                    shared_aes_key,
                    nonce,
                    bytearray(response_type.encode())[:16].ljust(16, b'\x00'),
                    response_data
                )
                client_socket.send(encrypted_response)
                client_socket.close()
                server_closed = True
                break

            else:
                response_type = "error"
                response_data = bytearray("Unknown cmd".encode())[:16].ljust(16, b'\x00')

            encrypted_response = tunnel.encrypt_message(
                shared_aes_key,
                nonce,
                bytearray(response_type.encode())[:16].ljust(16, b'\x00'),
                response_data
            )
            client_socket.send(encrypted_response)
            nonce = tunnel.next_nonce(nonce)


# Entry point of program
if __name__ == "__main__":

    atm = ATM()

    run_server()