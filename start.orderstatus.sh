#!/bin/bash
#
#
export PYTHON_EXE=/usr/bin/python3
#export ORDER_HOME=/home/crawling/HIADONE
export ORDER_HOME=/root/HIADONE
export PYTHONPATH=$PYTHONPATH:/root/HIADONE/bin:/root/HIADONE/lib:.
#
#
cd ${ORDER_HOME}/bin && ${PYTHON_EXE} ./order/order_parsing.py __ORDER_STATUS__ ${1}

