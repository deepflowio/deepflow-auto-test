package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

func test(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Header().Set("Content-Type", "application/json")
	data := map[string]interface{}{
		"code": "0",
		"data": map[string]interface{}{
			"user_id":       "123456",
			"register_time": "1697361101",
		},
	}

	jsonData, err := json.Marshal(data)
	_, err = w.Write(jsonData)
	if err != nil {
		http.Error(w, "Failed to write response", http.StatusInternalServerError)
		return
	}
}

func main() {
	http.HandleFunc("/user_info", test)

	fmt.Println("Server is running on :8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Error:", err)
	}
}
