# Fetch
from decimal import Decimal
import time
import requests
import argparse

def rate_limiter(period):
    def decorator(func):
        last_call=[0.0]
        
        def wrapper(*args, **kwargs):
            last_call
            
            current_time = time.time()
            
            if current_time - last_call[0] < period:
                print("Rate limited!")
                return None
            
            last_call[0] = current_time
            
            return func(*args, **kwargs)
    
        return wrapper
    return decorator            
            
        
@rate_limiter(2)
def fetch_gemini ():
    url = "https://api.gemini.com/v1/book/BTCUSD"
    resp = requests.get(url)
    data = resp.json()
    bids =[]
    asks=[]
    
    for entry in data ["bids"]:
        price = Decimal(entry["price"])
        amount= Decimal(entry["amount"])
        
        bids.append([price, amount])
        
    for entry in data ["asks"]:
        price = Decimal(entry["price"])
        amount= Decimal(entry["amount"])
        
        asks.append([price, amount])
        
    
    return bids, asks

@rate_limiter(2)
def fetch_coinbase ():
    url = "https://api.exchange.coinbase.com/products/BTC-USD/book?level=2"
    resp = requests.get(url)
    data = resp.json()
    bids =[]
    asks=[]
    
    for entry in data ["bids"]:
        price = Decimal(entry[0])
        amount=Decimal(entry[1])
 
        
        bids.append([price, amount])
        
    for entry in data ["asks"]:
        price = Decimal(entry[0])
        amount=Decimal(entry[1])

        
        asks.append([price, amount])
        
    
    return bids, asks

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

        # print(f"Price:{price}\tbtc to buy:{btc_to_buy}\ttotalbtc{total_btc}\ttotal cost{total_cost}")

    return total_cost

def exec_bid(bids, target_btc):
    total_revenue = Decimal('0')
    total_btc = Decimal('0')

    # bids sorted high to low
    for price, amount in bids:
        if total_btc >= target_btc:
            break

        needed_btc = target_btc - total_btc
        btc_to_sell = min(amount, needed_btc)
        revenue = price * btc_to_sell

        total_btc += btc_to_sell
        total_revenue += revenue

        # print(f"Price:{price}\tbtc sold:{btc_to_sell}\ttotalbtc{total_btc}\ttotal revenue{total_revenue}")

    return total_revenue

gemini_result = fetch_gemini()
coinbase_result = fetch_coinbase()

if gemini_result is None or coinbase_result is None:
    print("One of the exchanges was rate limited. ")
else:
    parser = argparse.ArgumentParser(description="BTC-USD order book aggregator")
    parser.add_argument("--qty", type=Decimal, default=Decimal('10'), help="Quantity of BTC to buy/sell")
    args = parser.parse_args()
    qty = args.qty

    gemini_bids, gemini_asks = gemini_result
    coinbase_bids, coinbase_asks = coinbase_result

    combined_bids = gemini_bids + coinbase_bids
    combined_asks = gemini_asks + coinbase_asks

    combined_bids.sort(key=lambda x: x[0], reverse=True)
    combined_asks.sort(key=lambda x: x[0])

    result_ask = exec_ask(combined_asks, qty)
    result_bid = exec_bid(combined_bids,qty)
    
    amount_ask = result_ask
    formatted_amount_ask ="${:,.2f}".format(amount_ask)
    
    amount_bid = result_bid
    formatted_amount_bid ="${:,.2f}".format(amount_bid)
    
    
    print(f"To buy {qty} BTC: {formatted_amount_ask}")
    print(f"To sell {qty} BTC: {formatted_amount_bid}")
   
 


