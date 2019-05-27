#!/bin/bash

BOOTSTRAPDNS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=PCF Bootstrap" --query 'Reservations[].Instances[].PublicDnsName' --output text)
ssh -i ~/.ssh/aws-oneclick.pem ubuntu@${BOOTSTRAPDNS}
