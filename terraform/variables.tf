# AWS region to deploy resources in
variable "aws_region" {
  description = "AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

# Name of the ECR repository for batch jobs
variable "ecr_repo_name" {
  description = "Name of the ECR repository for batch jobs."
  type        = string
  default     = "gpu-batch-jobs"
}
