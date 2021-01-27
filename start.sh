# ids=`ps -ef|grep python|grep yf|grep main.py awk '{print $2}'`            # 22.32.170.169
# ids=`ps -ef|grep python3|grep Excel-Online-App/main.py|awk '{print $2}'`  # 10.0.0.98
ids=`ps -ef | grep main.py | grep -v grep | awk '{print $2}'`               # local

if [[ "${ids}" != "" ]]
then 
    echo "[ Flask service already running at 5000 ]"
else 
    echo "[ Starting flask service at 50000 ... ]"
    # nohup python /root/yf/Excel-Online-App/main.py & 2>1&
    nohup python3 /Users/suoweihu/Documents/GitHub/Excel-Online-App/main.py
    # nohup python3 ~/Excel-Online-App/main.py
fi 
