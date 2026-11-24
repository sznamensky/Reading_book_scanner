#!/bin/bash
# Script TalkingScanner_v4_1.sh RELEASE created by Sergey Znamenskiy 20/11/2026 add /etc/TalkingScanner/tscnr.cfg, add /etc/TalkingScanner/tscnr.cfg, add preproc thresh, filenames to cfg file
# supports cyrillic and english characters recognition
# speech syntethizer supports russian
# designed to work with scanner control script button_ctrl_takepic_undist_preproc_v4_1.py 
# script supports  scanner designed by P.Sudravsky
# directories for temporary files /tmp/TalkingScanner	/media/reader/SCANS/TalkingScanner/book_pages_scans	
# /media/reader/SCANS/TalkingScanner/book_pages_text
# directories for results file /var/tmp/TalkingScanner	/media/reader/SCANS/TalkingScanner/results

echo "Привет, я читающий книжный сканер, версия 4.1" |RHVoice-test -p Aleksandr

echo "Checkpoint 01 CHECK THE SIZE OF results.txt IF > 50MB CLEAR results.txt"
file_name=/var/tmp/TalkingScanner/results.txt
file_size=`stat --printf="%s" $file_name`
if [ "$file_size" -gt 50000000 ] && [[ -d "/media/reader/SCANS/TalkingScanner" ]]; then 
	cp /var/tmp/TalkingScanner/results.txt /media/reader/SCANS/TalkingScanner/results/results_old.txt
	rm /var/tmp/TalkingScanner/results.txt
	touch /var/tmp/TalkingScanner/results.txt
elif [ "$file_size" -gt 50000000 ] && ! [[ -d "/media/reader/SCANS/TalkingScanner" ]]; then
	rm /var/tmp/TalkingScanner/results.txt
	touch /var/tmp/TalkingScanner/results.txt
fi


if ! [[ -d "/tmp/TalkingScanner" ]]; then
	mkdir /tmp/TalkingScanner
fi
cd /tmp/TalkingScanner

# MAIN CYCLE BEGIN
while true
do

echo "Checkpoint 02 COPY TO USB STICK AND REMOVE THE TEMPORARY FILES" 
if [[ -d "/media/reader/SCANS/TalkingScanner" ]]; then
		cp /tmp/TalkingScanner/*.png /media/reader/SCANS/TalkingScanner/book_pages_scans
		cp /tmp/TalkingScanner/pages.txt /media/reader/SCANS/TalkingScanner/book_pages_text
fi
for var in `ls /tmp/TalkingScanner`
do
	rm /tmp/TalkingScanner/$var
done

echo "Checkpoint 03 RUN SCANNER CONTROL PYTHON SCRIPT PUT THE SCANS TO /tmp/TalkingScanner"
echo "Кладите книгу. Жмите кнопку. Я прочитаю." |RHVoice-test -p Aleksandr
# SCANNER CONTROL PYTHON SCRIPT HERE
  
python /usr/local/bin/button_ctrl_takepic_undist_preproc_v4_1.py

echo "Checkpoint 04 PERFORM OCR CHECK IF SCANS ARE TURNED 180"
turned=false	# VARIABLE IF TRUE BOOK IS TURNED 180, NEEDS SWAP PAGES
for var in `ls /tmp/TalkingScanner |grep page`
do
angle=`tesseract $var stdout --psm 0 |grep Orientation |awk '{print $4}'`
if [[ $angle == 180 ]]; then
turned=true
echo "Page turned 180" 
fi
done

echo "Checkpoint 05 PERFORM OCR FOR THE SCANS LOADED APPEND OCR RESULTS TO pages.txt" 
if [[ $turned == false ]]; then	# DIRECT PAGES ORDER IN OUTPUT FILE pages.txt
for var in `ls /tmp/TalkingScanner |grep page`
do
tesseract /tmp/TalkingScanner/$var /tmp/TalkingScanner/out -l rus+eng --psm 3
cat   /tmp/TalkingScanner/out.txt >>/tmp/TalkingScanner/pages.txt
rm /tmp/TalkingScanner/out.txt
done
else		# SWAPPED PAGES ORDER IN OUTPUT FILE pages.txt
tesseract /tmp/TalkingScanner/page_2.png /tmp/TalkingScanner/out -l rus+eng --psm 1
cat   /tmp/TalkingScanner/out.txt >>/tmp/TalkingScanner/pages.txt
rm /tmp/TalkingScanner/out.txt
tesseract /tmp/TalkingScanner/page_1.png /tmp/TalkingScanner/out -l rus+eng --psm 1
cat   /tmp/TalkingScanner/out.txt >>/tmp/TalkingScanner/pages.txt
rm /tmp/TalkingScanner/out.txt
fi

echo "Checkpoint 06 READ pages.txt"
echo "Читаю"|RHVoice-test -p Aleksandr
sleep 1
RHVoice-test -i /tmp/TalkingScanner/pages.txt -p Elena
sleep 1
echo "Завершено"|RHVoice-test -p Aleksandr
sleep 1

echo "Checkpoint 07  APPEND THE pages.txt CONTENT TO results.txt AND COPY TO USB STICK"
cat   /tmp/TalkingScanner/pages.txt >>/var/tmp/TalkingScanner/results.txt
if [[ -d "/media/reader/SCANS/TalkingScanner" ]]; then
	cp /var/tmp/TalkingScanner/results.txt /media/reader/SCANS/TalkingScanner/results/results.txt
fi

done
# MAIN CYCLE END
