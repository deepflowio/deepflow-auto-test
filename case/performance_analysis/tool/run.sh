logfile=$1
process=$2
agent=$3
echo "" > $logfile
nginx_rate_array=(30000 25000 20000 15000)
istio_rate_array=(350 325 300 175)
chi_rate_array=(8000 7000 6000 5000)
server_rate_array=(410 400 390 380)
for i in "${!nginx_rate_array[@]}"; do
    if [ $process == "nginx" ];then
        sh ~/df-test/run-nginx.sh $logfile ${nginx_rate_array[i]}
        if [ $agent == "with_agent" ];then
            python3 ~/df-test/read_stat.py nginx deepflow-agent >> $logfile
        else
            echo -e "0\n0" >> $logfile
        fi
        echo "" >> $logfile
    elif [ $process == "istio" ];then
        sh ~/df-test/run-productpage.sh $logfile ${istio_rate_array[i]}
        if [ $agent == "with_agent" ];then
            python3 ~/df-test/read_stat.py deepflow-agent >> $logfile
        else
            echo -e "0\n0" >> $logfile
        fi
        echo "" >> $logfile
    elif [ $process == "go-chi" ];then
        sh ~/df-test/run-go-chi.sh $logfile ${chi_rate_array[i]}
        if [ $agent == "with_agent" ];then
            python3 ~/df-test/read_stat.py deepflow-agent >> $logfile
        else
            echo -e "0\n0" >> $logfile
        fi
        echo "" >> $logfile
    elif [ $process == "go-server" ];then
        sh ~/df-test/run-go-server.sh $logfile ${server_rate_array[i]}
        if [ $agent == "with_agent" ];then
            python3 ~/df-test/read_stat.py deepflow-agent >> $logfile
        else
            echo -e "0\n0" >> $logfile
        fi
        echo "" >> $logfile
    fi
done