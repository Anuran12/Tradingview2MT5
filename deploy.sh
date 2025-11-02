#!/bin/bash

# TradingView to MT5 Automated Trading System - Deployment Script
# This script helps deploy and manage the trading system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COMPOSE_FILE="docker-compose.yml"
ENV_FILE="mt5-bridge/.env"
PROJECT_NAME="tradingview-mt5"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Dependencies check passed"
}

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Environment file $ENV_FILE not found"
        read -p "Do you want to create it now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_env_file
        else
            log_error "Environment file is required. Exiting."
            exit 1
        fi
    fi
}

create_env_file() {
    log_info "Creating environment file template..."

    cat > "$ENV_FILE" << EOF
# MetaTrader 5 Configuration
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server
MT5_PATH=/opt/mt5

# Trading Parameters
TRADING_SYMBOL=EURUSD
LOT_SIZE=0.01
MAGIC_NUMBER=123456

# Bridge Service Configuration
BRIDGE_PORT=5000
LOG_LEVEL=INFO

# Flask Configuration
FLASK_ENV=production
EOF

    log_success "Environment file created: $ENV_FILE"
    log_warning "Please edit $ENV_FILE with your actual MT5 credentials before deploying"
}

build_services() {
    log_info "Building Docker services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build
    log_success "Services built successfully"
}

start_services() {
    log_info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    log_success "Services started successfully"
}

stop_services() {
    log_info "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    log_success "Services stopped successfully"
}

restart_services() {
    log_info "Restarting services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart
    log_success "Services restarted successfully"
}

show_status() {
    log_info "Service status:"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps

    log_info "Checking service health..."

    # Check n8n
    if curl -f http://localhost:5678/healthz &> /dev/null; then
        log_success "n8n is healthy"
    else
        log_error "n8n is not responding"
    fi

    # Check MT5 Bridge
    if curl -f http://localhost:5000/health &> /dev/null; then
        log_success "MT5 Bridge is healthy"
    else
        log_error "MT5 Bridge is not responding"
    fi
}

show_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        log_info "Showing logs for $service..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$service"
    else
        log_info "Showing all logs..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
    fi
}

cleanup() {
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f
    log_success "Cleanup completed"
}

backup_data() {
    local backup_dir="./backup/$(date +%Y%m%d_%H%M%S)"
    log_info "Creating backup in $backup_dir..."

    mkdir -p "$backup_dir"

    # Backup n8n data
    log_info "Backing up n8n data..."
    docker run --rm -v ${PROJECT_NAME}_n8n_data:/data -v $(pwd):/backup alpine tar czf "/backup/$backup_dir/n8n-data.tar.gz" -C /data .

    # Backup MT5 bridge logs
    log_info "Backing up MT5 bridge logs..."
    cp -r mt5-bridge/logs "$backup_dir/" 2>/dev/null || true

    # Backup configuration files
    log_info "Backing up configuration..."
    cp docker-compose.yml "$backup_dir/"
    cp mt5-bridge/.env "$backup_dir/" 2>/dev/null || true

    log_success "Backup completed: $backup_dir"
}

setup_n8n_workflow() {
    log_info "Setting up n8n workflow..."

    # Wait for n8n to be ready
    log_info "Waiting for n8n to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:5678/healthz &> /dev/null; then
            break
        fi
        sleep 2
    done

    log_info "Please manually import the workflow from: n8n-workflows/tradingview-to-mt5-workflow.json"
    log_info "1. Open http://localhost:5678 in your browser"
    log_info "2. Go to Workflows > Import from File"
    log_info "3. Select the workflow file"
    log_info "4. Activate the workflow"
    log_info "5. Copy the webhook URL for TradingView alerts"
}

show_help() {
    cat << EOF
TradingView to MT5 Automated Trading System - Deployment Script

USAGE:
    $0 [COMMAND]

COMMANDS:
    deploy      Full deployment (check dependencies, build, start)
    build       Build Docker services
    start       Start all services
    stop        Stop all services
    restart     Restart all services
    status      Show service status and health
    logs        Show all logs
    logs-n8n    Show n8n logs only
    logs-mt5    Show MT5 bridge logs only
    cleanup     Clean up unused Docker resources
    backup      Create backup of data and configurations
    setup-n8n   Setup instructions for n8n workflow
    help        Show this help message

ENVIRONMENT:
    COMPOSE_FILE    Docker Compose file (default: docker-compose.yml)
    ENV_FILE        Environment file (default: mt5-bridge/.env)

EXAMPLES:
    $0 deploy          # Full deployment
    $0 status          # Check status
    $0 logs-mt5        # View MT5 bridge logs
    $0 backup          # Create backup

EOF
}

# Main script logic
case "${1:-help}" in
    "deploy")
        check_dependencies
        check_env_file
        build_services
        start_services
        show_status
        setup_n8n_workflow
        ;;
    "build")
        check_dependencies
        build_services
        ;;
    "start")
        check_dependencies
        check_env_file
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "logs-n8n")
        show_logs "n8n"
        ;;
    "logs-mt5")
        show_logs "mt5-bridge"
        ;;
    "cleanup")
        cleanup
        ;;
    "backup")
        backup_data
        ;;
    "setup-n8n")
        setup_n8n_workflow
        ;;
    "help"|*)
        show_help
        ;;
esac
