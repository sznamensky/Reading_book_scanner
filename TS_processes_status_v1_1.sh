#!/bin/bash
# script created by Sergei Znamensky 17012026 checks Talking Scanner processes running
var1=`ps -ef |grep TalkingScanner |grep /bin/bash | awk '{print $2}'`
var2=`ps -ef |grep python |grep button | awk '{print $2}'`
if [[ "$var1" && "$var2" ]]; then 
	echo 'процессы читающего сканера запущены' |RHVoice-test -p Aleksandr
else
	echo 'процессы читающего сканера остановлены' |RHVoice-test -p Aleksandr
fi
# comment: second grep filters unnesessary lines in ps output, awk filters position in line  

