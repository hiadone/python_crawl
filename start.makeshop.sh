#!/bin/bash
#
#
export PYTHON_EXE=/usr/bin/python3
#
export DISPLAY=:10
export PYTHONPATH=$PYTHONPATH:/root/HIADONE/bin:/root/HIADONE/lib:.




$PYTHON_EXE ./makeshop/affetto.py

VAL=$(date +"%H")

if [ ${VAL} -ge 10 ] ; then
    $PYTHON_EXE ./makeshop/amylovespet.py
fi

$PYTHON_EXE ./makeshop/cocochien.py
$PYTHON_EXE ./makeshop/dermadog.py
$PYTHON_EXE ./makeshop/ecofoam.py
$PYTHON_EXE ./makeshop/hydewolf.py
$PYTHON_EXE ./makeshop/itsdog.py
$PYTHON_EXE ./makeshop/oraeorae.py
$PYTHON_EXE ./makeshop/petnoriter.py
$PYTHON_EXE ./makeshop/puppygallery.py








