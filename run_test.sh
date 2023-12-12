#!/bin/bash

# Define file to store powermetrics data
# output_file="powermetrics_output.txt"
time_factor=100
output_file="powermetrics_output.txt"

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
    sudo kill $POWERMETRICS_PID

}

# Start powermetrics
start_powermetrics
sleep 2
# Run your program
node webquery1.js
#node webquery2.js
sleep 5

# Once the Node.js program completes, stop powermetrics
stop_powermetrics
echo "Powermetrics data saved to $output_file"

if [[ -s "$output_file" ]]; then
    # Extract CPU Power values, print each, sum them, and multiply by the multiplication factor
    total=$(grep "CPU Power" "$output_file" | awk -v factor=$time_factor '{print $0; sum += $3} END {print "Total (multiplied by factor and divided by 10^6):"; print (sum * factor) / 1000000}')
    echo "Total after multiplying by $time_factor and dividing by 10^6: $total J "
    > "$output_file"
else
    echo "Error: Output file not found or is empty."
fi

