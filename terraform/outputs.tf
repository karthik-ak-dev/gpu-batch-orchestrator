output "ecr_repo_url" {
  description = "ECR repository URL for job images"
  value       = aws_ecr_repository.batch_jobs.repository_url
}

output "s3_bucket_name" {
  description = "S3 bucket name for job results"
  value       = aws_s3_bucket.job_results.bucket
}

output "batch_compute_environment_arn" {
  description = "ARN of the Batch compute environment"
  value       = aws_batch_compute_environment.gpu.arn
}

output "batch_job_queue_arn" {
  description = "ARN of the Batch job queue"
  value       = aws_batch_job_queue.main.arn
}

output "batch_job_definition_arns" {
  description = "ARNs of all Batch job definitions"
  value = [
    aws_batch_job_definition.job1.arn,
    aws_batch_job_definition.job2.arn,
    aws_batch_job_definition.job3.arn
  ]
}
