open terminal: Ctrl+Alt+T
cd to folder that has the permission file: "EduGorilla.pem" 
example: cd Docouments/EduGorilla
connect to remote server using command : ssh -i "EduGorilla.pem" eduser@130.211.252.45


change directory to Edu_1/Edu_2/Edu_3/Edu_4 on all for servers respectively using command:
cd sourav/Edu_1


type command : ps -ef
search for python main.py on the right side and get it's PID(4-5 digit number) on the extreme left column
type command: kill num(the 4-5 digit PID number)



type command : ls -l data/output | wc -l
you will get a number.note it down.


type command: nano main.py
goto line 19 you ll find something like if c > 160(some number):
replace that number with the number that I asked you to note down.
Ctrl+X
tpye: 'Y' and press ''Enter' to save


type command: rm data/crawler.sqlite | rm logs/* | rm nohup.out


type command: nohup python main.py &  (DON'T FORGET THE '&' AT THE END)
close terminal without pressing "enter" or any other key.

