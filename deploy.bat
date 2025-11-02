@echo off
REM TradingView to MT5 Automated Trading System - Windows Deployment Script

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support ANSI colors well, so we'll use plain text)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Default values
set COMPOSE_FILE=docker-compose.yml
set ENV_FILE=mt5-bridge\.env
set PROJECT_NAME=tradingview-mt5

REM Functions
:log_info
echo %INFO% %~1
goto :eof

:log_success
echo %SUCCESS% %~1
goto :eof

:log_warning
echo %WARNING% %~1
goto :eof

:log_error
echo %ERROR% %~1
goto :eof

:check_dependencies
call :log_info "Checking dependencies..."
docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit /b 1
)

call :log_success "Dependencies check passed"
goto :eof

:check_env_file
if not exist "%ENV_FILE%" (
    call :log_warning "Environment file %ENV_FILE% not found"
    set /p choice="Do you want to create it now? (y/n): "
    if /i "!choice!"=="y" (
        call :create_env_file
    ) else (
        call :log_error "Environment file is required. Exiting."
        exit /b 1
    )
)
goto :eof

:create_env_file
call :log_info "Creating environment file template..."

(
echo # MetaTrader 5 Configuration
echo MT5_LOGIN=your_mt5_login
echo MT5_PASSWORD=your_mt5_password
echo MT5_SERVER=your_mt5_server
echo MT5_PATH=/opt/mt5
echo.
echo # Trading Parameters
echo TRADING_SYMBOL=EURUSD
echo LOT_SIZE=0.01
echo MAGIC_NUMBER=123456
echo.
echo # Bridge Service Configuration
echo BRIDGE_PORT=5000
echo LOG_LEVEL=INFO
echo.
echo # Flask Configuration
echo FLASK_ENV=production
) > "%ENV_FILE%"

call :log_success "Environment file created: %ENV_FILE%"
call :log_warning "Please edit %ENV_FILE% with your actual MT5 credentials before deploying"
goto :eof

:build_services
call :log_info "Building Docker services..."
docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" build
if errorlevel 1 (
    call :log_error "Failed to build services"
    exit /b 1
)
call :log_success "Services built successfully"
goto :eof

:start_services
call :log_info "Starting services..."
docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" up -d
if errorlevel 1 (
    call :log_error "Failed to start services"
    exit /b 1
)
call :log_success "Services started successfully"
goto :eof

:stop_services
call :log_info "Stopping services..."
docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" down
call :log_success "Services stopped successfully"
goto :eof

:restart_services
call :log_info "Restarting services..."
docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" restart
call :log_success "Services restarted successfully"
goto :eof

:show_status
call :log_info "Service status:"
docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" ps

call :log_info "Checking service health..."

REM Check n8n
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5678/healthz' -TimeoutSec 10 | Out-Null; Write-Host '%SUCCESS% n8n is healthy' } catch { Write-Host '%ERROR% n8n is not responding' }"

REM Check MT5 Bridge
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5000/health' -TimeoutSec 10 | Out-Null; Write-Host '%SUCCESS% MT5 Bridge is healthy' } catch { Write-Host '%ERROR% MT5 Bridge is not responding' }"
goto :eof

:show_logs
if "%~1"=="" (
    call :log_info "Showing all logs..."
    docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" logs -f
) else (
    call :log_info "Showing logs for %~1..."
    docker-compose -f "%COMPOSE_FILE%" -p "%PROJECT_NAME%" logs -f "%~1"
)
goto :eof

:cleanup
call :log_info "Cleaning up unused Docker resources..."
docker system prune -f
call :log_success "Cleanup completed"
goto :eof

:backup_data
set "timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "backup_dir=backup\%timestamp%"

call :log_info "Creating backup in %backup_dir%..."

if not exist "%backup_dir%" mkdir "%backup_dir%"

REM Backup n8n data
call :log_info "Backing up n8n data..."
docker run --rm -v %PROJECT_NAME%_n8n_data:/data -v "%cd%":/backup alpine tar czf "/backup/%backup_dir%/n8n-data.tar.gz" -C /data .

REM Backup MT5 bridge logs
call :log_info "Backing up MT5 bridge logs..."
if exist "mt5-bridge\logs" (
    xcopy "mt5-bridge\logs" "%backup_dir%\logs\" /E /I /H /Y
)

REM Backup configuration files
call :log_info "Backing up configuration..."
copy "%COMPOSE_FILE%" "%backup_dir%\"
if exist "%ENV_FILE%" copy "%ENV_FILE%" "%backup_dir%\"

call :log_success "Backup completed: %backup_dir%"
goto :eof

:setup_n8n_workflow
call :log_info "Setting up n8n workflow..."
call :log_info "Please manually import the workflow from: n8n-workflows\tradingview-to-mt5-workflow.json"
call :log_info "1. Open http://localhost:5678 in your browser"
call :log_info "2. Go to Workflows -^> Import from File"
call :log_info "3. Select the workflow file"
call :log_info "4. Activate the workflow"
call :log_info "5. Copy the webhook URL for TradingView alerts"
goto :eof

:show_help
echo TradingView to MT5 Automated Trading System - Windows Deployment Script
echo.
echo USAGE:
echo     %0 [COMMAND]
echo.
echo COMMANDS:
echo     deploy      Full deployment (check dependencies, build, start)
echo     build       Build Docker services
echo     start       Start all services
echo     stop        Stop all services
echo     restart     Restart all services
echo     status      Show service status and health
echo     logs        Show all logs
echo     logs-n8n    Show n8n logs only
echo     logs-mt5    Show MT5 bridge logs only
echo     cleanup     Clean up unused Docker resources
echo     backup      Create backup of data and configurations
echo     setup-n8n   Setup instructions for n8n workflow
echo     help        Show this help message
echo.
echo EXAMPLES:
echo     %0 deploy          # Full deployment
echo     %0 status          # Check status
echo     %0 logs-mt5        # View MT5 bridge logs
echo     %0 backup          # Create backup
echo.
goto :eof

REM Main script logic
if "%1"=="deploy" (
    call :check_dependencies
    call :check_env_file
    call :build_services
    call :start_services
    call :show_status
    call :setup_n8n_workflow
) else if "%1"=="build" (
    call :check_dependencies
    call :build_services
) else if "%1"=="start" (
    call :check_dependencies
    call :check_env_file
    call :start_services
) else if "%1"=="stop" (
    call :stop_services
) else if "%1"=="restart" (
    call :restart_services
) else if "%1"=="status" (
    call :show_status
) else if "%1"=="logs" (
    call :show_logs
) else if "%1"=="logs-n8n" (
    call :show_logs n8n
) else if "%1"=="logs-mt5" (
    call :show_logs mt5-bridge
) else if "%1"=="cleanup" (
    call :cleanup
) else if "%1"=="backup" (
    call :backup_data
) else if "%1"=="setup-n8n" (
    call :setup_n8n_workflow
) else (
    call :show_help
)
