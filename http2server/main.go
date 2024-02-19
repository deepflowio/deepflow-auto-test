package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"flag"
)
var (
	lport = flag.String("p", "8080" ,"server Listening port") 
)
func main() {
	flag.Parse()
	server := &http.Server{
		Addr:    ":" + *lport,
		Handler: h2c.NewHandler(http.HandlerFunc(handler), &http2.Server{}),
	}

	log.Fatal(server.ListenAndServe())
}

func handler(w http.ResponseWriter, r *http.Request) {
	time.Sleep(1 * time.Millisecond)
	fmt.Fprint(w, "Hello,Im HTTP/2 Server!")
}
