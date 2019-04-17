package commands

import (
	"context"
	"log"
	"time"

	"github.com/cf-platform-eng/aws-pcf-quickstart/aws"
	"github.com/cf-platform-eng/aws-pcf-quickstart/config"
	"github.com/starkandwayne/om-tiler/mover"
	"github.com/starkandwayne/om-tiler/opsman"
	"github.com/starkandwayne/om-tiler/pivnet"
	"github.com/starkandwayne/om-tiler/tiler"

	kingpin "gopkg.in/alecthomas/kingpin.v2"
)

type DaemonCommand struct {
	logger       *log.Logger
	metadataFile string
	cacheDir     string
}

const (
	daemonName    = "daemon"
	checkInterval = 30 * time.Second
)

func (cmd *DaemonCommand) register(app *kingpin.Application) {
	c := app.Command(daemonName, "Run Daemon to listen for delete on sqs message bus").Action(cmd.run)
	c.Flag("metadata-file", "Path to config file").Default(config.MetadataFile).StringVar(&cmd.metadataFile)
	c.Flag("cache-dir", "Directory to place the cached tiles)").Default(config.CacheDir).StringVar(&cmd.cacheDir)
}

func (cmd *DaemonCommand) run(c *kingpin.ParseContext) error {
	cfg, err := config.LoadConfig(cmd.metadataFile, cmd.logger)
	if err != nil {
		return err
	}
	mover, err := mover.NewMover(
		pivnet.NewClient(cfg.Pivnet, cmd.logger),
		cmd.cacheDir,
		cmd.logger,
	)
	if err != nil {
		return err
	}
	om, err := opsman.NewClient(cfg.Opsman, cmd.logger)
	if err != nil {
		return err
	}

	t := tiler.NewTiler(om, mover, cmd.logger)

	ac, err := aws.NewClient(cfg.Aws, cmd.logger)
	if err != nil {
		return err
	}
	ctx := context.Background()
	crarg := aws.CustomResourceArg{
		Status:            aws.CRSuccess,
		RequestType:       aws.CRDelete,
		LogicalResourceID: cfg.MyCustomBOSH.LogicalResourceID,
		QueueURL:          cfg.MyCustomBOSH.SQSQueueURL,
	}
	for {
		requests, err := ac.CustomResourceRequests(ctx, crarg)
		if err != nil {
			return err
		}
		if len(*requests) > 0 {
			err := t.Delete(ctx)
			if err != nil {
				crarg.Status = aws.CRFailed
				crarg.Reason = err.Error()
				ac.UpdateCustomResource(ctx, crarg)
				return err
			}
			ac.UpdateCustomResource(ctx, crarg)
		} else {
			time.Sleep(checkInterval)
		}
	}
}
