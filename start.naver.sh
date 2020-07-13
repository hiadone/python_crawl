#!/bin/bash
#
#
export PYTHON_EXE=/usr/bin/python3
#
export DISPLAY=:10
export PYTHONPATH=$PYTHONPATH:/root/HIADONE/bin:/root/HIADONE/lib:.


$PYTHON_EXE ./naver/shopnaver.py
$PYTHON_EXE ./naver/smartstore.py





