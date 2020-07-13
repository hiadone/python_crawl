#!/bin/bash

xvfb_check=`ps -ef|grep -v "grep" | grep "Xvfb" | wc -l`

if [ "$xvfb_check" == "0" ]; then
	echo "Xvfb Process Down and Start"
	/usr/bin/Xvfb :10 -ac &
	echo "DISPLAY NUMBER : 10"
else
	echo "Xvfb Process Alive"
fi

