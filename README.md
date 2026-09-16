# Reading_book_scanner
This is the place for the code for my project of the book scanner capable to perform OCR of the scanned book pages and then read the text of the scanned book pages.
 
The project name is: CHIKS (ЧИКС = Читающий Книжный Сканер)
With its first release CHIKS supports reading paper books in Russian only.
With future releases supported languages list will be extended. 
Hardware: Raspberry PI 5 based.
Software installed:
1. operating system	Debian GNU/Linux 12 (bookworm)
kernel			Linux 6.12.25+rpt-rpi-2712
architecture		arm64	
2. OCR	tesseract v.5.3.0
3. TTS	RHVoice
4. CHIKS original software:	TalkingScanner_raspy5_v3_47_imx219.sh
5. CHIKS original software:	button_ctrl_takepic_undist_preproc_raspy5_v3_47_imx219.py
6. CHIKS original software:	TS_processes_status_v1_1.sh
7. CHIKS original software:	stop_TS_processes_v1_2.sh
8. CHIKS original software:	shutdown_pi.sh

## How to install/remove or upgrade App

### Installation

```shell
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install python3.10 -y
pip install -r requirement.txt
```

### Uninstall

```shell
cd 
rm -fR ~/Reading_book_scaner
```



# Заметки

## По оформлению.

1. В целом не хватает общего описания программного обеспечения. Обычно это пишут в Description. Для чего данное программное обеспечение. Какие задачи решает.
   - Версия языка.
   - Важные библиотеки на которых строится продукт (OpenCV, RVoice).
1. Не хватает описания того как ПО устанавливается (вместе с зависимостями) от начала и до  конца (как будто на чистую ОС). Тот же вопрос по удалению ПО. Если это GitHub то обычно делают еще CI на Actions для тестирования хотя бы базового функционала.
2. Не обнаружил юнит тестов, правилами хорошего тона принято.
3. Слабоватая документация. Нет навигации и структуры.
4. requirement.txt <- не собраны версии пакетов для работы ПО с проставленными версиями.  Если бы оно было, можно было бы пачкой ставить все батарейки питона.
   ```shell
	pip install -r requirement.txt
   ```
   
5. GitIgnore must have

## По качеству кода.

- Не используемые куски кода. 
- Не используемые импорты.
- Я сторонник NOCOMMENTS поэтому любые комментарии в коде считаю не красивым (дело вкуса), но коментарии как этот явно только отвлекают:
  ```python
  # function initialize camera  
	def initialize_camera(camera):
  ```
  
- У аргументов функций не проставлены типы. Сейчас принято ставить хоть это и питон, а принято писать как на языке со статической типизацией.
- Видно print <- так давно никто ничего не логирует. Требуется взять полноценную библиотеку и реализовать полноценное логирование с разграничением уровней логирования.
- Не обнаружил структуры в коде. Все поделено между функциями и глобальными переменными, хотя для выразительности можно было бы использовать классы. Ну например выделить класс который отслеживает нажатие кнопок от пользователя и в другой класс собрать логику сканирования и скана. Распознавание текста в отдельный класс.  Не утверждаю что именно так надо делить, но в одном файле писать логику плохая практика. Чревато багами, например спагетти код.
- Shell скриптовую логику логично было бы также унести в питон для единообразия и управляемости