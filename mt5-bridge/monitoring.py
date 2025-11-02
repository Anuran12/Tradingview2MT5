#!/usr/bin/env python3
"""
Monitoring script for MT5 Bridge Service
Provides health checks, metrics, and alerting
"""

import os
import time
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MT5Monitor:
    def __init__(self, bridge_url: str = "http://localhost:5000"):
        self.bridge_url = bridge_url.rstrip('/')
        self.alert_thresholds = {
            'max_response_time': 5.0,  # seconds
            'min_account_balance': 100.0,  # USD
            'max_positions': 10,  # maximum open positions
        }
        self.last_check = None
        self.error_count = 0
        self.max_errors = 5

    def check_health(self) -> Dict:
        """Check overall system health"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.bridge_url}/health", timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                health_data = response.json()
                health_data['response_time'] = response_time
                health_data['timestamp'] = datetime.now().isoformat()

                # Additional checks
                health_data['checks'] = self._perform_additional_checks()

                return {
                    'status': 'healthy' if health_data.get('status') == 'healthy' else 'unhealthy',
                    'details': health_data
                }
            else:
                return {
                    'status': 'unhealthy',
                    'details': {
                        'error': f'HTTP {response.status_code}',
                        'response_time': response_time
                    }
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'details': {'error': str(e)}
            }

    def _perform_additional_checks(self) -> Dict:
        """Perform additional health checks"""
        checks = {}

        try:
            # Check account info
            account_response = requests.get(f"{self.bridge_url}/account", timeout=5)
            if account_response.status_code == 200:
                account_data = account_response.json()
                checks['account_balance'] = account_data.get('balance', 0)
                checks['account_equity'] = account_data.get('equity', 0)
                checks['account_margin'] = account_data.get('margin', 0)
            else:
                checks['account_check'] = 'failed'

        except Exception as e:
            checks['account_check'] = f'error: {str(e)}'

        try:
            # Check positions
            positions_response = requests.get(f"{self.bridge_url}/positions", timeout=5)
            if positions_response.status_code == 200:
                positions_data = positions_response.json()
                checks['open_positions'] = len(positions_data.get('positions', []))
            else:
                checks['positions_check'] = 'failed'

        except Exception as e:
            checks['positions_check'] = f'error: {str(e)}'

        return checks

    def check_alerts(self, health_data: Dict) -> List[str]:
        """Check for alert conditions"""
        alerts = []

        if health_data['status'] != 'healthy':
            alerts.append("MT5 Bridge service is unhealthy")

        details = health_data.get('details', {})
        response_time = details.get('response_time', 0)
        if response_time > self.alert_thresholds['max_response_time']:
            alerts.append(".2f")

        checks = details.get('checks', {})

        account_balance = checks.get('account_balance', 0)
        if account_balance < self.alert_thresholds['min_account_balance']:
            alerts.append(".2f")

        open_positions = checks.get('open_positions', 0)
        if open_positions > self.alert_thresholds['max_positions']:
            alerts.append(f"Too many open positions: {open_positions}")

        return alerts

    def send_alert(self, message: str):
        """Send alert notification"""
        # This is a placeholder for alert mechanisms
        # You can integrate with email, Telegram, Slack, etc.

        logger.warning(f"ALERT: {message}")

        # Example: Send email alert
        # import smtplib
        # ... email sending code ...

        # Example: Send Telegram message
        # telegram_token = os.getenv('TELEGRAM_TOKEN')
        # chat_id = os.getenv('TELEGRAM_CHAT_ID')
        # ... telegram sending code ...

    def run_monitoring_loop(self, interval: int = 60):
        """Run continuous monitoring loop"""
        logger.info(f"Starting monitoring loop with {interval}s interval")

        while True:
            try:
                # Perform health check
                health_data = self.check_health()
                self.last_check = datetime.now()

                # Log health status
                if health_data['status'] == 'healthy':
                    logger.info("System health: OK")
                    self.error_count = 0
                else:
                    logger.error(f"System health: FAILED - {health_data}")
                    self.error_count += 1

                # Check for alerts
                alerts = self.check_alerts(health_data)
                for alert in alerts:
                    self.send_alert(alert)

                # Stop monitoring if too many errors
                if self.error_count >= self.max_errors:
                    logger.critical(f"Too many consecutive errors ({self.error_count}). Stopping monitoring.")
                    break

            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                self.error_count += 1

            # Wait for next check
            time.sleep(interval)

    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        try:
            # Get health data
            health = self.check_health()

            # Get additional metrics
            stats = {
                'timestamp': datetime.now().isoformat(),
                'health': health,
                'uptime': self._get_uptime(),
                'version': self._get_version(),
            }

            return stats

        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return str(timedelta(seconds=int(uptime_seconds)))
        except:
            return "unknown"

    def _get_version(self) -> str:
        """Get application version"""
        try:
            # You can read this from a version file or environment variable
            return os.getenv('APP_VERSION', '1.0.0')
        except:
            return "unknown"

def main():
    """Main monitoring function"""
    import argparse

    parser = argparse.ArgumentParser(description='MT5 Bridge Monitoring')
    parser.add_argument('--url', default='http://localhost:5000', help='MT5 Bridge URL')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run single check and exit')

    args = parser.parse_args()

    monitor = MT5Monitor(args.url)

    if args.once:
        # Single check mode
        health = monitor.check_health()
        print(json.dumps(health, indent=2))

        alerts = monitor.check_alerts(health)
        if alerts:
            print("\nAlerts:")
            for alert in alerts:
                print(f"- {alert}")
            exit(1)
        else:
            print("\nNo alerts")
            exit(0)
    else:
        # Continuous monitoring
        monitor.run_monitoring_loop(args.interval)

if __name__ == '__main__':
    main()
