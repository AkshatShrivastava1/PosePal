#!/bin/bash

# AWS EC2 Deployment Script for PosePal Backend
# This script sets up the backend on an EC2 instance

set -e

echo "🚀 Starting PosePal Backend Deployment on AWS EC2..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python and pip (for local development/testing)
echo "🐍 Installing Python..."
sudo apt install -y python3 python3-pip python3-venv

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/posepal-backend
sudo chown $USER:$USER /opt/posepal-backend
cd /opt/posepal-backend

# Clone or copy your application files here
echo "📋 Please copy your backend files to /opt/posepal-backend"
echo "   You can use scp, git clone, or any other method"

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Database
DATABASE_URL=sqlite:///./trainer.db

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# CORS Origins (add your frontend domain)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175,https://your-frontend-domain.com

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Create systemd service for the application
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/posepal-backend.service > /dev/null << EOF
[Unit]
Description=PosePal Backend API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/posepal-backend
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable posepal-backend.service

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # Backend API
sudo ufw --force enable

# Create startup script
echo "📝 Creating startup script..."
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd /opt/posepal-backend
docker-compose up -d
echo "Backend started! Check status with: docker-compose ps"
EOF

chmod +x start-backend.sh

# Create stop script
cat > stop-backend.sh << 'EOF'
#!/bin/bash
cd /opt/posepal-backend
docker-compose down
echo "Backend stopped!"
EOF

chmod +x stop-backend.sh

echo "✅ Deployment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your backend files to /opt/posepal-backend"
echo "2. Update the .env file with your actual API keys"
echo "3. Run: ./start-backend.sh"
echo "4. Check status: docker-compose ps"
echo "5. View logs: docker-compose logs -f"
echo ""
echo "🌐 Your API will be available at: http://your-ec2-ip:8000"
echo "📊 API docs: http://your-ec2-ip:8000/docs"
