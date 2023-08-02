logfile=$1
rate=$2

echo "go-server-rate:$rate"
echo -e "go-server-sampl\n$rate" >> $logfile
wrk2 -c1 -t1 -R$rate -d60 -L http://127.0.0.1:8080/?num=10000 | grep -E "(Latency Distribution|Requests/sec)" -A 8 | grep -E "^( 50.000| 90.000|Requests/sec:)"| awk '{printf "%s\n", $2;}' >> $logfile  &
sleep 70
python3 ~/df-test/read_stat.py go-server-sampl >> $logfile
python3 ~/df-test/read_stat.py wrk2 >> $logfile
python3 ~/df-test/read_stat.py mysqld >> $logfile