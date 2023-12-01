#!/bin/bash

# Define file to store powermetrics data
# output_file="powermetrics_output.txt"

# Function to start powermetrics
start_powermetrics() {
    # Start powermetrics with a sampling interval of 100ms (0.1 second)
    sudo powermetrics -i 100 -f text -o "powermetrics_output.txt" &
    # Save the PID of powermetrics
    POWERMETRICS_PID=$!
    #echo "Powermetrics started with PID: $POWERMETRICS_PID"
}

# Function to stop powermetrics
stop_powermetrics() {
    # Kill the powermetrics process
    #echo "Stopping powermetrics (PID: $POWERMETRICS_PID)..."
    sleep 1
    sudo kill $POWERMETRICS_PID

}

# Start powermetrics
start_powermetrics
sleep 1
# Run your Node.js program
node index.js

# Once the Node.js program completes, stop powermetrics
stop_powermetrics

echo "Powermetrics data saved to $output_file"

grep "CPU Power" powermetrics_output.txt | awk '{print $3}'