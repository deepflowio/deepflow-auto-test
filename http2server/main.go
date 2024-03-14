package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
)

var (
	lport = flag.String("p", "8080", "server Listening port")
	debug = flag.Bool("debug", false, "print info")
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
	if *debug {
		fmt.Println(r.Header)
	}
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()
	// for name, headers := range r.Header {
	// 	for _, h := range headers {
	// 		w.Header().Set(name, h)
	// 	}
	// }
	w.Write(body)
	//fmt.Fprint(w, "Hello,Im HTTP/2 Server! body length: ", len(body))
}
