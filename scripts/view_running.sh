#!/bin/bash

# get details for the currently running server proccess
# usefull for finding the PIDs to kill them individually

ps -e -o user -o pid -o stime -o cmd | grep SCREEN
