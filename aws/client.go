package aws

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudformation"
	"github.com/aws/aws-sdk-go/service/ec2"
	"github.com/aws/aws-sdk-go/service/ssm"
)

type Config struct {
	StackID   string
	StackName string
	Region    string
}

type Client struct {
	stackID   string
	stackName string
	region    string
	logger    *log.Logger
	session   *session.Session
}

func NewClient(c Config, logger *log.Logger) (*Client, error) {
	session, err := session.NewSession(&aws.Config{
		Region: aws.String(c.Region)},
	)
	if err != nil {
		return nil, fmt.Errorf("cloud not create aws session: %v", err)
	}
	return &Client{
		stackID:   c.StackID,
		stackName: c.StackName,
		region:    c.Region,
		logger:    logger,
		session:   session,
	}, nil
}

func (c *Client) GetStackInputs() (map[string]interface{}, error) {
	service := cloudformation.New(c.session)
	request := cloudformation.DescribeStacksInput{StackName: &c.stackID}
	response, err := service.DescribeStacks(&request)
	if err != nil {
		return nil, fmt.Errorf("cloud not get stack parameters: %v", err)
	}
	out := make(map[string]interface{})
	for _, stack := range response.Stacks {
		for _, parameter := range stack.Parameters {
			out[*parameter.ParameterKey] = *parameter.ParameterValue
		}
	}
	return out, nil
}

func (c *Client) GetRawSSMParameters() (map[string]interface{}, error) {
	withDecryption := false
	name := fmt.Sprintf("%s.SSMParameterJSON", c.stackName)
	service := ssm.New(c.session)
	request := ssm.GetParameterInput{Name: &name, WithDecryption: &withDecryption}
	response, err := service.GetParameter(&request)
	if err != nil {
		return nil, fmt.Errorf("could not get parameters via SSM: %v", err)
	}
	out := make(map[string]interface{})
	err = json.Unmarshal([]byte(*response.Parameter.Value), &out)
	if err != nil {
		return nil, fmt.Errorf("could not unmarshal SSM parameters: %v", err)
	}
	return out, nil
}

func (c *Client) ImportKeyPair(ctx context.Context, name string, privateKey []byte) error {
	service := ec2.New(c.session)
	drequest := ec2.DeleteKeyPairInput{KeyName: &name}
	service.DeleteKeyPairWithContext(ctx, &drequest)
	irequest := ec2.ImportKeyPairInput{KeyName: &name, PublicKeyMaterial: privateKey}
	_, err := service.ImportKeyPairWithContext(ctx, &irequest)
	if err != nil {
		fmt.Errorf("could not import aws ssh keypair: %v", err)
	}
	return nil
}
