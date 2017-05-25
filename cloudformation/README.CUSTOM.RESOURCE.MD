### Custom Resource CLI commands for interacting with Custom Resource.

#### Install all the relevant Tools.
```
    sudo yum update
    sudo yum install awscli jq
```

#### Set the Relevant ENV Variables
```
    export QURL=https:$(grep URL ~/SQSInfo.yml | cut -d: -f3)
    export QARN=$(grep ARN ~/SQSInfo.yml | cut -d: -f2,3,4,5,6,7)
    export SQSMSG=$(aws --region us-west-2 sqs receive-message --queue-url $QURL)
```

#### View the SQS Message Content related to the Custom Resource
```
    echo $SQSMSG | jq  -r '.Messages[0].Body' | jq -r '.Message' | jq
```

#### Construct Response JSON
```
    echo $SQSMSG | jq  -r '.Messages[0].Body' | jq -r '.Message' | jq '. | {Status: "SUCCESS", PhysicalResourceId: "CFPhase1", RequestId: .RequestId, LogicalResourceId: .LogicalResourceId,StackId: .StackId, Data: {ResponseItem1: "Item1", ResponseItem2: "Item2"} }' > response.json
```

#### Make CURL Request to Pre-Signed URL with Prepared JSON.
```
    curl -v --upload-file ./response.json $(echo $SQSMSG | jq  -r '.Messages[0].Body' | jq -r '.Message' | jq -r .ResponseURL)
```