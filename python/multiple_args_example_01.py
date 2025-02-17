import sys

# Usage: python3 parse_args.py --DNS 8.8.8.8 --DNS 1.1.1.1 --IP 192.168.1.1 --IP 10.0.0.1

def parse_arguments():
    dns_entries = []
    ip_entries = []
    
    args = sys.argv[1:]  # Exclude script name
    i = 0
    
    while i < len(args):
        if args[i] == "--DNS":
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                dns_entries.append(args[i + 1])
                i += 2  # Move past argument and value
            else:
                print("Error: --DNS requires a value")
                sys.exit(1)
        elif args[i] == "--IP":
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                ip_entries.append(args[i + 1])
                i += 2
            else:
                print("Error: --IP requires a value")
                sys.exit(1)
        else:
            print(f"Unknown argument: {args[i]}")
            i += 1  # Move to the next argument

    return dns_entries, ip_entries

# Run the argument parser
dns_entries, ip_entries = parse_arguments()

# Print results
print("Provided DNS entries:")
for dns in dns_entries:
    print(f"- {dns}")

print("Provided IP entries:")
for ip in ip_entries:
    print(f"- {ip}")
