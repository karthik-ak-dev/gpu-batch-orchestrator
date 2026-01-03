# GPU Batch Orchestrator

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Batch%20%7C%20Step%20Functions-orange?logo=amazon-aws)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple?logo=terraform)
![Docker](https://img.shields.io/badge/Container-Docker-blue?logo=docker)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black?logo=github-actions)

A production-ready, serverless orchestration framework for GPU-accelerated batch processing on AWS. Designed for cost-efficient execution of sequential, compute-intensive workloads using AWS Batch, Step Functions, and Infrastructure as Code.

---

## Problem Statement

**Challenge:** Running compute-intensive batch jobs on cloud infrastructure is expensive and complex:
- GPU instances are costly when underutilized
- Managing sequential job dependencies manually is error-prone
- Infrastructure setup is time-consuming and inconsistent across environments
- Container deployment requires manual intervention

**Solution:** This framework provides:
- **Serverless Orchestration** - AWS Step Functions manages job sequencing automatically
- **Cost Optimization** - Auto-scaling GPU compute (0 to N instances on demand)
- **Infrastructure as Code** - One-command deployment with Terraform
- **Automated CI/CD** - Push code, containers deploy automatically

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Sequential Job Orchestration** | Multi-stage pipeline with automatic dependency handling via Step Functions |
| **GPU-Optimized Compute** | AWS Batch with g4dn.xlarge instances (NVIDIA T4 GPUs) |
| **Auto-Scaling** | Scales from 0 to max vCPUs based on workload (pay only when running) |
| **S3 Data Transfer** | Loose coupling between jobs via S3-based data interchange |
| **Infrastructure as Code** | Complete Terraform configuration for reproducible deployments |
| **Containerized Jobs** | Docker containers for consistent execution environments |
| **Automated CI/CD** | GitHub Actions builds and pushes images on every commit |

---

## Tech Stack

| Category | Technologies |
|----------|--------------|
| **Cloud Provider** | AWS (Batch, Step Functions, S3, ECR, IAM) |
| **Compute** | EC2 GPU Instances (g4dn.xlarge - NVIDIA T4) |
| **Orchestration** | AWS Step Functions (State Machine) |
| **Batch Processing** | AWS Batch (Managed Compute Environment) |
| **Container Runtime** | Docker (Python 3.9-slim) |
| **Infrastructure as Code** | Terraform v1.0+ |
| **CI/CD** | GitHub Actions |
| **Language** | Python 3.9, HCL (Terraform), JSON |
| **Storage** | Amazon S3 (data), Amazon ECR (images) |

---

## Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD                                      │
│                                                                             │
│  ┌──────────────┐     ┌─────────────────────────────────────────────────┐   │
│  │   Trigger    │     │           AWS Step Functions                    │   │
│  │  (Console/   │────▶│         (Workflow Orchestrator)                 │   │
│  │   CLI/SDK)   │     │                                                 │   │
│  └──────────────┘     │   ┌─────────┐   ┌─────────┐   ┌─────────┐       │   │
│                       │   │  Job 1  │──▶│  Job 2  │──▶│  Job 3  │       │   │
│                       │   │Ingestion│   │Transform│   │Aggregate│       │   │
│                       │   └─────────┘   └─────────┘   └─────────┘       │   │
│                       └─────────────────────────────────────────────────┘   │
│                                                     │                       │
│                                            ┌────────▼───────────────────┐   │
│  ┌─────────────────────┐                   │        AWS Batch           │   │
│  │     Amazon ECR      │◀──────────────────│  (Managed Compute Env)     │   │
│  │  (Container Images) │                   │                            │   │
│  │                     │                   │  ┌──────────────────────┐  │   │
│  │  • job1-latest      │                   │  │  GPU Compute Pool    │  │   │
│  │  • job2-latest      │                   │  │  g4dn.xlarge (T4)    │  │   │
│  │  • job3-latest      │                   │  │  Auto-scaling: 0-4   │  │   │
│  └─────────────────────┘                   │  └──────────────────────┘  │   │
│                                            └────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           Amazon S3                                     ││
│  │                    (Data Storage & Transfer)                            ││
│  │                                                                         ││
│  │   Job 1 Output: /{job_id}/stage1_output.json                            ││
│  │   Job 2 Output: /{job_id}/stage2_output.json                            ││
│  │   Job 3 Output: /{job_id}/final_output.json                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         PIPELINE DATA FLOW                                 │
└────────────────────────────────────────────────────────────────────────────┘

    INPUT                 PROCESSING STAGES                        OUTPUT
    ═════                 ═════════════════                        ══════

                    ┌──────────────────────┐
   Input Data  ───▶ │   Job 1: Ingestion   │
                    │  • Read input data   │
                    │  • Initial processing│
                    │  • Write to S3       │
                    └──────────┬───────────┘
                               │
                               ▼ stage1_output.json
                    ┌──────────────────────┐
                    │  Job 2: Transform    │
                    │  • Read from S3      │
                    │  • Data transform    │
                    │  • Write to S3       │
                    └──────────┬───────────┘
                               │
                               ▼ stage2_output.json
                    ┌──────────────────────┐
                    │  Job 3: Aggregate    │───▶  Final Results
                    │  • Read from S3      │      (final_output.json)
                    │  • Aggregate data    │
                    │  • Final output      │
                    └──────────────────────┘
```

### Infrastructure Architecture (Terraform)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TERRAFORM MANAGED RESOURCES                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                              IAM LAYER                                       │
│  ┌─────────────────────────┐         ┌─────────────────────────────────┐     │
│  │   Batch Service Role    │         │      ECS Instance Role          │     │
│  │  • AWSBatchServiceRole  │         │  • EC2ContainerServiceRole      │     │
│  │  • ECS_FullAccess       │         │  • AmazonS3FullAccess           │     │
│  └─────────────────────────┘         └─────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           COMPUTE LAYER                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    Batch Compute Environment                           │  │
│  │                                                                        │  │
│  │   Type: EC2 (On-Demand)          Allocation: BEST_FIT_PROGRESSIVE      │  │
│  │   Instance: g4dn.xlarge          vCPUs: 0 (min) → 4 (max)              │  │
│  │   GPU: NVIDIA T4                 Networking: Default VPC/Subnets       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                         Batch Job Queue                                │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│         ┌────────────────────────────┼────────────────────────────┐          │
│         ▼                            ▼                            ▼          │
│  ┌──────────────┐            ┌──────────────┐            ┌──────────────┐    │
│  │   Job 1 Def  │            │   Job 2 Def  │            │   Job 3 Def  │    │
│  │   2 vCPU     │            │   2 vCPU     │            │   2 vCPU     │    │
│  │   4GB RAM    │            │   4GB RAM    │            │   4GB RAM    │    │
│  │   1 GPU      │            │   1 GPU      │            │   1 GPU      │    │
│  └──────────────┘            └──────────────┘            └──────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           STORAGE LAYER                                      │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────────┐  │
│  │      S3 Results Bucket      │    │          ECR Repository             │  │
│  │  • Job input/output data    │    │  • job1-latest                      │  │
│  │  • Intermediate files       │    │  • job2-latest                      │  │
│  │  • Final results            │    │  • job3-latest                      │  │
│  └─────────────────────────────┘    └─────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ACTIONS PIPELINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

   Developer                GitHub                     AWS
   ─────────               ────────                   ─────

      │                        │                         │
      │   git push (main)      │                         │
      │───────────────────────▶│                         │
      │                        │                         │
      │                        │   Trigger Workflow      │
      │                        │─────────────────────────│
      │                        │                         │
      │                        │   ┌─────────────────────────────────┐
      │                        │   │     GitHub Actions Runner       │
      │                        │   │                                 │
      │                        │   │  1. Checkout code               │
      │                        │   │  2. Configure AWS credentials   │
      │                        │   │  3. Login to ECR                │
      │                        │   │  4. Build Docker images (x3)    │
      │                        │   │  5. Push to ECR                 │
      │                        │   └─────────────────────────────────┘
      │                        │                         │
      │                        │   docker push           │
      │                        │────────────────────────▶│
      │                        │                         │
      │                        │                   ┌─────────────┐
      │                        │                   │    ECR      │
      │                        │                   │  (Updated)  │
      │                        │                   └─────────────┘
      │                        │                         │
      │   Workflow Complete    │                         │
      │◀───────────────────────│                         │
```

---

## Project Structure

```
gpu-batch-orchestrator/
├── .github/
│   └── workflows/
│       └── docker-ecr.yml       # CI/CD: Build & push Docker images to ECR
├── jobs/                         # Containerized job implementations
│   ├── job1/                     # Stage 1: Data Ingestion
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── job2/                     # Stage 2: Data Transformation
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── job3/                     # Stage 3: Data Aggregation
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── stepfn/
│   └── workflow.json             # Step Functions state machine definition
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                   # AWS resources (Batch, IAM, S3, ECR)
│   ├── variables.tf              # Configurable parameters
│   ├── outputs.tf                # Terraform outputs (ARNs, URLs)
│   ├── terraform.tfvars.example  # Example configuration
│   └── DEPLOYMENT.md             # Deployment guide
├── requirements.txt              # Python dependencies
└── .gitignore
```

---

## Quick Start

### Prerequisites

- [Terraform](https://www.terraform.io/downloads.html) v1.0+
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate permissions
- [Docker](https://www.docker.com/) (for local testing)

### 1. Deploy Infrastructure

```bash
cd terraform

# Configure your settings
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS region and bucket names

# Initialize and deploy
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### 2. Configure CI/CD

Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `ECR_REPO_NAME`

### 3. Run a Workflow

```bash
# Start execution via AWS CLI
aws stepfunctions start-execution \
  --state-machine-arn <your-state-machine-arn> \
  --input '{"job_id": "sample_001"}'
```

### 4. Monitor Execution

```bash
# Check execution status
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [terraform/DEPLOYMENT.md](terraform/DEPLOYMENT.md) | Step-by-step infrastructure deployment guide |
| [stepfn/workflow.json](stepfn/workflow.json) | Step Functions state machine definition |

---

## Skills Demonstrated

| Skill Area | Technologies & Concepts |
|------------|------------------------|
| **Cloud Architecture** | AWS Batch, Step Functions, S3, ECR, IAM |
| **Infrastructure as Code** | Terraform (modules, state management, outputs) |
| **Containerization** | Docker multi-stage builds, ECR registry |
| **CI/CD Pipelines** | GitHub Actions, automated deployments |
| **Serverless Orchestration** | AWS Step Functions state machines |
| **Cost Optimization** | Auto-scaling (0 to N), On-Demand/Spot strategy |
| **Python Development** | boto3 SDK, modular design, error handling |
| **Security** | IAM roles/policies, least-privilege access |
| **DevOps Practices** | GitOps, automated testing, reproducible builds |

---

## Cost Optimization Features

| Strategy | Implementation |
|----------|---------------|
| **Scale to Zero** | Compute environment scales down to 0 vCPUs when idle |
| **Right-Sizing** | g4dn.xlarge instances for optimal GPU price/performance |
| **On-Demand** | Reliable execution for production workloads |
| **BEST_FIT_PROGRESSIVE** | Optimal instance selection algorithm |
| **Containerized** | Fast startup, minimal overhead |

---

## License

MIT License - feel free to use this as a template for your own GPU batch processing needs.
