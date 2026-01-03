# AWS provider configuration
provider "aws" {
  region = var.aws_region
}

# S3 bucket for storing job results
resource "aws_s3_bucket" "job_results" {
  bucket = var.results_bucket_name
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

data "aws_iam_policy_document" "batch_service_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["batch.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "batch_service" {
  role       = aws_iam_role.batch_service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role_policy_attachment" "batch_service_ecs_full" {
  role       = aws_iam_role.batch_service.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

# Batch compute environment for GPU workloads
resource "aws_batch_compute_environment" "gpu" {
  name = "gpu-batch-ce"
  compute_resources {
    type                = "EC2"
    max_vcpus           = 4
    min_vcpus           = 0
    desired_vcpus       = 0
    instance_type       = ["g4dn.xlarge"]
    subnets             = data.aws_subnets.default.ids
    security_group_ids  = [data.aws_security_group.default.id]
    instance_role       = aws_iam_instance_profile.ecs_instance.arn
    allocation_strategy = "BEST_FIT_PROGRESSIVE"
  }
  service_role = aws_iam_role.batch_service.arn
  type         = "MANAGED"
  state        = "ENABLED"
}

# Get default subnets
data "aws_subnets" "default" {
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

# Get default security group
data "aws_security_group" "default" {
  filter {
    name   = "group-name"
    values = ["default"]
  }
  vpc_id = data.aws_vpc.default.id
}

# Get default VPC
data "aws_vpc" "default" {
  default = true
}

# IAM role for EC2 instances
resource "aws_iam_role" "ecs_instance" {
  name               = "ecs_instance_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_instance_assume_role.json
}

data "aws_iam_policy_document" "ecs_instance_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com", "ecs.amazonaws.com", "ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs_instance" {
  role       = aws_iam_role.ecs_instance.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy_attachment" "ecs_instance_s3" {
  role       = aws_iam_role.ecs_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "ecs_instance" {
  name = "ecs_instance_profile"
  role = aws_iam_role.ecs_instance.name
}

# Batch job queue
resource "aws_batch_job_queue" "main" {
  name     = "gpu-batch-queue"
  state    = "ENABLED"
  priority = 1
  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.gpu.arn
  }
}

# Job definitions for each pipeline stage
resource "aws_batch_job_definition" "job1" {
  name = "gpu-batch-job1"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job1-latest",
    vcpus : 2,
    memory : 4096,
    resourceRequirements : [{ type : "GPU", value : "1" }],
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}

resource "aws_batch_job_definition" "job2" {
  name = "gpu-batch-job2"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job2-latest",
    vcpus : 2,
    memory : 4096,
    resourceRequirements : [{ type : "GPU", value : "1" }],
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}

resource "aws_batch_job_definition" "job3" {
  name = "gpu-batch-job3"
  type = "container"
  container_properties = jsonencode({
    image : "${aws_ecr_repository.batch_jobs.repository_url}:job3-latest",
    vcpus : 2,
    memory : 4096,
    resourceRequirements : [{ type : "GPU", value : "1" }],
    jobRoleArn : aws_iam_role.ecs_instance.arn
  })
}
