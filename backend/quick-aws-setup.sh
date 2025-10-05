#!/bin/bash

# Quick AWS EC2 Setup Script for PosePal Backend
# Run this script on your EC2 instance after connecting via SSH

set -e

echo "🚀 Quick PosePal Backend Setup on AWS EC2"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Use a regular user with sudo access."
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Install additional tools
echo "🔧 Installing additional tools..."
sudo apt install -y curl wget git htop

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/posepal-backend
sudo chown $USER:$USER /opt/posepal-backend

# Navigate to application directory
cd /opt/posepal-backend

# Create basic environment file
echo "⚙️ Creating environment configuration..."
cat > .env << 'EOF'
# Database
DATABASE_URL=sqlite:///./trainer.db

# Gemini API (REPLACE WITH YOUR ACTUAL KEY)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# CORS Origins (ADD YOUR FRONTEND DOMAINS)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:5175

# Security (GENERATE A SECURE SECRET KEY)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Create startup script
echo "📝 Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
cd /opt/posepal-backend
echo "🚀 Starting PosePal Backend..."
docker-compose up -d
echo "✅ Backend started!"
echo "🌐 API available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "📊 API docs: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
echo "🔍 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f"
EOF

chmod +x start.sh

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash
cd /opt/posepal-backend
echo "🛑 Stopping PosePal Backend..."
docker-compose down
echo "✅ Backend stopped!"
EOF

chmod +x stop.sh

# Create restart script
cat > restart.sh << 'EOF'
#!/bin/bash
cd /opt/posepal-backend
echo "🔄 Restarting PosePal Backend..."
docker-compose down
docker-compose up -d
echo "✅ Backend restarted!"
EOF

chmod +x restart.sh

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your backend files to /opt/posepal-backend/"
echo "2. Update the .env file with your actual API keys"
echo "3. Run: ./start.sh"
echo ""
echo "📁 Files created:"
echo "   - /opt/posepal-backend/.env (environment config)"
echo "   - /opt/posepal-backend/start.sh (start backend)"
echo "   - /opt/posepal-backend/stop.sh (stop backend)"
echo "   - /opt/posepal-backend/restart.sh (restart backend)"
echo ""
echo "🌐 Your EC2 Public IP: $PUBLIC_IP"
echo "🔗 API will be available at: http://$PUBLIC_IP:8000"
echo "📊 API docs: http://$PUBLIC_IP:8000/docs"
echo ""
echo "💡 To copy files from your local machine:"
echo "   scp -r -i your-key.pem ./backend/* ubuntu@$PUBLIC_IP:/opt/posepal-backend/"
