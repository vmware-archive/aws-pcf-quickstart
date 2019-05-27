package database

import (
	"database/sql"
	"fmt"

	_ "github.com/go-sql-driver/mysql"
)

type Client struct {
	Username string
	Password string
	Address  string
	Port     string
}

var dbNames = []string{
	"uaa",
	"ccdb",
	"notifications",
	"autoscale",
	"app_usage_service",
	"routing",
	"diego",
	"account",
	"nfsvolume",
	"networkpolicyserver",
	"silk",
	"locket",
	"credhub",
}

func (c *Client) CreateDatabases() error {

	db, err := sql.Open("mysql",
		fmt.Sprintf("%s:%s@tcp(%s:%s)/", c.Username, c.Password, c.Address, c.Port),
	)
	if err != nil {
		return fmt.Errorf("could not connect to database: %v", err)
	}

	defer db.Close()

	for _, name := range dbNames {
		_, err = db.Exec("CREATE DATABASE IF NOT EXISTS " + name)
		if err != nil {
			return fmt.Errorf("could not create database %s: %v", name, err)
		}
	}

	return nil
}
