# AWS EC2 Deployment Guide for PosePal Backend

## Prerequisites

1. **AWS Account** with EC2 access
2. **EC2 Key Pair** for SSH access
3. **Domain name** (optional, for production)
4. **Gemini API Key** for AI analysis

## Step 1: Launch EC2 Instance

### Instance Configuration
- **AMI**: Ubuntu 22.04 LTS
- **Instance Type**: t3.medium or larger (recommended for OpenCV/MediaPipe)
- **Storage**: 20GB+ EBS volume
- **Security Group**: 
  - SSH (22) from your IP
  - HTTP (80) from anywhere
  - HTTPS (443) from anywhere
  - Custom (8000) from anywhere (for direct API access)

### Launch Commands
```bash
# Connect to your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y
```

## Step 2: Deploy Backend

### Option A: Using the Deployment Script
```bash
# Download and run the deployment script
wget https://raw.githubusercontent.com/your-repo/posepal/main/backend/aws-deploy.sh
chmod +x aws-deploy.sh
./aws-deploy.sh
```

### Option B: Manual Deployment
```bash
# Install Docker
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Create application directory
sudo mkdir -p /opt/posepal-backend
sudo chown $USER:$USER /opt/posepal-backend
cd /opt/posepal-backend

# Copy your backend files (use scp, git clone, etc.)
# scp -r -i your-key.pem ./backend/* ubuntu@your-ec2-ip:/opt/posepal-backend/
```

## Step 3: Configure Environment

Create `.env` file in `/opt/posepal-backend/`:
```bash
# Database
DATABASE_URL=sqlite:///./trainer.db

# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash

# CORS Origins (add your frontend domains)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend-domain.com

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Step 4: Start the Application

```bash
cd /opt/posepal-backend

# Start with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## Step 5: Configure Domain (Optional)

### Using Route 53
1. Create hosted zone for your domain
2. Update nameservers with your domain registrar
3. Create A record pointing to your EC2 IP

### Using CloudFlare
1. Add your domain to CloudFlare
2. Update nameservers
3. Create A record pointing to your EC2 IP

## Step 6: SSL Certificate (Optional)

### Using Let's Encrypt
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Step 7: Monitoring and Maintenance

### Health Checks
```bash
# Check application health
curl http://your-domain.com/health

# Check API documentation
curl http://your-domain.com/docs
```

### Logs
```bash
# View application logs
docker-compose logs -f posepal-backend

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Updates
```bash
# Update application
cd /opt/posepal-backend
git pull origin main  # if using git
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Step 8: Security Hardening

### Firewall Configuration
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Remove this after setting up nginx
```

### System Updates
```bash
# Set up automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Troubleshooting

### Common Issues

1. **Port 8000 not accessible**
   - Check security group settings
   - Verify firewall configuration
   - Check if application is running: `docker-compose ps`

2. **CORS errors**
   - Update CORS_ORIGINS in .env file
   - Restart application: `docker-compose restart`

3. **Gemini API errors**
   - Verify API key is correct
   - Check API quotas and limits
   - Review logs: `docker-compose logs posepal-backend`

4. **High memory usage**
   - Monitor with: `docker stats`
   - Consider upgrading instance type
   - Optimize Docker resource limits

### Performance Optimization

1. **Enable gzip compression** in nginx
2. **Set up Redis** for session storage (if needed)
3. **Use RDS** instead of SQLite for production
4. **Implement caching** for static responses

## Cost Optimization

1. **Use Spot Instances** for development
2. **Set up CloudWatch** monitoring
3. **Implement auto-scaling** if needed
4. **Use S3** for file storage instead of EBS

## Backup Strategy

```bash
# Database backup
docker-compose exec posepal-backend cp trainer.db /backup/trainer-$(date +%Y%m%d).db

# Application backup
tar -czf posepal-backup-$(date +%Y%m%d).tar.gz /opt/posepal-backend/
```

## Support

- **API Documentation**: http://your-domain.com/docs
- **Health Check**: http://your-domain.com/health
- **Logs**: `docker-compose logs -f`
- **Status**: `docker-compose ps`
