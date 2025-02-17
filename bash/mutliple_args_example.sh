#!/bin/bash

# ./mutliple_args_example.sh --DNS 8.8.8.8 --DNS 1.1.1.1 --IP 192.168.1.1 --IP 10.0.0.1

# Declare arrays to store multiple values
dns_entries=()
ip_entries=()

# Loop through the provided arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --DNS)
            if [[ -n "$2" && "$2" != --* ]]; then
                dns_entries+=("$2")
                shift 2  # Shift past the argument and its value
            else
                echo "Error: --DNS requires a value"
                exit 1
            fi
            ;;
        --IP)
            if [[ -n "$2" && "$2" != --* ]]; then
                ip_entries+=("$2")
                shift 2  # Shift past the argument and its value
            else
                echo "Error: --IP requires a value"
                exit 1
            fi
            ;;
        *)
            echo "Unknown argument: $1"
            shift
            ;;
    esac
done

# Print out all collected DNS entries
echo "Provided DNS entries:"
for dns in "${dns_entries[@]}"; do
    echo "- $dns"
done

# Print out all collected IP entries
echo "Provided IP entries:"
for ip in "${ip_entries[@]}"; do
    echo "- $ip"
done
