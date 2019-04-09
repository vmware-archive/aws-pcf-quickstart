package config

import (
	"encoding/json"
	"fmt"
	"io/ioutil"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudformation"
	"github.com/aws/aws-sdk-go/service/ssm"
	"github.com/starkandwayne/om-tiler/opsman"
	"github.com/starkandwayne/om-tiler/pivnet"
)

// Config contains the infrastructure details.
type Config struct {
	Raw    map[string]interface{}
	Opsman opsman.Config
	Pivnet pivnet.Config
}

type MetaData struct {
	StackName string `json:"StackName"`
	StackID   string `json:"StackId"`
	Region    string `json:"Region"`
}

type RawConfig struct {
	Domain            string `json:"Domain"`
	PivnetToken       string `json:"PivnetToken"`
	OpsmanPassword    string `json:"PcfOpsManagerAdminPassword"`
	SkipSSLValidation string `json:"SkipSSLValidation"`
}

// Filenames for configs.
const (
	CacheDir     = "/home/ubuntu/cache"
	VarsStore    = "/home/ubuntu/creds.yml"
	MetadataFile = "/var/local/cloudformation/stack-meta.json"
)

func LoadConfig(metadataFile string) (*Config, error) {
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

	parameters, err := getRawSSMParameters(md)
	if err != nil {
		return nil, err
	}
	for k, v := range parameters {
		raw[k] = v
	}

	inputs, err := getStackInputs(md)
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
		Raw:    raw,
	}, nil
}

func getStackInputs(md MetaData) (map[string]interface{}, error) {
	session, err := session.NewSession(&aws.Config{
		Region: aws.String(md.Region)},
	)
	if err != nil {
		return nil, err
	}
	service := cloudformation.New(session)
	request := cloudformation.DescribeStacksInput{StackName: &md.StackID}
	response, err := service.DescribeStacks(&request)
	if err != nil {
		return nil, err
	}
	out := make(map[string]interface{})
	for _, stack := range response.Stacks {
		for _, parameter := range stack.Parameters {
			out[*parameter.ParameterKey] = *parameter.ParameterValue
		}
	}

	return out, nil
}

func getRawSSMParameters(md MetaData) (map[string]interface{}, error) {
	withDecryption := false
	name := fmt.Sprintf("%s.SSMParameterJSON", md.StackName)

	// session, err := session.NewSession(aws.NewConfig())
	session, err := session.NewSession(&aws.Config{
		Region: aws.String(md.Region)},
	)
	if err != nil {
		return nil, err
	}

	service := ssm.New(session)
	request := ssm.GetParameterInput{Name: &name, WithDecryption: &withDecryption}
	response, err := service.GetParameter(&request)
	if err != nil {
		return nil, err
	}
	out := make(map[string]interface{})
	err = json.Unmarshal([]byte(*response.Parameter.Value), &out)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func GetPivnetConfig(token string) pivnet.Config {
	return pivnet.Config{
		Token:      token,
		UserAgent:  "PCF-Ecosystem-AWS-client",
		AcceptEULA: true,
	}
}
