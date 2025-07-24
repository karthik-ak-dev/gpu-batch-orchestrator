# NOTE: By default, Terraform state (terraform.tfstate) and lock files will be stored locally in this terraform/ directory.
# For team or production use, consider configuring a remote backend (e.g., S3 + DynamoDB).

# AWS provider configuration
provider "aws" {
  region = var.aws_region
}

# ECR repository for all job images
resource "aws_ecr_repository" "batch_jobs" {
  name = var.ecr_repo_name
}

# IAM role for AWS Batch service
resource "aws_iam_role" "batch_service" {
  name               = "batch_service_role"
  assume_role_policy = data.aws_iam_policy_document.batch_service_assume_role.json
}

# IAM policy document for Batch service role
# Allows AWS Batch to assume this role
data "aws_iam_policy_document" "batch_service_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["batch.amazonaws.com"]
    }
  }
}

# Attach AWS managed Batch service role policy
resource "aws_iam_role_policy_attachment" "batch_service" {
  role       = aws_iam_role.batch_service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

# Attach AmazonEC2ContainerServiceFullAccess policy to Batch service role
resource "aws_iam_role_policy_attachment" "batch_service_ecs_full" {
  role       = aws_iam_role.batch_service.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerServiceFullAccess"
}

# Batch compute environment for GPU workloads (EC2 On-Demand instances, default VPC)
resource "aws_batch_compute_environment" "gpu" {
  name = "gpu-batch-ce"
  compute_resources {
    type                = "EC2"                                      # Use On-Demand EC2 instances
    max_vcpus           = 16                                         # Max vCPUs for scaling
    min_vcpus           = 0                                          # No always-on capacity
    desired_vcpus       = 0                                          # Start with zero, scale as needed
    instance_type       = ["g4dn.xlarge", "g5.xlarge", "p3.2xlarge"] # GPU-backed EC2 types
    subnets             = data.aws_subnets.default.ids               # Use default VPC subnets
    security_group_ids  = [data.aws_security_group.default.id]       # Use default security group
    instance_role       = aws_iam_instance_profile.ecs_instance.arn  # EC2 instance profile for ECS
    allocation_strategy = "BEST_FIT_PROGRESSIVE"                     # Optimize usage
  }
  service_role = aws_iam_role.batch_service.arn
  type         = "MANAGED"
  state        = "ENABLED"
}

# Get default subnets for the region
# Ensures compute environment uses default networking
data "aws_subnets" "default" {
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

# Get default security group in the default VPC
# Used for compute environment networking
data "aws_security_group" "default" {
  filter {
    name   = "group-name"
    values = ["default"]
  }
  vpc_id = data.aws_vpc.default.id
}

# Get the default VPC
# Used for networking resources
data "aws_vpc" "default" {
  default = true
}

# IAM role for EC2 instances in the compute environment
resource "aws_iam_role" "ecs_instance" {
  name               = "ecs_instance_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_instance_assume_role.json
}

# IAM policy document for EC2 instance role
# Allows EC2 to assume this role
data "aws_iam_policy_document" "ecs_instance_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

# Attach ECS instance role policy to EC2 role
resource "aws_iam_role_policy_attachment" "ecs_instance" {
  role       = aws_iam_role.ecs_instance.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

# Attach AmazonS3FullAccess policy to EC2 role for full S3 access from jobs
resource "aws_iam_role_policy_attachment" "ecs_instance_s3" {
  role       = aws_iam_role.ecs_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Instance profile for EC2 instances in the compute environment
resource "aws_iam_instance_profile" "ecs_instance" {
  name = "ecs_instance_profile"
  role = aws_iam_role.ecs_instance.name
}

# AWS Batch job queue (connects jobs to compute environment)
#
# The job queue is where jobs are submitted. It acts as a buffer between job submissions and compute environments.
# Jobs in the queue are scheduled to run on the compute environments in the order specified.
#
# Attributes:
#   - name: Name of the job queue.
#   - state: ENABLED means the queue can accept jobs.
#   - priority: Higher priority queues are evaluated first by the scheduler.
#   - compute_environment_order: List of compute environments and their order for job placement.
#       - order: Lower numbers are higher priority (1 is highest). If the first environment is full/unavailable, the next is used.
#       - compute_environment: ARN of the compute environment to use for running jobs.
resource "aws_batch_job_queue" "main" {
  name     = "gpu-batch-queue"
  state    = "ENABLED"
  priority = 1
  compute_environment_order {
    order               = 1                                     # Highest priority (first to be used for job placement)
    compute_environment = aws_batch_compute_environment.gpu.arn # The compute environment where jobs will run
  }
}

# Example AWS Batch job definition for job1 (minimal resources)
resource "aws_batch_job_definition" "job1" {
  name = "gpu-batch-job1"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job1-latest",
    vcpus : 1,                                              # Minimum vCPUs
    memory : 512,                                           # Minimum memory in MiB
    resourceRequirements : [{ type : "GPU", value : "1" }], # Minimum 1 GPU (cannot be less)
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}

# Example AWS Batch job definition for job2 (minimal resources)
resource "aws_batch_job_definition" "job2" {
  name = "gpu-batch-job2"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job2-latest",
    vcpus : 1,
    memory : 512,
    resourceRequirements : [{ type : "GPU", value : "1" }],
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}

# Example AWS Batch job definition for job3 (minimal resources)
resource "aws_batch_job_definition" "job3" {
  name = "gpu-batch-job3"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job3-latest",
    vcpus : 1,
    memory : 512,
    resourceRequirements : [{ type : "GPU", value : "1" }],
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}

# Example AWS Batch job definition for job4 (minimal resources)
resource "aws_batch_job_definition" "job4" {
  name = "gpu-batch-job4"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job4-latest",
    vcpus : 1,
    memory : 512,
    resourceRequirements : [{ type : "GPU", value : "1" }],
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}
