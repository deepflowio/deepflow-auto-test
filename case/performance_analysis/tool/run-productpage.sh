logfile=$1
rate=$2

echo "productpage-rate:$rate"
echo -e "productpage\n$rate" >> $logfile
wrk2 -c50 -t4 -R$rate -d60 -L http://10.96.3.18:9080/productpage | grep -E "(Latency Distribution|Requests/sec)" -A 8 | grep -E "^( 50.000| 90.000|Requests/sec:)"| awk '{printf "%s\n", $2;}' >> $logfile  &
sleep 70
python3 ~/df-test/read_stat.py productpage >> $logfile
python3 ~/df-test/read_stat.py wrk2 >> $logfile
python3 ~/df-test/read_stat.py details >> $logfile
python3 ~/df-test/read_stat.py ws-javaagent.jar >> $logfile
python3 ~/df-test/read_stat.py ratings >> $logfile
python3 ~/df-test/read_stat.py envoy >> $logfile