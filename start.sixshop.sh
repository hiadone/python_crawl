#!/bin/bash
#
#
export PYTHON_EXE=/usr/bin/python3
#
echo "DISPLAY CHCEK"
xvfb_check=`ps -ef|grep -v "grep" | grep "Xvfb" | wc -l`

if [ "$xvfb_check" == "0" ]; then
        echo "Xvfb Process Down and Start"
        /usr/bin/Xvfb :10 -ac &
        echo "DISPLAY NUMBER : 10"
else
        echo "Xvfb Process Alive"
fi

#
export DISPLAY=:10
export PYTHONPATH=$PYTHONPATH:/root/HIADONE/bin:/root/HIADONE/lib:.


$PYTHON_EXE ./sixshop/bonjourtou_tou.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/comercotte.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/ddoang.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/guilty_pleasure.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/harryspet.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/melonicoco.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/pawunion.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/pethod.py > ../LOG/SixShop.log 2>&1
$PYTHON_EXE ./sixshop/wilddog.py > ../LOG/SixShop.log 2>&1







