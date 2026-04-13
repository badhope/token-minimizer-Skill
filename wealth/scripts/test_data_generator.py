"""Comprehensive test data generator for Wealth platform."""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List
from dataclasses import dataclass, asdict
import random
import hashlib

@dataclass
class StockKline:
    timestamp: str
    symbol: str
    name: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    change_pct: float

@dataclass
class FundData:
    symbol: str
    name: str
    date: str
    net_value: float
    cumulative_value: float
    daily_return: float
    subscription_status: str
    redemption_status: str

@dataclass
class IndicatorData:
    timestamp: str
    symbol: str
    rsi: float
    kdj_k: float
    kdj_d: float
    kdj_j: float
    macd_dif: float
    macd_dea: float
    macd_hist: float
    boll_upper: float
    boll_middle: float
    boll_lower: float

@dataclass
class TradeRecord:
    trade_id: str
    timestamp: str
    symbol: str
    name: str
    type: str
    price: float
    quantity: int
    amount: float
    commission: float

@dataclass
class BacktestResult:
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    trades: List[Dict]

class TestDataGenerator:
    SYMBOLS = ["000001", "000002", "600000", "600036", "000858", "000333", "600519", "601318"]
    NAMES = ["平安银行", "万科A", "浦发银行", "招商银行", "五粮液", "美的集团", "贵州茅台", "中国平安"]
    STRATEGIES = ["macd", "kdj", "bollinger", "mean_reversion"]

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data", "test")
        os.makedirs(self.data_dir, exist_ok=True)

    def generate_stock_kline(self, symbol: str, days: int = 100) -> List[StockKline]:
        """Generate mock stock K-line data."""
        name = self.NAMES[self.SYMBOLS.index(symbol)] if symbol in self.SYMBOLS else f"股票{symbol}"
        base_price = random.uniform(10, 200)
        data = []
        current_date = datetime.now()

        for i in range(days):
            date = current_date - timedelta(days=days - i - 1)
            change = random.uniform(-0.1, 0.1)
            open_price = base_price * (1 + random.uniform(-0.02, 0.02))
            close_price = open_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
            volume = int(random.uniform(1e6, 1e8))
            amount = volume * close_price

            kline = StockKline(
                timestamp=date.strftime("%Y-%m-%d"),
                symbol=symbol,
                name=name,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume,
                amount=round(amount, 2),
                change_pct=round(change * 100, 2)
            )
            data.append(kline)
            base_price = close_price

        return data

    def generate_fund_data(self, symbol: str, days: int = 100) -> List[FundData]:
        """Generate mock fund data."""
        name = f"基金{symbol}"
        base_value = 1.0
        data = []
        current_date = datetime.now()

        for i in range(days):
            date = current_date - timedelta(days=days - i - 1)
            daily_return = random.uniform(-0.05, 0.05)
            net_value = base_value * (1 + daily_return)

            fund = FundData(
                symbol=symbol,
                name=name,
                date=date.strftime("%Y-%m-%d"),
                net_value=round(net_value, 4),
                cumulative_value=round(net_value * random.uniform(1.1, 2.0), 4),
                daily_return=round(daily_return * 100, 4),
                subscription_status=random.choice(["开放", "暂停", "限大额"]),
                redemption_status=random.choice(["开放", "暂停", "T+3"])
            )
            data.append(fund)
            base_value = net_value

        return data

    def generate_indicators(self, symbol: str, days: int = 100) -> List[IndicatorData]:
        """Generate mock technical indicators."""
        data = []
        current_date = datetime.now()

        for i in range(days):
            date = current_date - timedelta(days=days - i - 1)

            indicator = IndicatorData(
                timestamp=date.strftime("%Y-%m-%d"),
                symbol=symbol,
                rsi=round(random.uniform(20, 80), 2),
                kdj_k=round(random.uniform(10, 90), 2),
                kdj_d=round(random.uniform(10, 90), 2),
                kdj_j=round(random.uniform(0, 100), 2),
                macd_dif=round(random.uniform(-1, 1), 4),
                macd_dea=round(random.uniform(-1, 1), 4),
                macd_hist=round(random.uniform(-0.5, 0.5), 4),
                boll_upper=round(random.uniform(90, 110), 2),
                boll_middle=round(random.uniform(85, 105), 2),
                boll_lower=round(random.uniform(80, 100), 2)
            )
            data.append(indicator)

        return data

    def generate_trade_records(self, symbol: str, count: int = 50) -> List[TradeRecord]:
        """Generate mock trade records."""
        name = self.NAMES[self.SYMBOLS.index(symbol)] if symbol in self.SYMBOLS else f"股票{symbol}"
        records = []
        current_date = datetime.now()

        for i in range(count):
            date = current_date - timedelta(days=count - i - 1, hours=random.randint(9, 15))
            trade_type = random.choice(["buy", "sell"])
            price = round(random.uniform(10, 200), 2)
            quantity = random.randint(100, 10000) * 100
            amount = price * quantity
            commission = max(amount * 0.0003, 5)

            trade = TradeRecord(
                trade_id=f"TR{date.strftime('%Y%m%d')}{i:04d}",
                timestamp=date.strftime("%Y-%m-%d %H:%M:%S"),
                symbol=symbol,
                name=name,
                type=trade_type,
                price=price,
                quantity=quantity,
                amount=round(amount, 2),
                commission=round(commission, 2)
            )
            records.append(trade)

        return records

    def generate_backtest_result(self, strategy: str, symbol: str) -> BacktestResult:
        """Generate mock backtest result."""
        initial_capital = 100000.0
        total_return = random.uniform(-0.3, 0.5)
        final_capital = initial_capital * (1 + total_return)
        days = random.randint(180, 365)
        annualized_return = (1 + total_return) ** (365 / days) - 1

        trades = self.generate_trade_records(symbol, random.randint(10, 30))

        return BacktestResult(
            strategy_name=strategy,
            symbol=symbol,
            start_date=(datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            initial_capital=initial_capital,
            final_capital=round(final_capital, 2),
            total_return=round(total_return * 100, 2),
            annualized_return=round(annualized_return * 100, 2),
            sharpe_ratio=round(random.uniform(0.5, 3.0), 2),
            max_drawdown=round(random.uniform(5, 25), 2),
            win_rate=round(random.uniform(30, 70), 1),
            total_trades=len(trades),
            trades=[asdict(t) for t in trades]
        )

    def save_to_file(self, data: Any, filename: str) -> str:
        """Save data to JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return filepath

    def calculate_checksum(self, filepath: str) -> str:
        """Calculate MD5 checksum of a file."""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def generate_all_test_data(self) -> Dict[str, Any]:
        """Generate all types of test data."""
        results = {
            "generation_time": datetime.now().isoformat(),
            "files": [],
            "total_records": 0
        }

        for symbol in self.SYMBOLS:
            klines = self.generate_stock_kline(symbol, days=100)
            kline_path = self.save_to_file([asdict(k) for k in klines], f"kline_{symbol}.json")
            results["files"].append({"type": "kline", "symbol": symbol, "path": kline_path, "records": len(klines)})
            results["total_records"] += len(klines)

            indicators = self.generate_indicators(symbol, days=100)
            indicator_path = self.save_to_file([asdict(i) for i in indicators], f"indicator_{symbol}.json")
            results["files"].append({"type": "indicator", "symbol": symbol, "path": indicator_path, "records": len(indicators)})
            results["total_records"] += len(indicators)

        fund_symbols = ["000001", "000002", "000003", "000004"]
        for symbol in fund_symbols:
            funds = self.generate_fund_data(symbol, days=100)
            fund_path = self.save_to_file([asdict(f) for f in funds], f"fund_{symbol}.json")
            results["files"].append({"type": "fund", "symbol": symbol, "path": fund_path, "records": len(funds)})
            results["total_records"] += len(funds)

        for strategy in self.STRATEGIES:
            symbol = random.choice(self.SYMBOLS)
            backtest = self.generate_backtest_result(strategy, symbol)
            backtest_path = self.save_to_file(asdict(backtest), f"backtest_{strategy}_{symbol}.json")
            results["files"].append({"type": "backtest", "strategy": strategy, "symbol": symbol, "path": backtest_path})
            results["total_records"] += 1

        metadata = {
            "symbols": self.SYMBOLS,
            "strategies": self.STRATEGIES,
            "generation_time": results["generation_time"],
            "total_files": len(results["files"]),
            "total_records": results["total_records"]
        }
        metadata_path = self.save_to_file(metadata, "metadata.json")
        results["files"].append({"type": "metadata", "path": metadata_path})

        checksums = {}
        for file_info in results["files"]:
            if os.path.exists(file_info["path"]):
                checksums[os.path.basename(file_info["path"])] = self.calculate_checksum(file_info["path"])

        checksum_path = self.save_to_file(checksums, "checksums.json")
        results["files"].append({"type": "checksums", "path": checksum_path})
        results["checksums"] = checksums

        results["total_files"] = len(results["files"])
        summary_path = self.save_to_file(results, "generation_summary.json")
        results["summary_path"] = summary_path

        return results

def main():
    print("=" * 60)
    print("Wealth Platform - Test Data Generator")
    print("=" * 60)

    generator = TestDataGenerator()
    print(f"\n[1/4] Data directory: {generator.data_dir}")

    print("\n[2/4] Generating test data...")
    results = generator.generate_all_test_data()

    print(f"\n[3/4] Validating data...")
    all_valid = True
    for file_info in results["files"]:
        if os.path.exists(file_info["path"]):
            size = os.path.getsize(file_info["path"])
            print(f"  ✓ {os.path.basename(file_info['path'])} ({size} bytes)")
        else:
            print(f"  ✗ {file_info['path']} - MISSING")
            all_valid = False

    if all_valid:
        print("\n[4/4] Data generation complete!")
        print(f"\nSummary:")
        print(f"  - Total files: {results['total_files']}")
        print(f"  - Total records: {results['total_records']}")
        print(f"  - Generation time: {results['generation_time']}")
        print(f"\nData stored at: {generator.data_dir}")
    else:
        print("\n⚠ Some files are missing!")

    print("\n" + "=" * 60)
    return results

if __name__ == "__main__":
    main()
