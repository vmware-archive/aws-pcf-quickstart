package main

import (
	"log"
	"os"

	"github.com/cf-platform-eng/aws-pcf-quickstart/commands"

	kingpin "gopkg.in/alecthomas/kingpin.v2"
)

func main() {
	logger := log.New(os.Stdout, "", 0)

	app := kingpin.New("quickstart", "Ops Manager (on) AWS")
	commands.Configure(logger, app)
	kingpin.MustParse(app.Parse(os.Args[1:]))
}
