#!/bin/bash
#
#
#
#
export PYTHON_EXE=/usr/bin/python3
#
export DISPLAY=:10
export PYTHONPATH=$PYTHONPATH:/root/HIADONE/bin:/root/HIADONE/lib:.

# 기존 다운로드된 이미지 삭제
find /root/HIADONE/images -follow -type f -atime +2 -name "*" -exec rm -f {} \;
sleep 30
#
#

naver_check=`ps -ef|grep -v "grep" | grep "start.naver.sh" | wc -l`
cafe_check=`ps -ef|grep -v "grep" | grep "start.cafe24.sh" | wc -l`
godo_check=`ps -ef|grep -v "grep" | grep "start.godomall.sh" | wc -l`
imweb_check=`ps -ef|grep -v "grep" | grep "start.imweb.sh" | wc -l`
makeshop_check=`ps -ef|grep -v "grep" | grep "start.makeshop.sh" | wc -l`
private_check=`ps -ef|grep -v "grep" | grep "start.private.sh" | wc -l`
wisa_check=`ps -ef|grep -v "grep" | grep "start.wisa.sh" | wc -l`
sixshop_check=`ps -ef|grep -v "grep" | grep "start.sixshop.sh" | wc -l`


if [ "$naver_check" == "0" ]; then
	if [ "$cafe_check" == "0" ]; then
		if [ "$godo_check" == "0" ]; then	
			if [ "$imweb_check" == "0" ]; then	
				if [ "$makeshop_check" == "0" ]; then	
					if [ "$private_check" == "0" ]; then	
						if [ "$wisa_check" == "0" ]; then	
							if [ "$sixshop_check" == "0" ]; then
								./start.naver.sh
								./start.cafe24.sh
								./start.godomall.sh
								./start.imweb.sh
								./start.makeshop.sh
								./start.private.sh
								./start.wisa.sh
								./start.sixshop.sh
							fi
						fi
					fi
				fi
			fi
		fi
	fi
fi









