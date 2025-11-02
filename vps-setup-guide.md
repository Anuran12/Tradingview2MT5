# 🚀 Complete VPS Setup Guide: TradingView to MT5 Automated System

**Hostinger VPS + Ubuntu + NoMachine GUI + TradingView + n8n + MT5**

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- ✅ **Hostinger VPS** with Ubuntu (at least 2GB RAM, 2 vCPUs recommended)
- ✅ **TradingView Premium Account** (for webhook alerts)
- ✅ **MetaTrader 5 Account** (demo or live)
- ✅ **Domain/Static IP** (for consistent webhook URLs)
- ✅ **SSH Access** to your VPS

---

## 🧹 **CLEAN RESTART: Wipe Everything and Start Fresh**

If you want to start over completely (recommended if having issues):

### **⚠️ WARNING: This will delete everything on your VPS**

```bash
# BACKUP ANY IMPORTANT DATA FIRST (if any exists)

# Complete system reset (run as root)
sudo rm -rf /home/*
sudo rm -rf /opt/*
sudo rm -rf /var/lib/docker
sudo apt purge -y docker* nomachine* wine* xfce4* lightdm*
sudo apt autoremove -y
sudo apt autoclean

# Reset firewall
sudo ufw --force reset
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 4000:4100/tcp  # NoMachine port range

# Reboot to clean state
sudo reboot
```

### **After Reboot: Fresh Start with GUI Priority**

---

## 🎯 **NEW ORDER: GUI First, Then Everything Else**

**Recommended sequence for smooth setup:**

1. ✅ **Basic VPS setup** (repositories, tools)
2. 🎯 **NoMachine GUI setup** (FIRST PRIORITY)
3. 🐳 **Docker & Trading System**
4. 📊 **MT5 Installation** (through GUI)
5. ⚙️ **Configuration & Testing**

---

## 🎯 Phase 1: VPS Basic Setup

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

# Allow NoMachine ports (FIRST PRIORITY)
sudo ufw allow 4000:4100/tcp

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

# If user already exists (from previous attempts), skip creation and just configure
# sudo usermod -aG sudo trading  # Add to sudo group
# su - trading                  # Switch to user

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

**If you see "user 'trading' already exists":**

- The user was created in a previous attempt
- Just run: `sudo usermod -aG sudo trading && su - trading`
- Then configure sudo with `sudo visudo`

**Alternative: Stay as root (not recommended)**
If you prefer to skip this step, you can continue as root, but you'll need to adjust file permissions later.

**If you create the trading user:**

- All subsequent commands should be run as the `trading` user
- Docker commands will work the same
- File ownership will be correct for the trading user

---

## 🖥️ **Phase 2: NoMachine GUI Setup (FIRST PRIORITY)**

### **Why GUI First?**

- MT5 installation requires GUI access
- Wine setup and testing needs GUI
- Much easier to troubleshoot with visual interface

### Step 2.1: Install NoMachine Server

```bash
# Clean up any Wine repository issues first (if you see Wine errors)
sudo rm -f /etc/apt/sources.list.d/wine*
sudo rm -f /etc/apt/keyrings/wine*

# Update system first
sudo apt update && sudo apt upgrade -y

# Download latest NoMachine for Ubuntu (working URL)
wget https://www.nomachine.com/free/linux/64/deb -O nomachine.deb

# Alternative working URL if the above doesn't work:
# wget https://download.nomachine.com/download/8.10/Linux/nomachine_8.10.1_1_amd64.deb -O nomachine.deb

# Install NoMachine
sudo dpkg -i nomachine.deb

# Fix any dependencies
sudo apt install -f -y

# Clean up
rm nomachine.deb
```

### Step 2.2: Install Desktop Environment

**Choose Your Desktop Environment:**

#### **Option A: XFCE (Lightweight - Recommended for VPS)**

```bash
# Install lightweight XFCE desktop
sudo apt install -y xfce4 xfce4-goodies xfce4-terminal

# Install display manager
sudo apt install -y lightdm lightdm-gtk-greeter

# Install additional GUI tools
sudo apt install -y firefox mousepad xarchiver
```

#### **Option B: MATE (Traditional GNOME-like, Very Stable)**

```bash
# Install MATE desktop (more familiar interface)
sudo apt install -y ubuntu-mate-desktop^

# Or minimal MATE
sudo apt install -y mate-desktop-environment mate-terminal
sudo apt install -y lightdm firefox mousepad
```

#### **Option C: Cinnamon (Modern, Feature-Rich)**

```bash
# Install Cinnamon desktop
sudo apt install -y cinnamon-desktop-environment
sudo apt install -y lightdm firefox mousepad
```

#### **Option D: KDE Plasma (Full-Featured, Modern)**

```bash
# Install KDE Plasma
sudo apt install -y kubuntu-desktop^
# OR for minimal KDE:
sudo apt install -y plasma-desktop sddm firefox konsole
```

#### **Option E: GNOME (Full Ubuntu Experience)**

```bash
# Install full GNOME desktop
sudo apt install -y ubuntu-gnome-desktop^

# Or minimal GNOME
sudo apt install -y gnome-session gdm3 firefox gnome-terminal
```

## 🎯 **Recommendations:**

- **For VPS (2-4GB RAM):** XFCE or MATE (lightweight)
- **For VPS (4GB+ RAM):** Cinnamon or KDE Plasma
- **For Best Experience:** MATE (stable, familiar, lightweight)

**My Recommendation: Use MATE** - it's stable, looks professional, and works great for remote desktop trading.

```bash
# Best choice for trading VPS
sudo apt install -y ubuntu-mate-desktop^
sudo apt install -y firefox mousepad
```

### Step 2.3: Configure Desktop Environment

**Configuration depends on your chosen desktop:**

#### **For MATE:**

```bash
# Set MATE as default desktop
sudo update-alternatives --config x-session-manager

# Create desktop configuration
sudo mkdir -p /home/trading/.config/mate
sudo chown -R trading:trading /home/trading/.config

# Set MATE session
echo "mate-session" > /home/trading/.xsession
sudo chown trading:trading /home/trading/.xsession
```

### Step 2.4: Start Services and Test

```bash
# Start display manager
sudo systemctl start lightdm
sudo systemctl enable lightdm

# Check NoMachine status
sudo systemctl status nxserver

# Get your VPS IP for NoMachine connection
curl -s ifconfig.me
```

### Step 2.5: Connect via NoMachine

**On your local machine:**

1. **Download NoMachine client** from https://www.nomachine.com/download
2. **Install and open** NoMachine
3. **Create new connection:**
   - **Host:** `YOUR_VPS_IP`
   - **Login:** `trading` (or `root` if no trading user yet)
   - **Password:** your user password
4. **Connect** - you should see the XFCE desktop

### Step 2.6: Test GUI Functionality

**In NoMachine GUI:**

1. **Open Terminal** - Applications → System → Terminal
2. **Open Firefox** - Applications → Internet → Firefox
3. **Test GUI responsiveness**

**Expected Result:** Full Ubuntu desktop with XFCE environment

---

## 🐳 Phase 3: Docker Installation

### Step 3.1: Install Docker

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

### Step 3.2: Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
docker --version
```

### Step 3.3: Test Docker Installation

```bash
# Test Docker
sudo docker run hello-world

# Test Docker Compose
sudo docker-compose --version
```

---

## 📁 Phase 4: Trading System Setup

### Step 4.1: Download Project Files

```bash
# Navigate to home directory
cd ~

# Clone the trading system (replace with actual repo URL)
git clone https://github.com/yourusername/Tradingview2MT5.git
cd Tradingview2MT5

# Make deployment script executable
chmod +x deploy.sh
```

### Step 4.2: Configure Environment Variables

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

**⚠️ IMPORTANT: MT5 Installation Requires GUI Access**

MT5 requires a graphical desktop environment to install and run. You cannot install it through a terminal-only connection.

#### **Option A: Use NoMachine (Recommended)**

1. **Install NoMachine on your VPS:**

```bash
# Go to home directory (where you can write files)
cd ~

# Download NoMachine for Ubuntu (use the correct URL)
wget https://www.nomachine.com/free/linux/64/deb -O nomachine.deb

# Alternative: Direct download with correct version
# wget https://download.nomachine.com/download/8.10/Linux/nomachine_8.10.1_1_amd64.deb

# Install it
sudo dpkg -i nomachine.deb

# Fix any dependencies
sudo apt install -f -y

# Clean up
rm nomachine.deb
```

2. **Install Desktop Environment:**

```bash
# Install lightweight desktop
sudo apt install -y xfce4 xfce4-goodies

# Install display manager
sudo apt install -y lightdm

# Set default desktop
echo "/usr/bin/xfce4-session" > ~/.xsession
```

3. **Configure NoMachine:**

- Connect using NoMachine client on your local machine
- Use VPS IP, username: `trading`, password: your trading user password
- Install MT5 through the graphical interface

#### **Option B: Use X11 Forwarding (Alternative)**

```bash
# On your local machine (Windows/Mac/Linux):
ssh -X trading@YOUR_VPS_IP

# Then try Wine commands
# (May still have issues with display)
```

#### **MT5 Installation Steps (Once You Have GUI Access):**

```bash
# Create MT5 directory and set permissions
sudo mkdir -p /opt/mt5
sudo chown trading:trading /opt/mt5
cd /opt/mt5

# Download MT5 (correct URL - note the dot, not comma)
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# Install Wine dependencies (complete reinstall if needed)
sudo dpkg --add-architecture i386
sudo apt update

# If Wine is broken, remove and reinstall
sudo apt remove --purge wine* -y
sudo apt autoremove -y
sudo apt install -y wine winetricks wine32:i386

# Verify Wine installation
wine --version

# Initialize Wine for 32-bit (MT5 requires 32-bit)
# Remove existing 64-bit prefix if it exists
rm -rf ~/.wine

# Create 32-bit Wine prefix
WINEARCH=win32 WINEPREFIX=~/.wine winecfg

# Accept the Wine configuration wizard
# This creates the necessary 32-bit Wine environment

# Alternative: Use wine32 directly
# wine32 winecfg

# Now run MT5 setup
wine mt5setup.exe

# Follow the installation wizard
# Install to C:\Program Files\MetaTrader 5 (default)
# The actual files will be in ~/.wine/drive_c/Program Files/MetaTrader 5

# If you get "Bad EXE format" error:
# 1. The direct download is being blocked/filtered
# 2. Use browser download method instead (see below)
# 3. Download from official MetaTrader website through GUI

#### **BEST METHOD: Browser Download (Most Reliable)**

Since direct downloads are failing, use your NoMachine GUI:

1. **Open Firefox/Chrome** in NoMachine
2. **Go to:** https://www.metatrader5.com/en/download
3. **Click "Download MetaTrader 5"** for Windows version
4. **Save the file** to your `/opt/mt5/` directory
5. **Run:** `wine /opt/mt5/mt5setup.exe`

**Expected file size:** 100-150 MB (not 23MB like the corrupted downloads)
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

## 🚀 Phase 5: Deploy Trading System

### Step 5.1: Build and Start Services

**⚠️ IMPORTANT: Configure MT5 credentials first!**

Before running Docker, make sure your MT5 credentials are configured:

```bash
# Edit the MT5 bridge environment file
nano mt5-bridge/.env

# Fill in your MT5 details (get these from your broker):
# MT5_LOGIN=your_account_number
# MT5_PASSWORD=your_password
# MT5_SERVER=your_broker_server
# MT5_PATH=/opt/mt5
```

**Then start the services:**

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

**Note:** The MT5 bridge will show warnings about MT5 not being available until you install MT5 on the host system via NoMachine GUI.

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

## 🎯 Phase 6: TradingView Configuration

### Step 6.1: Prepare Pine Script Strategy

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

### Step 6.2: Add Strategy to TradingView

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

### Step 6.3: Create TradingView Alerts

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

## 🔧 Phase 7: System Testing

### Step 7.1: Run System Tests

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

## 🌐 Phase 8: Production Setup

### Step 8.1: Install Nginx (Reverse Proxy)

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

## 🔄 Phase 9: Backup & Recovery

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

## 🚨 Phase 10: Troubleshooting

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

## 📊 Phase 11: Final Verification

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
