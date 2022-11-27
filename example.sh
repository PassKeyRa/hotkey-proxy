#!/bin/bash

PROGRAM=obsidian
CMD='echo lol >> /tmp/log.txt'
MODIFIER=ctrl
KEY=S

# create log file
touch /tmp/log.txt

# run the program with custom hotkey
python3 hotkey-proxy.py -m $MODIFIER -k $KEY -c "$CMD" $PROGRAM

# check log
cat /tmp/log.txt

rm /tmp/log.txt
