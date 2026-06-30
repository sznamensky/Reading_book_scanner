#!/bin/bash
# script created by Sergei Znamensky 25012026 to shutdown raspberry pi os
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
echo "выключаюсь, подождите несколько секунд" | RHVoice-test -p Aleksandr
shutdown -h now
