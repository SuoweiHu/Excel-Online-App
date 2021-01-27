# ids=`ps -ef|grep python|grep yf|grep main.py awk '{print $2}'`            # 22.32.170.169
# ids=`ps -ef|grep python3|grep Excel-Online-App/main.py|awk '{print $2}'`  # 10.0.0.98
ids=`ps -ef | grep main.py | grep -v grep |awk '{print $2}'`    # local


if [[ "${ids}" = "" ]]
then 
    echo "[ Flask service already stopped ! ]"
else 
    echo "[ Killing flask service at 5000 ... ]"
    kill -9 ${ids}
fi 
