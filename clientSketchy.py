import socket
import config
import ecc
import aes
import rng
import tunnel

def log(message):
    print(f"[CLIENT] {message}")

def run_client():
    # Public key used for ECC by the client.
    ecc_public_key = config.ecc_client_public_key

    # Private key used for ECC by the client.
    # Note for black-hat team: assume this variable is unknown to outside adversaries.
    ecc_private_key = 98809871890370349032600643223901530565260343024217164390661078677501054730141

    # Initialize RNG using a secret factor constructed from the private key
    rng.init_bbs(((ecc_private_key & 0xFFFF) * 7) + 13)

    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # establish connection with server
    client.connect((config.server_ip, config.server_port))

    # Send public key to server
    client.send(ecc_public_key.to_message().encode("utf-8")[:1024])

    # Wait for public key from server
    ecc_server_public_key_message = client.recv(1024)
    ecc_server_public_key = ecc.Point(0, 0)
    ecc_server_public_key.set_from_message(ecc_server_public_key_message)
    if not ecc_server_public_key.equals(config.ecc_server_public_key):
        log("Failed to make secure connection with server; unknown public key")
        client.close()
        return
    
    # Construct shared secret key
    ecc_shared_secret = ecc.point_multiply(ecc_server_public_key, ecc_private_key)
    shared_aes_key = ecc_shared_secret.x & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    # Challenge server to verify we have a valid shared secret
    random_secret_1 = rng.generate_random_number(128)
    client.send(aes.encrypt(random_secret_1.to_bytes(16, "little"), shared_aes_key.to_bytes(16, "little"))[:16])

    # Expect server to permute the secret using ((random_secret_1 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    random_secret_2_msg = aes.decrypt(client.recv(16), shared_aes_key.to_bytes(16, "little"))
    random_secret_2 = int.from_bytes(random_secret_2_msg, "little")
    if random_secret_2 != (((random_secret_1 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF):
        log("Failed to verify random secret with server")
        client.close()
        return

    # Receive random_secret_3, and permute it using ((random_secret_3 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    random_secret_3_msg = aes.decrypt(client.recv(16), shared_aes_key.to_bytes(16, "little"))
    random_secret_3 = int.from_bytes(random_secret_3_msg, "little")
    random_secret_4 = ((random_secret_3 * 7) + 13) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    client.send(aes.encrypt(random_secret_4.to_bytes(16, "little"), shared_aes_key.to_bytes(16, "little"))[:16])

    log("Successfully found valid server!")
    nonce = random_secret_4

    while True:
        print("==== ATM Menu ====")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. Exit")
        print("5. Close Server")
        choice = input("[CLIENT] Choose an option (1-5): ").strip()

        if choice == "1":
            amount = input("[CLIENT] Enter amount to deposit: ").strip()
            # Make sure input is a digit
            #if not amount.isdigit():
                #log("Invalid amount. Must be a non-negative integer.")
                #continue
            #amount = int(amount)
            # Make sure we dont overflow 16 bytes of data
            #if amount.bit_length() > 128:
                #log("Amount too large! Must fit within 128 bits (16 bytes).")
                #continue
            msg_type = bytearray("deposit", "utf-8").ljust(16, b'\x00')
            msg_data = amount.encode("utf-8") #amount.to_bytes(16, "little")

        elif choice == "2":
            amount = input("[CLIENT] Enter amount to withdraw: ").strip()
            # Make sure input is a digit
            if not amount.isdigit():
                log("Invalid amount. Must be a non-negative integer.")
                continue
            amount = int(amount)
            # Make sure we dont overflow 16 bytes of data
            if amount.bit_length() > 128:
                log("Amount too large! Must fit within 128 bits (16 bytes).")
                continue
            msg_type = bytearray("withdraw", "utf-8").ljust(16, b'\x00')
            msg_data = int(amount).to_bytes(16, "little")

        elif choice == "3":
            msg_type = bytearray("balance", "utf-8").ljust(16, b'\x00')
            msg_data = (0).to_bytes(16, "little")

        elif choice == "4":
            msg_type = bytearray("disconnect", "utf-8").ljust(16, b'\x00')
            msg_data = (0).to_bytes(16, "little")

        elif choice == "5":
            msg_type = bytearray("close", "utf-8").ljust(16, b'\x00')
            msg_data = (0).to_bytes(16, "little")

        else:
            log("Invalid option.")
            continue

        # Encrypt and send request
        encrypted_msg = tunnel.encrypt_message(shared_aes_key, nonce, msg_type, msg_data)
        client.send(encrypted_msg)
        nonce = tunnel.next_nonce(nonce)

        # Receive and decrypt response
        encrypted_response = client.recv(80)
        resp_type, resp_data = tunnel.decrypt_message(shared_aes_key, encrypted_response, nonce)
        if not resp_type or not resp_data:
            continue
        nonce = tunnel.next_nonce(nonce)

        resp_type_str = resp_type[0:16].rstrip(b"\x00").decode("utf-8").strip()
        resp_data = int.from_bytes(resp_data, "little")

        # Handle server responses
        if resp_type_str == "withdraw":
            log(f"Server Response: Withdrawal successful. New balance: ${resp_data}")
        elif resp_type_str == "inv_withdraw":
            log(f"Server Response: Withdrawal failed. Insufficient funds.")
        elif resp_type_str == "deposit":
            log(f"Server Response: Deposit successful. New balance: ${resp_data}")
        elif resp_type_str == "inv_deposit":
            log(f"Server Response: Deposit failed. Amount too large or invalid.")
        elif resp_type_str == "balance":
            log(f"Server Response: Current balance: ${resp_data}")
        elif resp_type_str == "disconnect":
            log(f"Server Response: Disconnecting. Goodbye!")
            break
        elif resp_type_str == "close":
            log(f"Server Response: Closing server. Goodbye!")
            break
        elif resp_type_str == "error":
            log(f"Server Response: ERROR: An unknown command was received.")
        else:
            log(f"Server Response: Critical error: Invalid response from server. Shutting down client.")
            return

        print()

    # close client socket (connection to the server)
    client.close()
    log("Connection to server closed")


# Entry point of program
if __name__ == "__main__":
    run_client()