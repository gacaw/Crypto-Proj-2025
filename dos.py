import os
import time

if os.fork() == 0:
    os.system('python3 server.py')
    os._exit(0)  

time.sleep(0.1)

# Create 10000 client processes in parallel 
for _ in range(10000):
    if os.fork() == 0:
        os.system('python3 client.py')
        os._exit(0)  # DO NOT REMOVE THIS LINE. I accidentally fork bombed myself 

while True:
    try:
        os.wait()
    except ChildProcessError:
        break