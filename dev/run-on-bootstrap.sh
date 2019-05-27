#!/bin/bash

BOOTSTRAPDNS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=PCF Bootstrap" --query 'Reservations[].Instances[].PublicDnsName' --output text)
go generate templates/templates.go && go build . && scp -i ~/.ssh/aws-oneclick.pem aws-pcf-quickstart ubuntu@${BOOTSTRAPDNS}:/home/ubuntu/ && ssh -i ~/.ssh/aws-oneclick.pem ubuntu@${BOOTSTRAPDNS}
