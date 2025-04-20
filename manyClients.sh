#!/bin/bash

# Path to the client script
CLIENT_SCRIPT="python3 client.py"

# Function to open a new terminal window and run the client script
run_client() {
    local index=$1
    xterm -hold -e "$CLIENT_SCRIPT" &
}

# Run 100 client processes in separate windows
for i in $(seq 1 100); do
    run_client $i
done

echo "Successfully launched 100 client processes in separate terminal windows."