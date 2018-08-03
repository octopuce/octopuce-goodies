#!/bin/bash
# auto-reload ARG[2] supervisor program  when the ARG[1] path changes
# Uses a callback system to avoid multiple executions
# Licensed under Public Domain
# 
# Mandatory for debian: apt-get install inotify-tools
# 
# @author Alban Crommer


############################
# PARAMS 
############################
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.dotnet/tools"
# Defines a delay for the callback command
sleep_time=2


############################
# USAGE  
############################

usage() {
    msg="
    Rerun a supervisor command every time filesystem changes are detected.
    
    Usage: $(basename $0) [-h|--help] path supervisor_program
    
      -h, --help          Display this help and exit.
      path                The program installation path ex: /opt/myapp
      supervisor_program  The program name as declared in supervisor ex: myapp
    "
    echo "$msg"
}

while [ $# -gt 0 ]; do
    case "$1" in
      -h|--help) usage; exit;;
      *) break;;
    esac
    shift
done


############################
# FUNCTIONS / HELPERS 
############################

# Function : timestamped log
log(){ echo "`date -R ` $1"; }
# Function : timestamp log + exit
err(){ log "$@"; exit 1; }
# Function : A callback executor with time based execution skip process based on event id
# ARG[1] : The callback id
# ARG[2] : The callback command
# Executes the command unless another event preempted execution during the sleep 
callback(){
    # Read from args
    local my_event_id="$1"
    local callback="$2"
    # Sleep
    sleep "$sleep_time"; 
    # Read from file
    local last_event_id=$( cat $tmp_file)
    # Check for preemption
    if [[ "$my_event_id" != "$last_event_id" ]] ; then 
        log "Callback $my_event_id Skipped: another event preempts me: '$last_event_id' " 
    else 
        log "Callback $my_event_id executes: '$callback'"
        $callback
    fi  
}


############################
# Args parsing 
############################

# ARG[1] : app path
[ -z "$1" ] && err "You MUST provide a path as argument"
watch_path="$1"
[[ ! -e "$watch_path" ]] && err "The request path is not valid : $watch_path"
shift

# ARG[2] : app name in supervisor
[ -z "$1" ] && err "You MUST provide a program as argument"
program="$1"
supervisorctl avail | grep -q "^$program" || err "The requested program is not valid : $program"

# Final tmp file based on program name
tmp_file="/tmp/.mark.supervisor-$program"

############################
# Business logic starts here
############################

log "Started with path $watch_path for program $program"

# Wait events forever 
	    
while true; do 

    # Receive event 
    event_string=$(inotifywait --quiet --recursive --event create,delete,delete_self,modify,move  --exclude 'logs' "$watch_path" )
    log "Received event_id : $event_string"

    # Set event ID and store it
    event_id=$(date "+%Y-%m-%d_%H:%M:%S@%N");
    echo "$event_id" > $tmp_file

    # Launch the callback and wait for a new event
    callback "$event_id" "supervisorctl restart $program" &

done


# EOF
