# TradingView to MT5 Automated Trading System

A fully automated trading system that integrates TradingView alerts with MetaTrader 5 (MT5) using n8n and Docker for real-time execution.

## 🚀 Features

- **Real-time execution**: Minimal latency between signal generation and trade execution
- **Docker-based**: Easy deployment and scaling
- **Webhook integration**: Seamless connection between TradingView and MT5
- **Comprehensive logging**: Full audit trail of all trading activities
- **Health monitoring**: Built-in health checks and error handling
- **24/7 operation**: Designed for continuous operation on VPS

## 🏗️ Architecture

```
TradingView → n8n Webhook → MT5 Bridge → MetaTrader 5
     ↓           ↓             ↓            ↓
  Strategy    Workflow    REST API     Live Trading
  Alerts      Processing   Service      Execution
```

## 📋 Prerequisites

- **TradingView Account** with Pine Script strategy
- **MetaTrader 5** terminal installed on your VPS
- **Docker & Docker Compose** installed
- **VPS/Server** with sufficient resources (2GB RAM minimum)
- **Stable internet connection**

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd Tradingview2MT5
```

### 2. Configure Environment Variables

```bash
# Copy and edit the environment template
cp mt5-bridge/.env.example mt5-bridge/.env

# Edit the .env file with your MT5 credentials
nano mt5-bridge/.env
```

Required environment variables:

```env
# MetaTrader 5 Configuration
MT5_LOGIN=your_mt5_login_number
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server
MT5_PATH=/opt/mt5

# Trading Parameters
TRADING_SYMBOL=EURUSD
LOT_SIZE=0.01
MAGIC_NUMBER=123456

# Bridge Service
BRIDGE_PORT=5000
LOG_LEVEL=INFO
```

### 3. Deploy with Docker

```bash
# Build and start all services
docker-compose up -d --build

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Setup n8n Workflow

1. Access n8n at `http://your-vps-ip:5678`
2. Import the workflow from `n8n-workflows/tradingview-to-mt5-workflow.json`
3. Activate the workflow
4. Copy the webhook URL for TradingView alerts

### 5. Configure TradingView

1. Open your TradingView chart
2. Add the strategy from `tradingview/moving-averages-strategy.pine`
3. Create alerts for "Long Signal" and "Short Signal"
4. Set webhook URL to: `http://your-vps-ip:5678/webhook/tradingview-webhook`
5. Set alert frequency to "Once per bar"

## 🔧 Configuration

### TradingView Strategy Parameters

| Parameter           | Description    | Default |
| ------------------- | -------------- | ------- |
| `period1`           | Fast MA period | 20      |
| `period2`           | Slow MA period | 50      |
| `maType1`           | Fast MA type   | SMA     |
| `maType2`           | Slow MA type   | EMA     |
| `takeProfitPercent` | TP percentage  | 2.0%    |
| `stopLossPercent`   | SL percentage  | 1.0%    |
| `lotSize`           | Position size  | 0.01    |
| `symbol`            | Trading symbol | EURUSD  |

### Supported Moving Averages

- **SMA**: Simple Moving Average
- **EMA**: Exponential Moving Average
- **TEMA**: Triple Exponential Moving Average
- **HMA**: Hull Moving Average
- **KAMA**: Kaufman's Adaptive Moving Average
- **ALMA**: Arnaud Legoux Moving Average
- **FRAMA**: Fractal Adaptive Moving Average
- **VIDYA**: Variable Index Dynamic Average

## 📊 Monitoring & Health Checks

### Service Health

```bash
# Check all services
curl http://localhost:5678/healthz  # n8n
curl http://localhost:5000/health   # MT5 Bridge
```

### View Logs

```bash
# n8n logs
docker-compose logs -f n8n

# MT5 Bridge logs
docker-compose logs -f mt5-bridge

# All logs
docker-compose logs -f
```

### Trading Activity

```bash
# Check current positions
curl http://localhost:5000/positions

# Check account info
curl http://localhost:5000/account

# Check symbol info
curl http://localhost:5000/symbol/EURUSD
```

## 🔄 API Endpoints

### MT5 Bridge Service (Port 5000)

| Endpoint               | Method | Description                 |
| ---------------------- | ------ | --------------------------- |
| `/health`              | GET    | Service health check        |
| `/webhook/tradingview` | POST   | Receive TradingView signals |
| `/positions`           | GET    | Get current positions       |
| `/account`             | GET    | Get account information     |
| `/symbol/<symbol>`     | GET    | Get symbol information      |

### TradingView Webhook Payload

```json
{
  "signal": "BUY|SELL",
  "symbol": "EURUSD",
  "lot_size": 0.01,
  "sl_percent": 1.0,
  "tp_percent": 2.0,
  "timestamp": "2023-10-30T12:00:00Z"
}
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. MT5 Connection Failed

```bash
# Check MT5 terminal is running
# Verify credentials in .env file
# Check MT5 server connectivity
docker-compose logs mt5-bridge
```

#### 2. Webhook Not Receiving Signals

```bash
# Verify n8n workflow is active
# Check webhook URL in TradingView alert
# Check n8n logs for incoming requests
docker-compose logs n8n
```

#### 3. Docker Services Not Starting

```bash
# Check Docker resources
docker system df

# Rebuild services
docker-compose down
docker-compose up -d --build
```

#### 4. TradingView Alert Not Triggering

- Ensure strategy is added to chart
- Check alert conditions match strategy signals
- Verify webhook URL is correct
- Test alert with "Test Alert" button

### Logs Location

- **n8n logs**: `docker-compose logs n8n`
- **MT5 Bridge logs**: `mt5-bridge/logs/mt5_bridge.log`
- **System logs**: `docker-compose logs`

## 🔒 Security Considerations

1. **Network Security**:

   - Use firewall to restrict access to ports 5678, 5000
   - Consider using VPN for remote access

2. **API Security**:

   - Keep MT5 credentials secure
   - Use strong passwords
   - Regularly rotate API keys if used

3. **Trading Security**:
   - Start with small lot sizes for testing
   - Implement proper risk management
   - Monitor account balance regularly

## 📈 Performance Optimization

### VPS Requirements

- **CPU**: 2 cores minimum
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 20GB SSD minimum
- **Network**: Stable 10Mbps+ connection

### Latency Optimization

1. **Colocate Services**: Run everything on the same VPS
2. **Network Optimization**: Use high-speed internet
3. **MT5 Settings**: Configure MT5 for fastest execution
4. **Docker Optimization**: Use host networking if possible

## 🔄 Updates & Maintenance

### System Updates

```bash
# Update Docker images
docker-compose pull

# Restart services
docker-compose restart

# Update with new code
git pull
docker-compose up -d --build
```

### Backup Important Data

```bash
# Backup n8n workflows and data
docker run --rm -v tradingview-n8n:/data -v $(pwd):/backup alpine tar czf /backup/n8n-backup.tar.gz -C /data .

# Backup MT5 bridge logs
cp -r mt5-bridge/logs ./backup/
```

## 🤝 Support

### Getting Help

1. Check the logs: `docker-compose logs -f`
2. Verify configuration files
3. Test individual components
4. Check network connectivity

### Common Commands

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# Restart specific service
docker-compose restart mt5-bridge

# View resource usage
docker stats

# Clean up
docker system prune -a
```

## 📝 Changelog

### v1.0.0

- Initial release
- Docker-based deployment
- n8n workflow integration
- MT5 bridge service
- TradingView webhook support
- Comprehensive logging and monitoring

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**⚠️ Disclaimer**: This software is for educational and informational purposes only. Trading cryptocurrencies and forex involves substantial risk of loss and is not suitable for every investor. Past performance does not guarantee future results. Please trade responsibly and never risk more than you can afford to lose.
