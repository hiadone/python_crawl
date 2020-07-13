#!/bin/bash
#
#
export PYTHON_EXE=/usr/bin/python3
#
export DISPLAY=:10
export PYTHONPATH=$PYTHONPATH:/root/HIADONE/bin:/root/HIADONE/lib:.


$PYTHON_EXE ./wisa/howlpot.py
$PYTHON_EXE ./wisa/smallstuff.py







