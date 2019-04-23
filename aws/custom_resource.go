package aws

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/service/sqs"
	"github.com/google/uuid"
)

const (
	physicalResourceID string        = "PivotalCloudFoundry"
	CRSuccess          crStatus      = "SUCCESS"
	CRFailed                         = "FAILED"
	CRCreate           crRequestType = "Create"
	CRUpdate                         = "Update"
	CRDelete                         = "Delete"
)

type crStatus string
type crRequestType string

type CustomResourceArg struct {
	RequestType       crRequestType
	LogicalResourceID string
	Status            crStatus
	Reason            string
	QueueURL          string
}

type CustomResourceRequest struct {
	RequestType       string `json:"RequestType"`
	ResponseURL       string `json:"ResponseURL"`
	RequestID         string `json:"RequestId"`
	ResourceType      string `json:"ResourceType"`
	LogicalResourceID string `json:"LogicalResourceId"`
}

type CustomResourceResponse struct {
	Status             string `json:"Status"`
	Reason             string `json:"Reason"`
	PhysicalResourceID string `json:"PhysicalResourceId"`
	StackID            string `json:"StackId"`
	RequestID          string `json:"RequestId"`
	LogicalResourceID  string `json:"LogicalResourceId"`
}

func (c *Client) UpdateCustomResource(ctx context.Context, i CustomResourceArg) error {
	requests, err := c.CustomResourceRequests(ctx, i)
	if err != nil {
		return err
	}

	for _, request := range *requests {
		body, err := json.Marshal(CustomResourceResponse{
			Status:             string(i.Status),
			Reason:             i.Reason,
			PhysicalResourceID: physicalResourceID,
			StackID:            c.stackID,
			RequestID:          request.RequestID,
			LogicalResourceID:  request.LogicalResourceID,
		})
		if err != nil {
			return err
		}
		c.logger(ctx).Printf("sending SQS message %s", body)
		hreq, err := http.NewRequest("PUT", request.ResponseURL, bytes.NewReader(body))
		if err != nil {
			return err
		}
		_, err = http.DefaultClient.Do(hreq)
		if err != nil {
			return err
		}
	}
	return nil
}

func (c *Client) CustomResourceRequests(ctx context.Context, i CustomResourceArg) (*[]CustomResourceRequest, error) {
	service := sqs.New(c.session)
	id := uuid.New().String()
	var max int64 = 10
	var visibility int64 = 1
	var waitTimeSeconds int64 = 20
	request := sqs.ReceiveMessageInput{
		QueueUrl:                &i.QueueURL,
		ReceiveRequestAttemptId: &id,
		MaxNumberOfMessages:     &max,
		VisibilityTimeout:       &visibility,
		WaitTimeSeconds:         &waitTimeSeconds,
	}

	var requests []CustomResourceRequest
	var response sqs.ReceiveMessageOutput
	for attempt := 1; attempt <= 5; attempt++ {
		response, err := service.ReceiveMessageWithContext(ctx, &request)
		if err != nil {
			return nil, err
		}
		for _, msg := range response.Messages {
			type Msg struct {
				Message string
			}
			var message Msg
			err := json.Unmarshal([]byte(*msg.Body), &message)
			if err != nil {
				return nil, err
			}
			var req CustomResourceRequest
			err = json.Unmarshal([]byte(message.Message), &req)
			if err != nil {
				return nil, err
			}

			if req.LogicalResourceID == i.LogicalResourceID &&
				req.RequestType == string(i.RequestType) {
				requests = append(requests, req)
			}
		}
		if len(requests) == 0 {
			c.logger(ctx).Printf("retrying: 0 messages of %d matched %s/%s",
				len(response.Messages), i.RequestType, i.LogicalResourceID)
			time.Sleep(time.Second * 5)
		} else {
			break
		}
	}
	c.logger(ctx).Printf("received %d messages(s) of which %d matched %s/%s",
		len(response.Messages), len(requests), i.RequestType, i.LogicalResourceID)
	return &requests, nil
}
