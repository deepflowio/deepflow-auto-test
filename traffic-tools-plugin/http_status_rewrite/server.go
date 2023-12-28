package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

type DataItem struct {
	ID    int    `json:"ID"`
	NAME  string `json:"NAME"`
	STATE int    `json:"STATE"`
}

type ResponseData struct {
	OPT_STATUS  string     `json:"OPT_STATUS"`
	DESCRIPTION string     `json:"DESCRIPTION"`
	DATA        []DataItem `json:"DATA"`
}

func test(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	data := ResponseData{
		OPT_STATUS:  "SUCCESS",
		DESCRIPTION: "Data retrieved successfully",
		DATA: []DataItem{
			{
				ID:    1,
				NAME:  "Item 111111111111111111111111111111111111111111111111111111111111111111111111111",
				STATE: 1,
			},
			{
				ID:    2,
				NAME:  "Item 2111111111111111111111111111111111111111111111111111111111111111111111111111",
				STATE: 2,
			},
			{
				ID:    3,
				NAME:  "Item 2111111111111111111111111111111111111111111111111111111111111111111111111111",
				STATE: 2,
			},
			{
				ID:    4,
				NAME:  "Item 2111111111111111111111111111111111111111111111111111111111111111111111111111",
				STATE: 2,
			},
			{
				ID:    5,
				NAME:  "Item 2111111111111111111111111111111111111111111111111111111111111111111111111111",
				STATE: 2,
			},
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
	http.HandleFunc("/v1/vtaps/", test)

	fmt.Println("Server is running on :8080")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Println("Error:", err)
	}
}
