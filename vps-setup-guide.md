# 🚀 Complete VPS Setup Guide: TradingView to MT5 Automated System

**Hostinger VPS + Ubuntu + TradingView + n8n + MT5**

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- ✅ **Hostinger VPS** with Ubuntu (at least 2GB RAM, 2 vCPUs recommended)
- ✅ **TradingView Premium Account** (for webhook alerts)
- ✅ **MetaTrader 5 Account** (demo or live)
- ✅ **Domain/Static IP** (for consistent webhook URLs)
- ✅ **SSH Access** to your VPS

---

## 🎯 Phase 1: VPS Initial Setup

### Step 1.1: Connect to Your VPS

```bash
# Connect via SSH (replace with your VPS IP)
ssh root@YOUR_VPS_IP

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### Step 1.2: Install Essential Tools

```bash
# Update system packages (now with fixed repositories)
sudo apt update && sudo apt upgrade -y

# Install basic tools
sudo apt install -y curl wget git nano htop unzip software-properties-common

# Install Python3 and pip
sudo apt install -y python3 python3-pip python3-dev

# Verify installations
python3 --version
pip3 --version
```

### Step 1.3: Configure Firewall (UFW)

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (important!)
sudo ufw allow ssh
sudo ufw allow 22

# Allow required ports for trading system
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5678  # n8n
sudo ufw allow 5000  # MT5 Bridge

# Check status
sudo ufw status
```

### Step 1.4: Create Trading User (Security Best Practice)

**Is this step necessary?** Yes, highly recommended for security. Running everything as root increases security risks.

**Why create a dedicated user?**

- Security: Limits damage if compromised
- Isolation: Trading operations separate from system admin
- Best practice: Never run applications as root

```bash
# Create the trading user (interactive - you'll be prompted for password)
sudo adduser trading

# Add trading user to sudo group for admin privileges
sudo usermod -aG sudo trading

# Switch to trading user for all subsequent operations
su - trading

# Configure passwordless sudo for trading user (optional but convenient)
sudo visudo

# In the editor, add this line at the end:
# trading ALL=(ALL) NOPASSWD: ALL

# Save and exit (Ctrl+X, then Y, then Enter in nano)

# Verify you're now the trading user
whoami  # Should show "trading"

# Test sudo access
sudo whoami  # Should show "root" without password prompt
```

**Alternative: Stay as root (not recommended)**
If you prefer to skip this step, you can continue as root, but you'll need to adjust file permissions later.

**If you create the trading user:**

- All subsequent commands should be run as the `trading` user
- Docker commands will work the same
- File ownership will be correct for the trading user

---

## 🐳 Phase 2: Docker Installation

### Step 2.1: Install Docker

```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add trading user to docker group
sudo usermod -aG docker trading
```

### Step 2.2: Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
docker --version
```

### Step 2.3: Test Docker Installation

```bash
# Test Docker
sudo docker run hello-world

# Test Docker Compose
sudo docker-compose --version
```

---

## 📁 Phase 3: Trading System Setup

### Step 3.1: Download Project Files

```bash
# Navigate to home directory
cd ~

# Clone the trading system (replace with actual repo URL)
git clone https://github.com/yourusername/Tradingview2MT5.git
cd Tradingview2MT5

# Make deployment script executable
chmod +x deploy.sh
```

### Step 3.2: Configure Environment Variables

```bash
# Copy environment template
cp mt5-bridge/.env.example mt5-bridge/.env

# Edit with your MT5 credentials
nano mt5-bridge/.env
```

**Fill in your MT5 details:**

```env
# MetaTrader 5 Configuration
MT5_LOGIN=12345678          # Your MT5 account number
MT5_PASSWORD=your_password  # Your MT5 password
MT5_SERVER=YourBroker-Server  # Your broker's server (e.g., ICMarkets-Demo)
MT5_PATH=/opt/mt5

# Trading Parameters
TRADING_SYMBOL=EURUSD
LOT_SIZE=0.01
MAGIC_NUMBER=123456

# Bridge Service
BRIDGE_PORT=5000
LOG_LEVEL=INFO
```

### Step 3.3: Download and Install MetaTrader 5

```bash
# Create MT5 directory
sudo mkdir -p /opt/mt5
cd /opt/mt5

# Download MT5 for Linux
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# Note: MT5 for Linux requires Wine. Let's install Wine first
sudo apt install -y wine winetricks

# Initialize Wine for MT5
wine mt5setup.exe

# Follow the installation wizard
# Install MT5 in /opt/mt5 directory
```

### Step 3.4: Configure MT5 for API Access

1. **Launch MT5 Terminal:**

```bash
cd /opt/mt5
wine terminal64.exe &
```

2. **Login to Your Account:**

   - Open MT5 terminal
   - File → Login to Trade Account
   - Enter your credentials

3. **Enable Algo Trading:**

   - Tools → Options → Expert Advisors
   - Check "Allow automated trading"
   - Check "Allow DLL imports"
   - Check "Allow external experts to import functions"

4. **Test Connection:**
   - Verify you can see live prices
   - Check account balance

---

## 🚀 Phase 4: Deploy Trading System

### Step 4.1: Build and Start Services

```bash
# Make sure you're in the project directory
cd ~/Tradingview2MT5

# Build and start all services
sudo docker-compose up -d --build

# Check if services are running
sudo docker-compose ps

# View logs to check for errors
sudo docker-compose logs -f
```

### Step 4.2: Verify Services Health

```bash
# Check n8n is running
curl -f http://localhost:5678/healthz

# Check MT5 Bridge is running
curl -f http://localhost:5000/health

# Check all containers
sudo docker ps
```

### Step 4.3: Setup n8n Workflow

1. **Access n8n Web Interface:**

   - Open browser: `http://YOUR_VPS_IP:5678`
   - Create admin account

2. **Import Workflow:**

   - Go to "Workflows" → "Import from File"
   - Upload: `n8n-workflows/tradingview-to-mt5-workflow.json`
   - Click "Import"

3. **Configure Webhook:**

   - Open the imported workflow
   - Click on the "Webhook Receiver" node
   - Copy the webhook URL (should look like: `http://YOUR_VPS_IP:5678/webhook/tradingview-webhook`)

4. **Activate Workflow:**
   - Click "Activate" button (top right)
   - Workflow should show as "Active"

---

## 🎯 Phase 5: TradingView Configuration

### Step 5.1: Prepare Pine Script Strategy

The strategy file is already updated: `tradingview/moving-averages-strategy.pine`

**Key Parameters to Configure:**

- `period1`: 20 (Fast MA)
- `period2`: 50 (Slow MA)
- `maType1`: SMA (Fast MA type)
- `maType2`: EMA (Slow MA type)
- `takeProfitPercent`: 2.0
- `stopLossPercent`: 1.0
- `lotSize`: 0.01
- `symbol`: EURUSD

### Step 5.2: Add Strategy to TradingView

1. **Open TradingView:**

   - Go to `www.tradingview.com`
   - Open any chart (EUR/USD recommended)

2. **Add Strategy:**

   - Click "Pine Editor" (bottom panel)
   - Paste the entire content from `tradingview/moving-averages-strategy.pine`
   - Click "Save"
   - Click "Add to Chart"

3. **Configure Strategy:**
   - Click the strategy name on chart
   - Adjust parameters as needed
   - Ensure it's showing BUY/SELL signals

### Step 5.3: Create TradingView Alerts

1. **Create BUY Alert:**

   - Click "Alert" button (bell icon) on chart
   - Condition: "Long Signal"
   - Webhook URL: `http://YOUR_VPS_IP:5678/webhook/tradingview-webhook`
   - Message: Leave empty (strategy generates JSON)
   - Frequency: "Once per bar"

2. **Create SELL Alert:**

   - Same process but for "Short Signal"

3. **Test Alerts:**
   - Click "Test Alert" to verify webhook delivery
   - Check n8n logs for incoming signals

---

## 🔧 Phase 6: System Testing

### Step 6.1: Run System Tests

```bash
# Run the test script
cd ~/Tradingview2MT5
python3 test-system.py
```

### Step 6.2: Manual Testing

**Test MT5 Bridge API:**

```bash
# Check account info
curl http://localhost:5000/account

# Check positions
curl http://localhost:5000/positions

# Check symbol info
curl http://localhost:5000/symbol/EURUSD
```

**Test Webhook Flow:**

```bash
# Send test webhook
curl -X POST http://localhost:5000/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{
    "signal": "BUY",
    "symbol": "EURUSD",
    "lot_size": 0.01,
    "sl_percent": 1.0,
    "tp_percent": 2.0
  }'
```

### Step 6.3: Monitor Logs

```bash
# Monitor all logs
sudo docker-compose logs -f

# Monitor specific services
sudo docker-compose logs -f n8n
sudo docker-compose logs -f mt5-bridge
```

---

## 🌐 Phase 7: Production Setup

### Step 7.1: Install Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration for n8n
sudo nano /etc/nginx/sites-available/trading-system
```

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    # n8n
    location /n8n/ {
        proxy_pass http://localhost:5678/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MT5 Bridge (protected)
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/trading-system /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 7.2: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

### Step 7.3: Setup Auto-Restart

```bash
# Create systemd service for trading system
sudo nano /etc/systemd/system/trading-system.service
```

```ini
[Unit]
Description=TradingView to MT5 System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=trading
WorkingDirectory=/home/trading/Tradingview2MT5
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable trading-system
sudo systemctl start trading-system
```

### Step 7.4: Monitoring Setup

```bash
# Install monitoring tools
sudo apt install -y htop iotop ncdu

# Setup log rotation
sudo nano /etc/logrotate.d/trading-system
```

```
/home/trading/Tradingview2MT5/mt5-bridge/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 trading trading
}
```

---

## 🔄 Phase 8: Backup & Recovery

### Step 8.1: Automated Backups

```bash
# Create backup script
nano ~/backup-trading-system.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/trading/backups/$(date +%Y%m%d_%H%M%S)"
PROJECT_DIR="/home/trading/Tradingview2MT5"

mkdir -p "$BACKUP_DIR"

# Backup n8n data
docker run --rm -v tradingview-n8n:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/n8n-data.tar.gz -C /data .

# Backup MT5 bridge logs
cp -r "$PROJECT_DIR/mt5-bridge/logs" "$BACKUP_DIR/"

# Backup configuration
cp "$PROJECT_DIR/docker-compose.yml" "$BACKUP_DIR/"
cp "$PROJECT_DIR/mt5-bridge/.env" "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
```

```bash
# Make executable and test
chmod +x ~/backup-trading-system.sh
~/backup-trading-system.sh
```

### Step 8.2: Setup Cron Jobs

```bash
# Edit crontab
crontab -e
```

**Add these lines:**

```bash
# Backup daily at 2 AM
0 2 * * * /home/trading/backup-trading-system.sh

# Health check every 5 minutes
*/5 * * * * curl -f http://localhost:5000/health > /dev/null || echo "$(date): MT5 Bridge unhealthy" >> /home/trading/health.log

# Restart services if down (every hour)
0 * * * * docker-compose -f /home/trading/Tradingview2MT5/docker-compose.yml ps | grep -q "Up" || docker-compose -f /home/trading/Tradingview2MT5/docker-compose.yml restart
```

---

## 🚨 Phase 9: Troubleshooting

### Common Issues & Solutions

**1. MT5 Connection Failed:**

```bash
# Check MT5 terminal is running
ps aux | grep mt5

# Check MT5 bridge logs
docker-compose logs mt5-bridge

# Restart MT5 bridge
docker-compose restart mt5-bridge
```

**2. Webhook Not Working:**

```bash
# Check n8n workflow status
curl http://localhost:5678/rest/workflows

# Check n8n logs
docker-compose logs n8n

# Test webhook manually
curl -X POST http://localhost:5678/webhook/tradingview-webhook -d '{"test": "data"}'
```

**3. Docker Issues:**

```bash
# Check Docker status
sudo systemctl status docker

# Check disk space
df -h

# Clean up Docker
docker system prune -f
```

**4. TradingView Alerts Not Triggering:**

- Verify strategy is added to chart
- Check alert conditions
- Confirm webhook URL is correct
- Test with "Test Alert" button

---

## 📊 Phase 10: Final Verification

### Complete System Check

```bash
#!/bin/bash
echo "🔍 Trading System Health Check"
echo "================================"

# Check services
echo "1. Docker Services:"
docker-compose ps

echo -e "\n2. Service Health:"
curl -s http://localhost:5678/healthz && echo " ✅ n8n OK" || echo " ❌ n8n FAIL"
curl -s http://localhost:5000/health && echo " ✅ MT5 Bridge OK" || echo " ❌ MT5 Bridge FAIL"

echo -e "\n3. MT5 Connection:"
curl -s http://localhost:5000/account | jq '.balance' 2>/dev/null && echo " ✅ MT5 Account OK" || echo " ❌ MT5 Account FAIL"

echo -e "\n4. Webhook Test:"
curl -s -X POST http://localhost:5678/webhook/tradingview-webhook \
  -H "Content-Type: application/json" \
  -d '{"signal":"BUY","symbol":"EURUSD","lot_size":0.01}' && echo " ✅ Webhook OK" || echo " ❌ Webhook FAIL"

echo -e "\n5. System Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
echo "RAM: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk: $(df / | tail -1 | awk '{print $5}')"

echo -e "\n✅ System check complete!"
```

### Live Testing

1. **Create a test alert in TradingView**
2. **Monitor logs:** `docker-compose logs -f`
3. **Check MT5 terminal for order execution**
4. **Verify webhook delivery in n8n**

---

## 🎉 You're Done!

Your automated trading system is now live and ready for 24/7 operation!

### Quick Reference

**Access Points:**

- **n8n Dashboard:** `http://YOUR_VPS_IP:5678`
- **MT5 Bridge API:** `http://YOUR_VPS_IP:5000`
- **System Logs:** `docker-compose logs -f`

**Management Commands:**

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# Restart services
docker-compose restart

# Backup
~/backup-trading-system.sh

# Health check
~/Tradingview2MT5/test-system.py
```

**Important Reminders:**

- ✅ Start with small lot sizes (0.01)
- ✅ Monitor account balance regularly
- ✅ Keep MT5 credentials secure
- ✅ Test system before going live
- ✅ Backup regularly

---

**⚠️ Trading Disclaimer:** This system is for educational purposes. Trading involves risk. Never risk more than you can afford to lose. Past performance doesn't guarantee future results.

Need help with any step? Check the logs and refer to the troubleshooting section!
