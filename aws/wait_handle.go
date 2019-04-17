package aws

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"

	"github.com/google/uuid"
)

const (
	WHSuccess whStatus = "SUCCESS"
	WHFailure          = "FAILURE"
)

type whStatus string
type UpdateWaitHandleInput struct {
	Status    whStatus
	Data      string
	Reason    string
	HandleURL string
}
type WaitHandleResponse struct {
	Status   string `json:"Status"`
	UniqueID string `json:"UniqueId"`
	Data     string `json:"Data"`
	Reason   string `json:"Reason"`
}

func (c *Client) UpdateWaitHandle(ctx context.Context, i UpdateWaitHandleInput) error {
	body, err := json.Marshal(WaitHandleResponse{
		Status:   string(i.Status),
		Reason:   i.Reason,
		UniqueID: uuid.New().String(),
		Data:     i.Data,
	})
	if err != nil {
		return err
	}
	hreq, err := http.NewRequest("PUT", i.HandleURL, bytes.NewReader(body))
	if err != nil {
		return err
	}
	_, err = http.DefaultClient.Do(hreq)
	if err != nil {
		return err
	}
	return nil
}
