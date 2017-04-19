# The script will delete an existing Ops Manager VM and deploy a new one

# Create all user-defined env variables
echo "Creating user defined env vars"
AwsRegion="us-west-2"
OpsManImageId="ami-3441c854"
OpsManPrivateIp="10.0.0.98"
PcfStackName="pcf-stack"
PcfOpsManNameTag="PCF-OpsManager"
OpsManKeyPairName="pcf-opsmanager-keypair"

# Delete the Ops Manager VM instance if it exists

echo 'Terminate Ops Manager VM if it exists'
OpsMan_Instance_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$PcfOpsManNameTag" "Name=instance-state-name,Values=running" --output text --query "Reservations[*].Instances[*].InstanceId")

# wait for the VM to go from shutting-down to terminated state

if [ "" = "$OpsMan_Instance_ID" ]; then
	echo 'Ops Manager Instance ' $tempInstId ' does not exist'
else
	echo "Terminating existing Ops Manager VM [InstanceId=" $OpsMan_Instance_ID "] ..."
	tempInstId=$(aws ec2 terminate-instances --instance-ids $OpsMan_Instance_ID --output text --query 'TerminatingInstances[*].InstanceId')
	echo 'Termination in progress for Ops Manager VM InstanceId ' $tempInstId
	while state=$(aws ec2 describe-instances --instance-ids $tempInstId --output text --query 'Reservations[*].Instances[*].State.Name'); test "$state" = "shutting-down"; do
	  sleep 1; echo -n '.'
	done; echo " $state"
fi
		   
# clear $tempInstId
tempInstId=''

# state values = shutting-down, terminated

# Create all env variables from the CloudFormation output
echo "Creating Env Vars from Cloud Formation script output"

PcfOpsManagerSecurityGroupId=$(aws cloudformation describe-stacks --stack-name $PcfStackName --output text --query 'Stacks[0].Outputs[?OutputKey==`PcfOpsManagerSecurityGroupId`].OutputValue')
PcfPublicSubnetId=$(aws cloudformation describe-stacks --stack-name $PcfStackName --output text --query 'Stacks[0].Outputs[?OutputKey==`PcfPublicSubnetId`].OutputValue')

# Now deploy the Ops Man VM with an assigned private IP
echo "Creating Ops Manager VM"
OpsMan_Instance_ID=$(aws ec2 run-instances --image-id $OpsManImageId --count 1 --instance-type m3.large --key-name $OpsManKeyPairName --security-group-ids $PcfOpsManagerSecurityGroupId --subnet-id $PcfPublicSubnetId --associate-public-ip-address --private-ip-address $OpsManPrivateIp --region $AwsRegion --block-device-mappings "[{\"DeviceName\": \"/dev/sda1\",\"Ebs\":{\"VolumeSize\":100}}]" --monitoring Enabled=true --output text --query 'Instances[*].InstanceId')

echo "New Ops Manager VM created Instance ID is " $OpsMan_Instance_ID

# wait for the VM to go from pending to running state
while state=$(aws ec2 describe-instances --instance-ids $OpsMan_Instance_ID --output text --query 'Reservations[*].Instances[*].State.Name'); test "$state" = "pending"; do
  sleep 1; echo -n '.'
done; echo " $state"

# create a Name tag for the Ops Man VM
echo "create a Name tag ["$PcfOpsManNameTag"] for the Ops Man VM "
aws ec2 create-tags --resources $OpsMan_Instance_ID --tags 'Key="Name",Value="'$PcfOpsManNameTag'"'

# Fetch the Ops Man Public IP and FQDN in the next 2 steps
OpsMan_PublicIpAddress=$(aws ec2 describe-instances  --instance-ids $OpsMan_Instance_ID --output text --query "Reservations[*].Instances[*].PublicIpAddress")
OpsMan_PublicDnsName=$(aws ec2 describe-instances  --instance-ids $OpsMan_Instance_ID --output text --query "Reservations[*].Instances[*].PublicDnsName")

echo "New Ops Manager FQDN is " $OpsMan_PublicDnsName
echo "New Ops Manager Public IP Address is " $OpsMan_PublicIpAddress
