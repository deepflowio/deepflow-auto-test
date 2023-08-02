logfile=$1
rate=$2

echo "go-chi-rate:$rate"
echo -e "authApp\n$rate" >> $logfile
wrk2 -c1 -t1 -R$rate -d60 -L http://127.0.0.1:8081/authenticate -s auth.lua| grep -E "(Latency Distribution|Requests/sec)" -A 8 | grep -E "^( 50.000| 90.000|Requests/sec:)"| awk '{printf "%s\n", $2;}' >> $logfile  &
sleep 70
python3 ~/df-test/read_stat.py authApp >> $logfile
python3 ~/df-test/read_stat.py wrk2 >> $logfile
python3 ~/df-test/read_stat.py postgres >> $logfile