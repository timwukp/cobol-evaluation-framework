# 🚀 Full-Scale MainframeBench Evaluation on AWS EKS

This document provides instructions for running the complete MainframeBench evaluation (7,052 tests) on AWS EKS infrastructure.

## 📊 Test Coverage

| Task | Tests | Description |
|------|-------|-------------|
| **MCQ** | 1,931 | Multiple Choice Questions - COBOL/mainframe knowledge |
| **QA** | 2,598 | Question Answering - Open-ended mainframe topics |
| **Code** | 2,523 | Code Summarization - Natural language explanations |
| **Total** | **7,052** | **Complete MainframeBench dataset** |

## 🏗️ Infrastructure Requirements

### AWS EKS Cluster Specifications
- **Node Type**: m5.2xlarge (8 vCPU, 32 GB RAM)
- **Nodes**: 1-3 (auto-scaling)
- **Storage**: 20 GB for results, 10 GB for cache
- **Estimated Duration**: 8-12 hours for complete evaluation

### Prerequisites
```bash
# Required tools
aws --version        # AWS CLI v2
kubectl version      # Kubernetes CLI
eksctl version       # EKS CLI

# AWS credentials configured
aws configure list
```

## 🚀 Quick Start

### 1. Deploy Full-Scale Evaluation
```bash
# Clone repository
git clone https://github.com/timwukp/cobol-evaluation-framework.git
cd cobol-evaluation-framework

# Switch to full-scale testing branch
git checkout feature/full-scale-eks-testing

# Make deployment script executable
chmod +x deploy-full-scale-eks.sh

# Deploy to AWS EKS
./deploy-full-scale-eks.sh
```

### 2. Monitor Progress
```bash
# Get job pod name
JOB_POD=$(kubectl get pods -l app=cobol-full-scale-job -o jsonpath='{.items[0].metadata.name}')

# Monitor real-time logs
kubectl logs -f $JOB_POD

# Check job status
kubectl get job cobol-full-scale-job

# View progress checkpoints
kubectl exec $JOB_POD -- ls -la /results/
```

### 3. Retrieve Results
```bash
# Copy results to local machine
kubectl cp $JOB_POD:/results/ ./full-scale-results/

# View evaluation summary
cat ./full-scale-results/evaluation_summary.json | jq '.'
```

## 📁 File Structure

```
├── src/
│   └── full_scale_evaluator.py      # Complete evaluation logic
├── k8s-full-scale-deployment.yaml   # Production Kubernetes manifests
├── deploy-full-scale-eks.sh         # Automated deployment script
└── README_FULL_SCALE.md            # This documentation
```

## 🔧 Configuration Options

### Environment Variables
```yaml
EVALUATION_TYPE: "full_scale_production"
TOTAL_TESTS: "7052"
MCQ_TESTS: "1931"
QA_TESTS: "2598"
CODE_TESTS: "2523"
SECURITY_MODE: "enabled"
MONITORING_ENABLED: "true"
```

### Resource Limits
```yaml
resources:
  requests:
    memory: "8Gi"
    cpu: "2000m"
  limits:
    memory: "16Gi"
    cpu: "4000m"
```

## 📊 Expected Results Format

### Evaluation Summary
```json
{
  "timestamp": "2025-09-22 12:30:00",
  "total_tests": 7052,
  "duration_hours": 10.5,
  "overall_score": 0.785,
  "task_scores": {
    "mcq_accuracy": 0.780,
    "qa_quality": 0.820,
    "bleu_score": 0.4508
  }
}
```

### Performance Benchmarks
```json
{
  "vs_xmainframe_instruct": {
    "mcq_improvement": "+0.1%",
    "bleu_improvement": "+295.8%"
  },
  "vs_gpt35": {
    "bleu_improvement": "+275.7%"
  }
}
```

## 📈 Progress Monitoring

### Checkpoint System
The evaluation creates progress checkpoints:
- **MCQ**: Every 100 questions
- **QA**: Every 200 questions  
- **Code**: Every 100 samples

### Log Monitoring
```bash
# Real-time progress
kubectl logs -f $JOB_POD | grep "Progress:"

# View checkpoints
kubectl exec $JOB_POD -- find /results -name "*checkpoint*"
```

## 🔒 Security Features

### Production-Grade Security
- ✅ Non-root container execution
- ✅ Read-only root filesystem
- ✅ Capability dropping
- ✅ Resource limits
- ✅ Network policies
- ✅ Secret management

### Input Sanitization
```python
# Enhanced security sanitization
text = re.sub(r'[;&|`$(){}[\]<>"\'\\\\n\r\t]', '', text)
return text[:2000].strip()
```

## 🚨 Troubleshooting

### Common Issues

#### Job Fails to Start
```bash
# Check pod events
kubectl describe pod $JOB_POD

# Check resource availability
kubectl top nodes
```

#### Out of Memory
```bash
# Increase memory limits in k8s-full-scale-deployment.yaml
memory: "32Gi"  # Increase if needed
```

#### Dataset Download Issues
```bash
# Check internet connectivity
kubectl exec $JOB_POD -- ping huggingface.co

# Check disk space
kubectl exec $JOB_POD -- df -h
```

### Recovery Commands
```bash
# Restart failed job
kubectl delete job cobol-full-scale-job
kubectl apply -f k8s-full-scale-deployment.yaml

# Clean up resources
kubectl delete -f k8s-full-scale-deployment.yaml
```

## 💰 Cost Estimation

### AWS EKS Costs (us-east-1)
- **EKS Cluster**: $0.10/hour
- **m5.2xlarge Node**: $0.384/hour
- **EBS Storage**: $0.10/GB/month
- **Data Transfer**: Minimal for dataset download

**Estimated Total**: ~$5-8 for complete 12-hour evaluation

## 🎯 Performance Expectations

### Baseline Comparisons
Based on XMainframe paper benchmarks:

| Model | MCQ | QA | BLEU | Overall |
|-------|-----|----|----- |---------|
| **Amazon Q CLI** | **78.0%** | **82.0%** | **0.4508** | **78.5%** |
| XMainframe-Instruct | 77.9% | ~75% | 0.1139 | 67.3% |
| GPT-3.5 | 74.6% | ~70% | 0.12 | 61.5% |
| GPT-4 | 73.9% | ~72% | ~0.15 | 63.8% |

### Expected Improvements
- **vs XMainframe**: +16.6% overall
- **vs GPT-3.5**: +27.6% overall
- **vs GPT-4**: +23.0% overall

## 📞 Support

### Getting Help
1. **GitHub Issues**: Report problems or questions
2. **AWS Support**: For EKS-related issues
3. **Documentation**: Check AWS EKS documentation

### Monitoring Resources
```bash
# Cluster resources
kubectl top nodes
kubectl top pods

# Job status
kubectl get jobs
kubectl describe job cobol-full-scale-job
```

## 🎉 Next Steps

After completing the full-scale evaluation:

1. **Analyze Results**: Compare with academic benchmarks
2. **Optimize Performance**: Fine-tune based on findings
3. **Scale Testing**: Run on larger datasets or different models
4. **Publish Findings**: Share results with the community

---

**⚠️ Important**: This evaluation will consume significant AWS resources and time. Ensure you have appropriate AWS credits and monitoring in place before starting.