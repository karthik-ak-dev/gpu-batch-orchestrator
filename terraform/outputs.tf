output "ecr_repo_url" {
  value = aws_ecr_repository.batch_jobs.repository_url
}

output "batch_compute_environment_arn" {
  value = aws_batch_compute_environment.gpu.arn
}

output "batch_job_queue_arn" {
  value = aws_batch_job_queue.main.arn
}

output "batch_job_definition_arn" {
  value = aws_batch_job_definition.job.arn
} 
