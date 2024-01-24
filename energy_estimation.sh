# run with "bash energy_estimation"

time_factor=100
output_file="powermetrics_output.txt" # Scrape powermetrics data from termnal

start_powermetrics() {
    # Start powermetrics with a sampling interval of 100ms (0.1 second)
    sudo powermetrics -i 100 -f text -o "powermetrics_output.txt" &
    # Save the PID of powermetrics
    POWERMETRICS_PID=$!
    sleep 1.5
}

stop_powermetrics() {
    # Kill the powermetrics process
    sleep 1
    sudo kill $POWERMETRICS_PID
}

# Start powermetrics
start_powermetrics

# Run your program
python3 testing_programs/twosum1.py

# Once the execution completes, stop powermetrics
stop_powermetrics

echo "Powermetrics data saved to $output_file"

if [[ -s "$output_file" ]]; then
    # Extract CPU Power values, print each, sum them, and multiply by the multiplication factor
    total=$(grep "CPU Power" "$output_file" | awk -v factor=$time_factor '{print $0; sum += $3} 
    END {print "Total (multiplied by factor and divided by 10^6):"; print (sum * factor) / 1000000}')
else
    echo "Error: Output file not found or is empty."
fi
echo "Total after multiplying by $time_factor and dividing by 10^6: $total J "