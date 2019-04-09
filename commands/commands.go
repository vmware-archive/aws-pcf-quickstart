package commands

import (
	"log"

	kingpin "gopkg.in/alecthomas/kingpin.v2"
)

type register interface {
	register(app *kingpin.Application)
}

// Configure sets up the kingpin commands for the omg-cli.
func Configure(logger *log.Logger, app *kingpin.Application) {
	cmds := []register{
		&BuildCommand{logger: logger},
	}

	for _, c := range cmds {
		c.register(app)
	}
}
