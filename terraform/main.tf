# create vpc and subnet resources
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

#create internet gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}   

locals {
    public_subnet_cidrs = [
        "10.0.1.0/24", "10.0.2.0/24"
    ]
    private_subnet_cidrs = [
        "10.0.3.0/24", "10.0.4.0/24"
    ]
    region = "us-east-1"
}

# create two public subnets
resource "aws_subnet" "public" {
  count = length(local.public_subnet_cidrs)
  vpc_id = aws_vpc.main.id
  cidr_block = local.public_subnet_cidrs[count.index]
  availability_zone = local.region
  map_public_ip_on_launch = true
} 

# create two private subnets
resource "aws_subnet" "private" {
  count = length(local.private_subnet_cidrs)
  vpc_id = aws_vpc.main.id
  cidr_block = local.private_subnet_cidrs[count.index]
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = false
}

