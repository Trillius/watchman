# Kubernetes Deployment Guide for Watchman

This guide covers deploying the Watchman Discord bot to Kubernetes using either Helm charts or raw manifests.

## Prerequisites

- Kubernetes cluster (v1.19+)
- `kubectl` configured to access your cluster
- [Helm v3](https://helm.sh/docs/intro/install/) (for Helm deployment)
- Docker registry access (to push your bot image)

## Building and Pushing the Container Image

### 1. Build the Docker Image

```bash
# Build the image
docker build -t watchman-discord-bot:latest .

# Tag for your registry
docker tag watchman-discord-bot:latest your-registry.com/watchman-discord-bot:latest

# Push to registry
docker push your-registry.com/watchman-discord-bot:latest
```

### 2. Update Image References

Update the image references in your deployment files:

**For Helm:** Edit `helm/watchman/values.yaml`:
```yaml
image:
  repository: your-registry.com/watchman-discord-bot
  tag: "latest"
```

**For Raw Manifests:** Edit `k8s/deployment.yaml`:
```yaml
spec:
  template:
    spec:
      containers:
      - name: watchman
        image: your-registry.com/watchman-discord-bot:latest
```

## Option 1: Helm Chart Deployment (Recommended)

### 1. Create Secrets

First, create the secrets with your actual values:

```bash
helm install watchman ./helm/watchman \
  --set secrets.discordToken="YOUR_DISCORD_BOT_TOKEN" \
  --set secrets.apiSecretKey="YOUR_API_SECRET_KEY" \
  --set secrets.newsChannelId="YOUR_NEWS_CHANNEL_ID" \
  --set secrets.statusChannelId="YOUR_STATUS_CHANNEL_ID" \
  --set image.repository="your-registry.com/watchman-discord-bot" \
  --set image.tag="latest"
```

### 2. Or Use a Values File

Create a custom values file (`values-prod.yaml`):

```yaml
image:
  repository: your-registry.com/watchman-discord-bot
  tag: "latest"

secrets:
  create: true
  discordToken: "YOUR_DISCORD_BOT_TOKEN"
  apiSecretKey: "YOUR_API_SECRET_KEY"
  newsChannelId: "YOUR_NEWS_CHANNEL_ID"
  statusChannelId: "YOUR_STATUS_CHANNEL_ID"
  discordGuildId: "YOUR_GUILD_ID"

resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi

persistence:
  enabled: true
  size: 2Gi

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: watchman.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
```

Then deploy:

```bash
helm install watchman ./helm/watchman -f values-prod.yaml
```

### 3. Helm Commands

```bash
# Install
helm install watchman ./helm/watchman

# Upgrade
helm upgrade watchman ./helm/watchman

# Check status
helm status watchman

# View values
helm get values watchman

# Uninstall
helm uninstall watchman
```

## Option 2: Raw Kubernetes Manifests

### 1. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Create Secrets

**Method A: Using kubectl (recommended):**

```bash
kubectl create secret generic watchman-secrets \
  --namespace=watchman \
  --from-literal=discord-token="YOUR_DISCORD_BOT_TOKEN" \
  --from-literal=api-secret-key="YOUR_API_SECRET_KEY" \
  --from-literal=news-channel-id="YOUR_NEWS_CHANNEL_ID" \
  --from-literal=status-channel-id="YOUR_STATUS_CHANNEL_ID" \
  --from-literal=discord-guild-id="YOUR_GUILD_ID"
```

**Method B: Using YAML file:**

1. Copy the example secret file:
   ```bash
   cp k8s/secret-example.yaml k8s/secret.yaml
   ```

2. Edit `k8s/secret.yaml` with base64 encoded values:
   ```bash
   echo -n "YOUR_DISCORD_TOKEN" | base64
   echo -n "YOUR_API_SECRET_KEY" | base64
   ```

3. Apply the secret:
   ```bash
   kubectl apply -f k8s/secret.yaml
   ```

### 3. Deploy All Resources

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or apply individually
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/deployment.yaml
```

## Monitoring and Management

### Check Deployment Status

```bash
# Check pods
kubectl get pods -n watchman

# Check services
kubectl get services -n watchman

# Check logs
kubectl logs -n watchman deployment/watchman -f

# Check events
kubectl get events -n watchman --sort-by='.lastTimestamp'
```

### Scaling

```bash
# Scale replicas (Helm)
helm upgrade watchman ./helm/watchman --set replicaCount=2

# Scale replicas (kubectl)
kubectl scale deployment watchman -n watchman --replicas=2
```

### Health Checks

The bot exposes a health endpoint at `/health`. You can test it:

```bash
# Port forward to test locally
kubectl port-forward -n watchman service/watchman 8080:8080

# Test health endpoint
curl http://localhost:8080/health
```

## Configuration Options

### Environment Variables

Key environment variables that can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Discord bot token | Required |
| `API_SECRET_KEY` | API authentication key | Required |
| `NEWS_CHANNEL_ID` | Discord channel for news | Optional |
| `STATUS_CHANNEL_ID` | Discord channel for status | Optional |
| `NEWS_CHECK_INTERVAL` | News check interval (seconds) | 3600 |
| `MONITOR_INTERVAL` | System monitor interval (seconds) | 300 |
| `LOG_LEVEL` | Logging level | INFO |

### Resource Requirements

**Minimum:**
- CPU: 100m
- Memory: 128Mi
- Storage: 1Gi

**Recommended:**
- CPU: 200m
- Memory: 256Mi
- Storage: 2Gi

**Production:**
- CPU: 500m
- Memory: 512Mi
- Storage: 5Gi

## Troubleshooting

### Common Issues

1. **Pod not starting:**
   ```bash
   kubectl describe pod -n watchman <pod-name>
   kubectl logs -n watchman <pod-name>
   ```

2. **Secret not found:**
   ```bash
   kubectl get secrets -n watchman
   kubectl describe secret watchman-secrets -n watchman
   ```

3. **Persistent volume issues:**
   ```bash
   kubectl get pvc -n watchman
   kubectl describe pvc -n watchman
   ```

4. **Network connectivity:**
   ```bash
   kubectl get svc -n watchman
   kubectl get endpoints -n watchman
   ```

### Debug Commands

```bash
# Interactive shell in pod
kubectl exec -it -n watchman deployment/watchman -- /bin/bash

# Check environment variables
kubectl exec -n watchman deployment/watchman -- env

# Test network connectivity
kubectl exec -n watchman deployment/watchman -- curl http://localhost:8080/health
```

## Security Considerations

1. **Secrets Management:**
   - Never commit real secrets to Git
   - Use external secret management (HashiCorp Vault, AWS Secrets Manager, etc.)
   - Rotate secrets regularly

2. **Network Policies:**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: watchman-netpol
     namespace: watchman
   spec:
     podSelector:
       matchLabels:
         app: watchman
     policyTypes:
     - Ingress
     - Egress
     egress:
     - to: []
       ports:
       - protocol: TCP
         port: 443  # HTTPS
       - protocol: TCP
         port: 53   # DNS
       - protocol: UDP
         port: 53   # DNS
   ```

3. **Pod Security:**
   - Run as non-root user (already configured)
   - Drop all capabilities (already configured)
   - Use read-only root filesystem where possible

## Backup and Disaster Recovery

### Database Backup

```bash
# Create backup job
kubectl create job --from=cronjob/watchman-backup manual-backup-$(date +%Y%m%d-%H%M%S) -n watchman

# Copy database file
kubectl cp watchman/<pod-name>:/app/data/bot_data.db ./backup-$(date +%Y%m%d).db -n watchman
```

### Configuration Backup

```bash
# Export all configurations
kubectl get all,secrets,configmaps,pvc -n watchman -o yaml > watchman-backup.yaml
```

## Updates and Rollbacks

### Rolling Updates

```bash
# Update image (Helm)
helm upgrade watchman ./helm/watchman --set image.tag=v1.1.0

# Update image (kubectl)
kubectl set image deployment/watchman watchman=your-registry.com/watchman-discord-bot:v1.1.0 -n watchman
```

### Rollbacks

```bash
# Rollback (Helm)
helm rollback watchman 1

# Rollback (kubectl)
kubectl rollout undo deployment/watchman -n watchman

# Check rollout status
kubectl rollout status deployment/watchman -n watchman
```

## Production Checklist

- [ ] Container image pushed to production registry
- [ ] Secrets created and verified
- [ ] Resource limits configured appropriately
- [ ] Persistent volumes configured with appropriate storage class
- [ ] Monitoring and alerting configured
- [ ] Network policies applied (if required)
- [ ] Backup strategy implemented
- [ ] Health checks responding correctly
- [ ] Discord bot permissions verified
- [ ] API endpoints accessible (if exposing externally)
- [ ] Logging aggregation configured
