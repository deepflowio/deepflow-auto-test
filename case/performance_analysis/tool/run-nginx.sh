logfile=$1
rate=$2

# run wrk2
echo "nginx-rate:$rate"
echo -e "nginx\n$rate" >> $logfile
wrk2 -c20 -t20 -R$rate -d60 -L http://nginx_ip:80/index.html | grep -E "(Latency Distribution|Requests/sec)" -A 8 | grep -E "^( 50.000| 90.000|Requests/sec:)"| awk '{printf "%s\n", $2;}' >> $logfile  &
sleep 70
python3 ~/df-test/read_stat.py nginx >> $logfile
python3 ~/df-test/read_stat.py wrk2 >> $logfile