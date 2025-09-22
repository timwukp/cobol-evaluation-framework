#!/bin/bash
# Full-Scale MainframeBench Evaluation on AWS EKS
# Deploys and runs complete 7,052 test evaluation

set -e

echo "🚀 FULL-SCALE MAINFRAMEBENCH EVALUATION ON AWS EKS"
echo "=================================================="
echo "Total Tests: 7,052"
echo "- MCQ: 1,931 tests"
echo "- QA: 2,598 tests"
echo "- Code Summarization: 2,523 tests"
echo "=================================================="

# Configuration
CLUSTER_NAME="cobol-eval-cluster"
REGION="us-east-1"
NODE_TYPE="m5.2xlarge"  # 8 vCPU, 32 GB RAM for full dataset
MIN_NODES=1
MAX_NODES=3
NAMESPACE="default"

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI required"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl required"; exit 1; }
command -v eksctl >/dev/null 2>&1 || { echo "❌ eksctl required"; exit 1; }

# Check AWS credentials
aws sts get-caller-identity >/dev/null 2>&1 || { echo "❌ AWS credentials not configured"; exit 1; }
echo "✅ Prerequisites check passed"

# Create EKS cluster if it doesn't exist
echo "🏗️  Setting up EKS cluster..."
if ! eksctl get cluster --name $CLUSTER_NAME --region $REGION >/dev/null 2>&1; then
    echo "Creating new EKS cluster: $CLUSTER_NAME"
    eksctl create cluster \
        --name $CLUSTER_NAME \
        --region $REGION \
        --node-type $NODE_TYPE \
        --nodes-min $MIN_NODES \
        --nodes-max $MAX_NODES \
        --managed \
        --enable-ssm \
        --version 1.28
else
    echo "✅ EKS cluster $CLUSTER_NAME already exists"
fi

# Update kubeconfig
echo "🔧 Updating kubeconfig..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Verify cluster connection
echo "🔍 Verifying cluster connection..."
kubectl get nodes

# Create namespace if needed
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy application code to cluster
echo "📦 Deploying application code..."
kubectl create configmap app-source \
    --from-file=src/ \
    --from-file=requirements.txt \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# Update secrets with actual AWS credentials
echo "🔐 Setting up AWS credentials..."
AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found in AWS CLI config"
    echo "Please run: aws configure"
    exit 1
fi

# Create secret with actual credentials
kubectl create secret generic cobol-full-scale-secrets \
    --from-literal=AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    --from-literal=AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    --from-literal=AWS_REGION="$REGION" \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# Deploy the full-scale evaluation
echo "🚀 Deploying full-scale evaluation job..."
kubectl apply -f k8s-full-scale-deployment.yaml

# Wait for job to start
echo "⏳ Waiting for job to start..."
kubectl wait --for=condition=Ready pod -l app=cobol-full-scale-job --timeout=300s

# Get job pod name
JOB_POD=$(kubectl get pods -l app=cobol-full-scale-job -o jsonpath='{.items[0].metadata.name}')
echo "📊 Job started in pod: $JOB_POD"

# Monitor job progress
echo "📈 Monitoring evaluation progress..."
echo "This will take several hours to complete all 7,052 tests..."
echo ""
echo "To monitor progress:"
echo "  kubectl logs -f $JOB_POD"
echo ""
echo "To check job status:"
echo "  kubectl get job cobol-full-scale-job"
echo ""
echo "To get results:"
echo "  kubectl exec $JOB_POD -- ls -la /results/"
echo "  kubectl cp $JOB_POD:/results/ ./full-scale-results/"

# Function to monitor job
monitor_job() {
    echo "🔍 Starting job monitoring..."
    
    while true; do
        JOB_STATUS=$(kubectl get job cobol-full-scale-job -o jsonpath='{.status.conditions[0].type}' 2>/dev/null || echo "Running")
        
        case $JOB_STATUS in
            "Complete")
                echo "✅ Job completed successfully!"
                break
                ;;
            "Failed")
                echo "❌ Job failed!"
                kubectl describe job cobol-full-scale-job
                exit 1
                ;;
            *)
                echo "⏳ Job still running... (Status: $JOB_STATUS)"
                # Show recent logs
                kubectl logs --tail=5 $JOB_POD 2>/dev/null || echo "Waiting for logs..."
                sleep 300  # Check every 5 minutes
                ;;
        esac
    done
}

# Ask user if they want to monitor
read -p "🤔 Do you want to monitor the job progress? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    monitor_job
else
    echo "📝 Job is running in background. Use the commands above to monitor progress."
fi

# Function to retrieve results
retrieve_results() {
    echo "📥 Retrieving evaluation results..."
    
    # Create local results directory
    mkdir -p ./full-scale-results
    
    # Copy results from pod
    kubectl cp $JOB_POD:/results/ ./full-scale-results/ 2>/dev/null || echo "⚠️  Results not ready yet"
    
    # Show summary if available
    if [ -f "./full-scale-results/evaluation_summary.json" ]; then
        echo "📊 EVALUATION SUMMARY:"
        cat ./full-scale-results/evaluation_summary.json | jq '.'
    fi
    
    echo "📁 Results saved to: ./full-scale-results/"
}

# Ask if user wants to retrieve results now
if [[ $REPLY =~ ^[Yy]$ ]]; then
    retrieve_results
fi

echo ""
echo "🎉 Full-scale deployment complete!"
echo "=================================================="
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Job: cobol-full-scale-job"
echo "Pod: $JOB_POD"
echo ""
echo "📋 Next steps:"
echo "1. Monitor: kubectl logs -f $JOB_POD"
echo "2. Check status: kubectl get job cobol-full-scale-job"
echo "3. Get results: kubectl cp $JOB_POD:/results/ ./full-scale-results/"
echo ""
echo "⚠️  Note: This evaluation will take several hours to complete all 7,052 tests"
echo "=================================================="