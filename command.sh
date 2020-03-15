#!/bin/bash

input_full=$(mktemp)
output_body=$(mktemp)

# Read STDIN and write out the full mail to a file
cat > $input_full

# Give this input to the command handler and have it write out a full output with headers
./command.py -i $input_full -o $output_body

# Now send the body of the message to mutt for the sender.
echo | mutt -H $output_body

# In the future, delete the temp files here.
# rm $input_full $output_body
