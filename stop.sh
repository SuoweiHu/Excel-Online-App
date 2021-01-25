# ids=`ps -ef|grep python|grep yf|grep main.py awk '{print $2}'`
ids=`ps -ef|grep Excel-Online-App/main.py`

if [[ "${ids}" = "" ]]
then 
    echo "[ Flask service already stopped ! ]"
else 
    echo "[ Killing flask service at 5000 ... ]"
    kill -9 ${ids}
fi 
