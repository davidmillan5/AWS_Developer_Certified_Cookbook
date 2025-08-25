# EC2 Fundamentals


## What is Amazon EC2?

***Amazon Elastic Compute Cloud (Amazon EC2)*** provides on-demand, scalable computing capacity in the Amazon Web 
Services (AWS) Cloud. Using Amazon EC2 reduces hardware costs so you can develop and deploy applications faster. You 
can use Amazon EC2 to launch as many or as few virtual servers as you need, configure security and networking, and 
manage storage. You can add capacity (scale up) to handle compute-heavy tasks, such as monthly or yearly processes, or 
spikes in website traffic. When usage decreases, you can reduce capacity (scale down) again.

An EC2 instance is a virtual server in the AWS Cloud. When you launch an EC2 instance, the instance type that you 
specify determines the hardware available to your instance. Each instance type offers a different balance of compute, 
memory, network, and storage resources.


<p align="center">
  <a href="https://example.com">
    <img src="https://docs.aws.amazon.com/images/AWSEC2/latest/UserGuide/images/instance-types.png" width="400" height="200"/>
  </a>
</p>


# Features of Amazon EC2

Amazon EC2 provides the following high-level features:

## Instances
Virtual servers.

## Amazon Machine Images (AMIs)
Preconfigured templates for your instances that package the components you need for your server (including the operating system and additional software).

## Instance Types
Various configurations of CPU, memory, storage, networking capacity, and graphics hardware for your instances.

## Amazon EBS Volumes
Persistent storage volumes for your data using Amazon Elastic Block Store (Amazon EBS).

## Instance Store Volumes
Storage volumes for temporary data that is deleted when you stop, hibernate, or terminate your instance.

## Key Pairs
Secure login information for your instances. AWS stores the public key and you store the private key in a secure place.

## Security Groups
A virtual firewall that allows you to specify the protocols, ports, and source IP ranges that can reach your instances, and the destination IP ranges to which your instances can connect.


## Walkthrough to Launch a new EC2 Intances Through CLI Commands

### ***Configure the CLI (one-time)***

This stores your keys and defaults locally.

```
aws --version
aws configure
# Enter:
# AWS Access Key ID: <your_access_key_id>
# AWS Secret Access Key: <your_secret_access_key>
# Default region name: us-east-1      # or your preferred region
# Default output format: json

```

### ***Make a key pair (for SSH)***

We’ll save a PEM file and lock down its permissions.

```
KeyName=cli-key
aws ec2 create-key-pair --profile myprofile --key-name "$KeyName" --key-format pem --query 'KeyMaterial' --output text > "$KeyName.pem"

```
### ***Ensure you have a default VPC***


Verify if you have a default VPC active
```
aws ec2 describe-vpcs --profile david_admin \
  --filters Name=isDefault,Values=true \
  --query "Vpcs[0].VpcId" \
  --output text

```

If you don't have a default VPC you can create one with the following command

```
aws ec2 create-default-vpc --profile david_admin \
  --query "Vpc.VpcId" \
  --output text

```
### ***How to Create a Security Group***

```
# 1. Set your known VPC ID
VpcId="vpc-1234567890abcdef0"   # <-- replace with your real VPC ID

# 2. Create a new security group in that VPC
SgName=cli-sg
SgId=$(aws ec2 create-security-group \
  --profile david_admin \
  --group-name "$SgName" \
  --description "Allow SSH from my IP" \
  --vpc-id "$VpcId" \
  --query "GroupId" \
  --output text)

# 3. Get your public IP and convert it into CIDR notation
MyIpCidr="$(curl -s https://checkip.amazonaws.com)/32"

# 4. Authorize inbound SSH (port 22) only from your IP
aws ec2 authorize-security-group-ingress \
  --profile david_admin \
  --group-id "$SgId" \
  --protocol tcp \
  --port 22 \
  --cidr "$MyIpCidr"

# (Optional) Authorize inbound HTTP (port 80) from anywhere
# aws ec2 authorize-security-group-ingress \
#   --profile david_admin \
#   --group-id "$SgId" \
#   --protocol tcp \
#   --port 80 \
#   --cidr 0.0.0.0/0

# 5. Print the Security Group ID
echo $SgId


```


### ***Pick a Free Tier AMI (Amazon Linux)***

```
# Variables
Ami="ami-0b016c703b95ecbe4"   # Amazon Linux 2023 AMI for us-east-2
InstanceType="t3.micro"       # Free Tier eligible
KeyName="your-keypair-name"   # <-- replace with your actual EC2 key pair name
SgId="sg-xxxxxxxx"            # <-- replace with your created Security Group ID
TagSpec='ResourceType=instance,Tags=[{Key=Name,Value=cli-ec2}]'

# Launch the instance
InstanceId=$(aws ec2 run-instances \
  --region us-east-2 \
  --profile david_admin \
  --image-id "$Ami" \
  --instance-type "$InstanceType" \
  --key-name "$KeyName" \
  --security-group-ids "$SgId" \
  --tag-specifications "$TagSpec" \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Launched instance: $InstanceId"


```


###***Check The Status of your instance***

```
aws ec2 describe-instances \
  --instance-ids $InstanceId \
  --region us-east-2 \
  --profile david_admin \
  --query "Reservations[*].Instances[*].{ID:InstanceId,State:State.Name,Type:InstanceType,AZ:Placement.AvailabilityZone,PublicIP:PublicIpAddress}" \
  --output table

```

###***Start/Stop/Terminate your Instance***

```
# Stop
aws ec2 stop-instances --instance-ids $InstanceId --region us-east-2 --profile david_admin

# Start again
aws ec2 start-instances --instance-ids $InstanceId --region us-east-2 --profile david_admin

aws ec2 terminate-instances --instance-ids $InstanceId --region us-east-2 --profile david_admin

```