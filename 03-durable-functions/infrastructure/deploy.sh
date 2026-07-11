#!/bin/bash
set -e

REPO_NAME="durable-agents"
REGION=$(aws configure get region 2>/dev/null || echo "us-east-1")
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:latest"

echo "=== Deploying Claude Agent SDK + Durable Functions ==="
echo "  Account: ${ACCOUNT_ID}"
echo "  Region:  ${REGION}"
echo "  Image:   ${IMAGE_URI}"
echo ""

# Step 1: Create ECR repo if it doesn't exist
echo "--- Creating ECR repository (if needed) ---"
aws ecr describe-repositories --repository-names ${REPO_NAME} 2>/dev/null || \
  aws ecr create-repository --repository-name ${REPO_NAME} --image-scanning-configuration scanOnPush=true

# Step 2: Login to ECR
echo "--- Logging in to ECR ---"
aws ecr get-login-password --region ${REGION} | \
  docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Step 3: Build container image
echo "--- Building container image ---"
cd "$(dirname "$0")/.."
docker build --platform linux/arm64 -t ${REPO_NAME}:latest .

# Step 4: Tag and push
echo "--- Pushing to ECR ---"
docker tag ${REPO_NAME}:latest ${IMAGE_URI}
docker push ${IMAGE_URI}

# Step 5: Deploy CloudFormation stack
echo "--- Deploying SAM stack ---"
cd infrastructure
sam deploy \
  --stack-name sam-app-durable \
  --no-confirm-changeset \
  --capabilities CAPABILITY_IAM \
  --resolve-image-repos \
  --parameter-overrides "BedrockModelId=us.anthropic.claude-sonnet-4-6"

echo ""
echo "=== Deployment complete ==="
echo "Invoke with:"
echo "  aws lambda invoke --function-name basic-durable-agent:live \\"
echo "    --payload '{\"prompt\": \"Research AWS Lambda durable functions\"}' \\"
echo "    --cli-binary-format raw-in-base64-out response.json"
