"""Alert and notification system implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger

from wealth.data.base import RealtimeQuote


class AlertType(str, Enum):
    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"
    PERCENT_CHANGE = "PERCENT_CHANGE"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    STRATEGY_SIGNAL = "STRATEGY_SIGNAL"
    RSI_OVERBOUGHT = "RSI_OVERBOUGHT"
    RSI_OVERSOLD = "RSI_OVERSOLD"


class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    alert_id: str
    symbol: str
    alert_type: AlertType
    level: AlertLevel
    condition: str
    current_value: float
    message: str
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PriceAlert(Alert):
    target_price: float = 0.0
    direction: str = ""


@dataclass
class PercentChangeAlert(Alert):
    threshold_pct: float = 0.0


@dataclass
class VolumeAlert(Alert):
    threshold_volume: float = 0.0


@dataclass
class StrategyAlert(Alert):
    signal_type: str = ""
    strategy_name: str = ""


class Notifier(ABC):
    @abstractmethod
    def send(self, alert: Alert) -> bool:
        pass

    @abstractmethod
    async def send_async(self, alert: Alert) -> bool:
        pass


class DesktopNotifier(Notifier):
    def __init__(self):
        try:
            from plyer import notification
            self._notification = notification
            self._available = True
        except ImportError:
            logger.warning("plyer not available, desktop notifications disabled")
            self._available = False

    def send(self, alert: Alert) -> bool:
        if not self._available:
            return False

        try:
            self._notification.notify(
                title=f"[{alert.level.value}] {alert.symbol}",
                message=alert.message,
                app_name="Wealth",
                timeout=10,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
            return False

    async def send_async(self, alert: Alert) -> bool:
        return self.send(alert)


class EmailNotifier(Notifier):
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: List[str],
        use_tls: bool = True,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.use_tls = use_tls

    def send(self, alert: Alert) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)
            msg["Subject"] = f"[Wealth] {alert.level.value} - {alert.symbol}: {alert.message}"

            body = f"""
Alert Details:
- Symbol: {alert.symbol}
- Type: {alert.alert_type.value}
- Level: {alert.level.value}
- Condition: {alert.condition}
- Current Value: {alert.current_value}
- Message: {alert.message}
- Time: {alert.triggered_at or datetime.now()}
"""
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    async def send_async(self, alert: Alert) -> bool:
        return self.send(alert)


class WebhookNotifier(Notifier):
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}

    def send(self, alert: Alert) -> bool:
        try:
            import httpx
            payload = {
                "alert_id": alert.alert_id,
                "symbol": alert.symbol,
                "type": alert.alert_type.value,
                "level": alert.level.value,
                "message": alert.message,
                "current_value": alert.current_value,
                "condition": alert.condition,
                "timestamp": (alert.triggered_at or datetime.now()).isoformat(),
            }

            with httpx.Client() as client:
                response = client.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False

    async def send_async(self, alert: Alert) -> bool:
        try:
            import httpx
            payload = {
                "alert_id": alert.alert_id,
                "symbol": alert.symbol,
                "type": alert.alert_type.value,
                "level": alert.level.value,
                "message": alert.message,
                "current_value": alert.current_value,
                "condition": alert.condition,
                "timestamp": (alert.triggered_at or datetime.now()).isoformat(),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class DingTalkNotifier(Notifier):
    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secret

    def _generate_sign(self) -> str:
        if not self.secret:
            return ""

        import base64
        import hashlib
        import hmac
        import time
        import urllib.parse

        timestamp = str(int(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f"&timestamp={timestamp}&sign={sign}"

    def send(self, alert: Alert) -> bool:
        try:
            import httpx
            url = self.webhook_url + self._generate_sign()

            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"[{alert.level.value}] {alert.symbol}",
                    "text": f"## [{alert.level.value}] {alert.symbol}\n\n**{alert.message}**\n\n- Condition: {alert.condition}\n- Current Value: {alert.current_value}\n- Time: {alert.triggered_at or datetime.now()}",
                },
            }

            with httpx.Client() as client:
                response = client.post(url, json=payload, timeout=10)
                return response.json().get("errcode", 1) == 0
        except Exception as e:
            logger.error(f"Failed to send DingTalk notification: {e}")
            return False

    async def send_async(self, alert: Alert) -> bool:
        return self.send(alert)


class WeChatNotifier(Notifier):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, alert: Alert) -> bool:
        try:
            import httpx
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"[{alert.level.value}] {alert.symbol}: {alert.message}",
                },
            }

            with httpx.Client() as client:
                response = client.post(self.webhook_url, json=payload, timeout=10)
                return response.json().get("errcode", 1) == 0
        except Exception as e:
            logger.error(f"Failed to send WeChat notification: {e}")
            return False

    async def send_async(self, alert: Alert) -> bool:
        return self.send(alert)


class NotifierManager:
    def __init__(self):
        self._notifiers: List[Notifier] = []
        self._alerts: List[Alert] = []
        self._alert_handlers: Dict[str, callable] = {}

    def add_notifier(self, notifier: Notifier):
        self._notifiers.append(notifier)

    def remove_notifier(self, notifier: Notifier):
        if notifier in self._notifiers:
            self._notifiers.remove(notifier)

    def register_handler(self, alert_type: AlertType, handler: callable):
        self._alert_handlers[alert_type.value] = handler

    async def send_alert(self, alert: Alert) -> Dict[str, bool]:
        alert.triggered_at = datetime.now()
        self._alerts.append(alert)

        results = {}
        for notifier in self._notifiers:
            name = notifier.__class__.__name__
            results[name] = await notifier.send_async(alert)

        return results

    def send_alert_sync(self, alert: Alert) -> Dict[str, bool]:
        alert.triggered_at = datetime.now()
        self._alerts.append(alert)

        results = {}
        for notifier in self._notifiers:
            name = notifier.__class__.__name__
            results[name] = notifier.send(alert)

        return results

    def get_active_alerts(self) -> List[Alert]:
        return [a for a in self._alerts if a.is_active]

    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        return sorted(self._alerts, key=lambda x: x.triggered_at or datetime.min, reverse=True)[:limit]


class AlertMonitor:
    def __init__(self, data_source, notifier_manager: NotifierManager):
        self.data_source = data_source
        self.notifier_manager = notifier_manager
        self._monitoring = False
        self._monitor_tasks: List[asyncio.Task] = []

    async def start_monitoring(self, symbols: List[str], interval: int = 60):
        self._monitoring = True
        logger.info(f"Started monitoring {len(symbols)} symbols")

    async def stop_monitoring(self):
        self._monitoring = False
        for task in self._monitor_tasks:
            task.cancel()
        logger.info("Stopped monitoring")

    async def check_price_alerts(self, symbol: str, current_price: float):
        active_alerts = self.notifier_manager.get_active_alerts()
        price_alerts = [
            a for a in active_alerts
            if a.symbol == symbol and a.alert_type in [AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW]
        ]

        for alert in price_alerts:
            triggered = False
            if alert.alert_type == AlertType.PRICE_ABOVE and current_price >= alert.current_value:
                triggered = True
            elif alert.alert_type == AlertType.PRICE_BELOW and current_price <= alert.current_value:
                triggered = True

            if triggered:
                alert.condition = f"Price {current_price} crossed threshold"
                await self.notifier_manager.send_alert(alert)

    async def check_percent_change_alerts(self, symbol: str, change_pct: float):
        active_alerts = self.notifier_manager.get_active_alerts()
        pct_alerts = [
            a for a in active_alerts
            if a.symbol == symbol and a.alert_type == AlertType.PERCENT_CHANGE
        ]

        for alert in pct_alerts:
            threshold = alert.metadata.get("threshold_pct", 0)
            if abs(change_pct) >= threshold:
                alert.condition = f"Change {change_pct}% exceeded threshold {threshold}%"
                await self.notifier_manager.send_alert(alert)

    async def check_volume_alerts(self, symbol: str, volume: float, avg_volume: float):
        active_alerts = self.notifier_manager.get_active_alerts()
        vol_alerts = [
            a for a in active_alerts
            if a.symbol == symbol and a.alert_type == AlertType.VOLUME_SPIKE
        ]

        for alert in vol_alerts:
            threshold = alert.metadata.get("threshold_ratio", 3.0)
            ratio = volume / avg_volume if avg_volume > 0 else 0
            if ratio >= threshold:
                alert.condition = f"Volume {ratio:.1f}x average"
                await self.notifier_manager.send_alert(alert)
