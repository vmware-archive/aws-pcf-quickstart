package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/cf-platform-eng/aws-pcf-quickstart/aws"
	"github.com/cf-platform-eng/aws-pcf-quickstart/database"
	"github.com/starkandwayne/om-tiler/opsman"
	"github.com/starkandwayne/om-tiler/pivnet"
)

// Config contains the infrastructure details.
type Config struct {
	Raw               map[string]interface{}
	Opsman            opsman.Config
	Pivnet            pivnet.Config
	Aws               aws.Config
	Database          *database.Client
	MyCustomBOSH      CustomResource
	PcfWaitHandle     string
	PcfDeploymentSize string
}

type MetaData struct {
	StackName string `json:"StackName"`
	StackID   string `json:"StackId"`
	Region    string `json:"Region"`
}

type RawConfig struct {
	Domain                       string `json:"Domain"`
	PivnetToken                  string `json:"PivnetToken"`
	OpsmanPassword               string `json:"PcfOpsManagerAdminPassword"`
	SkipSSLValidation            string `json:"SkipSSLValidation"`
	PcfCustomResourceSQSQueueURL string `json:"PcfCustomResourceSQSQueueUrl"`
	PcfWaitHandle                string `json:"PcfWaitHandle"`
	PcfRdsAddress                string `json:"PcfRdsAddress"`
	PcfRdsPort                   string `json:"PcfRdsPort"`
	PcfRdsUsername               string `json:"PcfRdsUsername"`
	PcfRdsPassword               string `json:"PcfRdsPassword"`
	PcfDeploymentSize            string `json:"PcfDeploymentSize"`
}

type CustomResource struct {
	LogicalResourceID string
	SQSQueueURL       string
}

// Filenames for configs.
const (
	CacheDir     = "/home/ubuntu/cache"
	VarsStore    = "/home/ubuntu/creds.yml"
	MetadataFile = "/var/local/cloudformation/stack-meta.json"
)

func LoadConfig(metadataFile string, logger *log.Logger) (*Config, error) {
	if metadataFile == "" {
		metadataFile = MetadataFile
	}
	mr, err := ioutil.ReadFile(metadataFile)
	if err != nil {
		return nil, err
	}
	var md MetaData
	err = json.Unmarshal(mr, &md)
	if err != nil {
		return nil, err
	}
	raw := make(map[string]interface{})
	err = json.Unmarshal(mr, &raw)
	if err != nil {
		return nil, err
	}

	awsConfig := aws.Config{
		StackID:   md.StackID,
		StackName: md.StackName,
		Region:    md.Region,
	}

	ac, err := aws.NewClient(awsConfig, logger)
	if err != nil {
		return nil, err
	}

	parameters, err := ac.GetRawSSMParameters()
	if err != nil {
		return nil, err
	}
	for k, v := range parameters {
		raw[k] = v
	}

	inputs, err := ac.GetStackInputs()
	if err != nil {
		return nil, err
	}
	for k, v := range inputs {
		raw[k] = v
	}

	jsonRaw, err := json.Marshal(raw)
	if err != nil {
		return nil, err
	}
	var c RawConfig
	err = json.Unmarshal(jsonRaw, &c)
	if err != nil {
		return nil, err
	}

	return &Config{
		Opsman: opsman.Config{
			Target:               fmt.Sprintf("https://opsman.%s", c.Domain),
			Username:             "admin",
			Password:             c.OpsmanPassword,
			DecryptionPassphrase: c.OpsmanPassword,
			SkipSSLVerification:  c.SkipSSLValidation == "true",
		},
		Pivnet: GetPivnetConfig(c.PivnetToken),
		Aws:    awsConfig,
		Database: &database.Client{
			Address:  c.PcfRdsAddress,
			Port:     c.PcfRdsPort,
			Username: c.PcfRdsUsername,
			Password: c.PcfRdsPassword,
		},
		PcfDeploymentSize: c.PcfDeploymentSize,
		PcfWaitHandle:     c.PcfWaitHandle,
		MyCustomBOSH: CustomResource{
			LogicalResourceID: "MyCustomBOSH",
			SQSQueueURL:       c.PcfCustomResourceSQSQueueURL,
		},
		Raw: raw,
	}, nil
}

func GetPivnetConfig(token string) pivnet.Config {
	return pivnet.Config{
		Token: token,
		// UserAgent:  "PCF-Ecosystem-AWS-client",
		AcceptEULA: true,
	}
}
