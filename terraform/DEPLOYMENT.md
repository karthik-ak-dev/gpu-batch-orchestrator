# Deployment Guide for gpu-batch-orchestrator Terraform

This guide explains how to deploy and destroy the AWS Batch infrastructure using Terraform.

---

## Prerequisites
- [Terraform](https://www.terraform.io/downloads.html) installed (v1.0+ recommended)
- AWS CLI installed and configured with credentials (`aws configure`)
- Sufficient AWS permissions to create IAM, ECR, Batch, and networking resources

---

## 1. Configure Variables

Edit `terraform.tfvars` (or copy from `terraform.tfvars.example`) to set your desired AWS region and ECR repository name:

```
aws_region   = "us-east-1"
ecr_repo_name = "gpu-batch-jobs"
```

---

## 2. Initialize Terraform

From the `terraform/` directory, run:

```
terraform init
```

---

## 3. Deploy Infrastructure (Recommended Workflow)

1. Generate a plan file:
   ```
   terraform plan -out=tfplan
   ```
2. Review the plan output in your terminal.
3. Apply the saved plan:
   ```
   terraform apply tfplan
   ```
- Review the plan and type `yes` to confirm.
- On success, Terraform will output the ECR repo URL, Batch compute environment ARN, job queue ARN, and job definition ARNs.

---

## 4. Destroy Infrastructure

To remove all resources created by this Terraform configuration:

```
terraform destroy
```

- Review the plan and type `yes` to confirm.

---

## Notes
- State is stored locally in the `terraform/` directory by default.
- Make sure your AWS credentials are active and have the necessary permissions.
- For production or team use, consider using a remote backend for state.

---

**For any issues or questions, refer to the main project README or contact the project maintainer.** 