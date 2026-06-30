#!/bin/bash
# script stop_TS_processes_v1_2.sh created by Sergei Znamensky 17012026 to stop Talking Scanner processes any version
for var in `ps -ef |grep TalkingScanner |grep /bin/bash | awk '{print $2}'`
do
kill $var
done
wait 
for var in `ps -ef |grep python |grep button | awk '{print $2}'`
do
kill $var
done
wait
for var in `ps -ef |grep RHVoice |grep TalkingScanner | awk '{print $2}'`
do
kill $var
done
sleep 1
echo 'процессы читающего сканера остановлены' |RHVoice-test -p Aleksandr
# comment: second grep filters unnesessary lines in ps output, awk filters position in line  

