# gpu-batch-orchestrator

Efficient orchestration of GPU workloads using AWS Batch, Step Functions, and automated CI/CD with GitHub Actions.

---

## 1. AWS Batch Infrastructure (Terraform)

This project uses **Terraform** to provision and manage all AWS Batch resources for running GPU-accelerated workloads at scale and low cost.

### Key Components
- **Compute Environment**: Uses GPU-backed EC2 instance types (`g4dn.xlarge`, `g5.xlarge`, `p3.2xlarge`) as **Spot Instances** to minimize costs.
- **Job Queue**: Routes jobs to the compute environment.
- **Job Definitions**: Specifies containerized Python workloads, including GPU, CPU, memory, and ECR image.
- **IAM Roles/Policies**: Grants AWS Batch permissions for EC2 Spot, ECR, and S3 access.
- **Allocation Strategy**: Uses `BEST_FIT_PROGRESSIVE` to optimize Spot instance usage and cost savings.

### How it Works
- All infrastructure is defined in Terraform code.
- Developers can easily update or redeploy infrastructure using Terraform commands.

---

## 2. CI/CD: Docker Build & Deploy with GitHub Actions

A GitHub Actions workflow automates Docker image builds and pushes to Amazon ECR on every push to the `main` branch.

### Workflow Steps
1. **Authenticate to AWS** using GitHub Secrets.
2. **Build Docker Image** for your Python workload.
3. **Tag & Push** the image to your ECR repository.

### Benefits
- Developers only need to commit code changes.
- No manual Docker/ECR steps required.
- AWS Batch and Step Functions always use the latest image.

---

## 3. AWS Step Functions Workflow (YAML/JSON)

The workflow is defined outside Terraform (in YAML or JSON) and coordinates the execution of multiple AWS Batch jobs.

### Workflow Structure
- **Parallel Step**: Runs two AWS Batch jobs (Step 1 & 2) at the same time using `batch:submitJob.sync`.
- **Sequential Steps**: After both parallel jobs finish, runs Step 3, then Step 4, each as AWS Batch jobs.
- **Data Passing**: Uses S3 URLs to pass outputs between steps.
- **Configuration**: Each step specifies the Batch job definition ARN, job queue ARN, and container overrides (commands, parameters).

### How to Trigger
- Start executions via AWS Console, CLI, or SDK with a JSON payload.
- AWS Batch provisions GPU Spot instances as needed for each job.

---

## 4. Jobs/Tasks Folder Structure

The `jobs/` directory contains the Python scripts that are executed by each step in the Step Functions workflow. Each job is organized in its own subfolder, with its own script, requirements, and Dockerfile.

### Structure

```
jobs/
  job1/
    main.py
    requirements.txt
    Dockerfile
  job2/
    main.py
    requirements.txt
    Dockerfile
  job3/
    main.py
    requirements.txt
    Dockerfile
  job4/
    main.py
    requirements.txt
    Dockerfile
```

- Each `main.py` implements the logic for a workflow step, taking input (e.g., from S3 or parameters) and producing output (e.g., uploading to S3).
- Each job is containerized for AWS Batch execution.

---

## Summary
- **Infrastructure as Code**: All AWS Batch resources managed by Terraform.
- **Automated CI/CD**: GitHub Actions builds and deploys Docker images to ECR.
- **Flexible Orchestration**: Step Functions coordinates complex GPU workflows with cost-efficient Spot instances.

---

**Simple, scalable, and cost-effective orchestration for GPU workloads on AWS.**
