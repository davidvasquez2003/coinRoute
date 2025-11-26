# BTC Order Book Aggregator
Python script that fetches Bitcoin order books from Gemini and Coinbase exchanges to calculate the cost of buying or selling BTC.

## Usage
```bash
python main.py --qty 10
```

**Options:**
- `--qty` - Amount of BTC to buy/sell (default: 10)

**Example:**
```bash
python main.py              # Buy/sell 10 BTC
python main.py --qty 5      # Buy/sell 5 BTC  
python main.py --qty 0.1    # Buy/sell 0.1 BTC
```

## Requirements
```bash
pip install requests
```

## How it works
1. Fetches live order book data from Gemini and Coinbase APIs
2. Combines and sorts the order books for best prices
3. Simulates buying (asks) and selling (bids) the specified amount
4. Shows total cost/revenue with rate limiting protection