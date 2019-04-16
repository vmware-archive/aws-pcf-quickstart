package aws

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/google/uuid"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudformation"
	"github.com/aws/aws-sdk-go/service/ec2"
	"github.com/aws/aws-sdk-go/service/sqs"
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
		return nil, err
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

func (c *Client) SignalResource(ctx context.Context, resourceId string, success bool) error {
	status := "success"
	if !success {
		status = "failure"
	}
	id := uuid.New().String()
	service := cloudformation.New(c.session)
	request := cloudformation.SignalResourceInput{
		LogicalResourceId: &resourceId,
		StackName:         &c.stackName,
		Status:            &status,
		UniqueId:          &id,
	}
	_, err := service.SignalResourceWithContext(ctx, &request)
	return err
}

func (c *Client) ReceiveMessage(ctx context.Context, queueUrl string) error {
	service := sqs.New(c.session)
	all := "All"
	id := uuid.New().String()
	var max int64 = 10
	var visibility int64 = 1
	request := sqs.ReceiveMessageInput{
		AttributeNames:        []*string{&all},
		MessageAttributeNames: []*string{&all},

		QueueUrl:                &queueUrl,
		ReceiveRequestAttemptId: &id,
		MaxNumberOfMessages:     &max,
		VisibilityTimeout:       &visibility,
	}
	_, err := service.ReceiveMessageWithContext(ctx, &request)
	// TODO return repsonse
	return err
}

func (c *Client) GetRawSSMParameters() (map[string]interface{}, error) {
	withDecryption := false
	name := fmt.Sprintf("%s.SSMParameterJSON", c.stackName)
	service := ssm.New(c.session)
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

func (c *Client) ImportKeyPair(ctx context.Context, name string, privateKey []byte) error {
	service := ec2.New(c.session)
	request := ec2.ImportKeyPairInput{KeyName: &name, PublicKeyMaterial: privateKey}
	_, err := service.ImportKeyPairWithContext(ctx, &request)
	return err
}
