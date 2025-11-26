from decimal import Decimal
import time
import requests
import argparse

# Limiter to calls to the api for the period of 2 seconds 
def rate_limiter(period):
    def decorator(func):
        # mutable so inner function can be modified 
        last_call=[0]
        
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # if last call was within the period, skip execution
            if current_time - last_call[0] < period:
                print("Rate limited")
                return None
            
            # update last call timestamp and continue
            last_call[0] = current_time
            return func(*args, **kwargs)
    
        return wrapper
    return decorator            
            
# simulates the api rate limit   
@rate_limiter(2)
def fetch_gemini ():
    url = "https://api.gemini.com/v1/book/BTCUSD"
    resp = requests.get(url)
    data = resp.json()
    
    bids =[]
    asks=[]
    
    # Gemini return values for bids/asks in the string "price" and "amount"
    for entry in data ["bids"]:
        if "price"not in entry or "amount" not in entry:
            print("Malformed Entry bids:", entry)
            continue
        
        price = Decimal(entry["price"])
        amount= Decimal(entry["amount"])
        bids.append([price, amount])
        
    for entry in data ["asks"]:
        if "price" not in entry or "amount" not in entry:
            print("Malformed Entry asks:", entry)
            continue
            
        price = Decimal(entry["price"])
        amount= Decimal(entry["amount"])
        asks.append([price, amount])
    
    return bids, asks

# simulates the api rate limit
@rate_limiter(2)
def fetch_coinbase ():
    url = "https://api.exchange.coinbase.com/products/BTC-USD/book?level=2"
    resp = requests.get(url)
    data = resp.json()
    bids =[]
    asks=[]
    # Coinbase returns bids/asks as lists: [price, size]
    for entry in data ["bids"]:
        price = Decimal(entry[0])
        amount=Decimal(entry[1])
        bids.append([price, amount])
        
    for entry in data ["asks"]:
        price = Decimal(entry[0])
        amount=Decimal(entry[1])
        asks.append([price, amount]) 
    
    return bids, asks

# calculate cost of buying BTC
def exec_ask(asks, target_btc):
    # Counters set at 0
    total_cost = Decimal('0')
    total_btc = Decimal('0')
    
    # iterate through ask prices: price1, amount1 - price 2, amount 2
    for price, amount in asks:
        # stop if you bought enough (10BTC)
        if total_btc >= target_btc:
            break
        # calculate how much you still need
        needed_btc = target_btc - total_btc
        btc_to_buy = min(amount, needed_btc)
        cost = price * btc_to_buy

        total_btc += btc_to_buy
        total_cost += cost

    return total_cost

# calculate revenue of selling BTC
def exec_bid(bids, target_btc):
    total_revenue = Decimal('0')
    total_btc = Decimal('0')
    
    for price, amount in bids:
        # stop if bid reached the target btc
        if total_btc >= target_btc:
            break

        needed_btc = target_btc - total_btc
        btc_to_sell = min(amount, needed_btc)
        revenue = price * btc_to_sell

        total_btc += btc_to_sell
        total_revenue += revenue

    return total_revenue
# safe decimal validator
def positive_decimal(value):
    try:
        val = Decimal(value)
    except:
        raise argparse.ArgumentTypeError("Invalid number: '{value}'")
    
    if val <= 0:
        raise argparse.ArgumentTypeError("qty must be greater than 0")

    return val

# Script entry point
gemini_result = fetch_gemini()
coinbase_result = fetch_coinbase()

# If either API call was rate-limited, skip execution
if gemini_result is None or coinbase_result is None:
    print("One of the exchanges was rate limited. ")
else:
    # Read command-line argument: --qty (amount of btc)
    parser = argparse.ArgumentParser(description="BTC-USD order book aggregator")
    parser.add_argument("--qty", type=positive_decimal, default=Decimal('10'), help="Quantity of BTC to buy/sell")
    args = parser.parse_args()
    qty = args.qty
    
    if qty <= 0:
        print("Please enter a positive number")
        exit(1)
        
    # unpack order books
    gemini_bids, gemini_asks = gemini_result
    coinbase_bids, coinbase_asks = coinbase_result
    
    # combine liquidity sources (gemini + coinbase)
    combined_bids = gemini_bids + coinbase_bids
    combined_asks = gemini_asks + coinbase_asks
    
    # ensure proper sorting
    # bids are high to low
    combined_bids.sort(key=lambda x: x[0], reverse=True)
    # asks are low to high
    combined_asks.sort(key=lambda x: x[0])
    

    # run simulated trades
    result_ask = exec_ask(combined_asks, qty)
    result_bid = exec_bid(combined_bids,qty)
    
    # format USD (XXX,XXX.XX)
    amount_ask = result_ask
    formatted_amount_ask ="${:,.2f}".format(amount_ask)
    amount_bid = result_bid
    formatted_amount_bid ="${:,.2f}".format(amount_bid)
    
    # Final output
    print(f"To buy {qty} BTC: {formatted_amount_ask}")
    print(f"To sell {qty} BTC: {formatted_amount_bid}")
   
 


