# ps -ef|grep python|grep yf|grep main.py
ps -ef | grep main.py | grep -v grep
echo
netstat -an|grep 5000