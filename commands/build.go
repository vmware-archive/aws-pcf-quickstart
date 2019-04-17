package commands

import (
	"context"
	"log"

	"github.com/cf-platform-eng/aws-pcf-quickstart/aws"
	"github.com/cf-platform-eng/aws-pcf-quickstart/config"
	"github.com/cf-platform-eng/aws-pcf-quickstart/templates"
	"github.com/starkandwayne/om-tiler/mover"
	"github.com/starkandwayne/om-tiler/opsman"
	"github.com/starkandwayne/om-tiler/pivnet"
	"github.com/starkandwayne/om-tiler/steps"
	"github.com/starkandwayne/om-tiler/tiler"

	kingpin "gopkg.in/alecthomas/kingpin.v2"
)

type BuildCommand struct {
	logger           *log.Logger
	metadataFile     string
	cacheDir         string
	varsStore        string
	skipApplyChanges bool
}

const buildName = "build"

func (cmd *BuildCommand) register(app *kingpin.Application) {
	c := app.Command(buildName, "Deploy PCF and Service Broker using OpsManager").Action(cmd.run)
	c.Flag("metadata-file", "Path to config file").Default(config.MetadataFile).StringVar(&cmd.metadataFile)
	c.Flag("cache-dir", "Directory to place the cached tiles)").Default(config.CacheDir).StringVar(&cmd.cacheDir)
	c.Flag("vars-store", "Path to a file for storing generated secrets e.g creds.yml").Default(config.VarsStore).StringVar(&cmd.varsStore)
	c.Flag("skip-apply-changes", "Only upload and configure tiles").BoolVar(&cmd.skipApplyChanges)
}

func (cmd *BuildCommand) run(c *kingpin.ParseContext) error {
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
	t.RegisterStep(tiler.BuildCallback, steps.Step{
		Name:      "UpdateCustomResource",
		DependsOn: []string{tiler.StepDeployDirector},
		Do: func(ctx context.Context) error {
			return ac.UpdateCustomResource(ctx, aws.CustomResourceArg{
				Status:            aws.CRSuccess,
				RequestType:       aws.CRCreate,
				LogicalResourceID: cfg.MyCustomBOSH.LogicalResourceID,
				QueueURL:          cfg.MyCustomBOSH.SQSQueueURL,
			})
		},
	})

	pattern, err := templates.GetPattern(cfg.Raw, cmd.varsStore, true)
	if err != nil {
		return err
	}
	ctx := context.Background()
	err = t.Build(ctx, pattern, cmd.skipApplyChanges)
	if err != nil {
		ac.UpdateWaitHandle(ctx, aws.UpdateWaitHandleInput{
			Status:    aws.WHFailure,
			Reason:    err.Error(),
			HandleURL: cfg.PcfWaitHandle,
		})
		return err
	}

	return ac.UpdateWaitHandle(ctx, aws.UpdateWaitHandleInput{
		Status:    aws.WHSuccess,
		Reason:    "Successfully deployed Elastic Runtime",
		HandleURL: cfg.PcfWaitHandle,
	})
}
