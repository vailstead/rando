#!/bin/bash

##
# bash_starter.sh - A simple start script that supports short & long CLI options
#   and supports color coded log messages to std out.
#
# Utility Functions:
#   usage()         - prints usage
#   log_stdout()    - logs error message to STDOUT
#   log_err()       - wrapper function calling log_stdout with "err" and $1 (message)
#   log_warn()      - wrapper function calling log_stdout with "warn" and $1 (message)
#   log_info()      - wrapper function calling log_stdout with "info" and $1 (message)
#   log_success()   - wrapper function calling log_stdout with "success" and $1 (message)
#   log_debug()     - wrapper function calling log_stdout with "debug" and $1 (message). Debug flag must be set
#   log_trace()     - wrapper function calling log_stdout with "trace" and $1 (line number) $2 (message). Debug flag must be set
#   
#
# Script Functions:
#  sample_func() - Sample function, replace with your function
#
# DON'T FORGET TO SHELLCHECK! https://github.com/koalaman/shellcheck?tab=readme-ov-file#installing
##

##
# Logging
##
COLOR_ERROR="\033[1;31;47m"
COLOR_WARNING='\033[1;31m'
COLOR_SUCCESS='\033[0;32m'
COLOR_INFO='\033[0;34m'
COLOR_DEBUG='\033[0;33m'
COLOR_TRACE='\033[0;30m'
NC='\033[0m'

log_stdout () {
    case $1 in
        "err")
            echo -e "${COLOR_ERROR}[ERROR]${NC} ${2}";
            exit 1;
        ;; 
        "warn")
            echo -e "${COLOR_WARNING}[WARNING]${NC} ${2}";
        ;;
        "info")
             echo -e "${COLOR_INFO}[INFO]${NC} ${2}";
        ;;
        "success")
             echo -e "${COLOR_SUCCESS}[SUCCESS]${NC} ${2}";
        ;;
        "debug")
             if [ "$DEBUG" ]; then
                echo -e "${COLOR_DEBUG}[DEBUG]${NC} ${2}";
             fi
        ;;
        "trace")
             if [ "$TRACE" ]; then
                echo -e "${COLOR_TRACE}[TRACE] Line $2 ${NC} ${3}";
             fi
        ;;
    esac
}
log_err() { log_stdout  "err" "$1"; }
log_warn() { log_stdout  "warn" "$1"; }
log_success() { log_stdout  "success" "$1"; }
log_info() { log_stdout  "info" "$1"; }
log_debug() { log_stdout  "debug" "$1"; }
log_trace() { log_stdout  "trace" "$1" "$2"; }


# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Display this help message"
    echo "  -s, --short <arg>   Example short option with argument"
    echo "  -l, --long          Example long option"
    echo "  -d, --debug         Toggle debug mode"
    echo ""
    exit 1
}

# Default values for the options
short_option=""
long_option=false

# Use `getopt` to handle short (-s) and long (--short) options
if ! OPTIONS=$(getopt -o hs:ldt -l help,short:,long,debug,trace -- "$@")
then
    log_err "Error in getopt parsing. Check usage with '$0 --help'"
fi 

# Apply the parsed options
eval set -- "$OPTIONS"

# Process the options using a while loop
while true; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -s|--short)
            short_option="$2"
            shift 2
            ;;
        -l|--long)
            long_option=true
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        -t|--trace)
            TRACE=true
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
done

# Function sample_function
# Description: 
#   A description about the function
# Arguments:
#   $1 - type:any Random argument
#   $2 - type:any Random argument - 
# Output:
#   Kubectl command to be ran in cluster to register
sample_func(){
    log_trace $LINENO "in create_cluster() function"
    if [ "$TRACE" ]; then
        arg_idx=1
        for arg in "$@"; do
        log_trace $LINENO "Argument \$${arg_idx}: ${arg}"
        arg_idx=$((arg_idx+1))
    done
    fi
    if [ "$DEBUG" ]; then
        log_debug "Operating System: $(uname -o)"
        log_debug "Kernel: $(uname -srv)"
    fi
}

sample_func 1 2
# Display parsed options
echo "Short option value: $short_option"
echo "Long option is set: $long_option"
echo "Printing examples of log messages, modify log functions/colors as you see fit"
log_warn "Warning log message"
log_success "Success log message"
log_info "Info log message"
log_debug "Debug log message, -d,--debug option must be set"
log_trace "Trace log message, -t,--trace option must be set"
log_err "Error log message, will exit with non-zero exit code"
