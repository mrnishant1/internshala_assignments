import time
import hmac
import hashlib
import json
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from dotenv import load_dotenv 
import os
load_dotenv()
secretKey = os.getenv("secretKey")
apiKey = os.getenv("apiKey")

def place_order(symbol: str, side: str, order_type: str, quantity: float, price: float = None):
    # validation API key and SecretKey
    if not secretKey or not apiKey:
        print("error: Missing secretKey or apiKey")
        return

    # validate required parameters
    missing = []
    if not symbol:
        missing.append('symbol')
    if not side:
        missing.append('side')
    if not order_type:
        missing.append('order_type')
    if quantity is None:
        missing.append('quantity')
    if order_type and order_type.upper() == 'LIMIT' and price is None:
        missing.append('price')

    if missing:
        error = {'status': 'error', 'message': f'missing parameter(s): {", ".join(missing)}'}
        print(error)
        return error

    order_type = order_type.upper()
    side = side.upper()
    time_in_force = 'GTC'
    recv_window = 5000
    timestamp = int(time.time() * 1000)

    params = [
        f"symbol={symbol}",
        f"side={side}",
        f"type={order_type}",
        f"quantity={quantity}"
    ]

    if order_type == 'LIMIT':
        params.append(f"price={price}")
        params.append(f"timeInForce={time_in_force}")

    params.append(f"recvWindow={recv_window}")
    params.append(f"timestamp={timestamp}")

    query_string = '&'.join(params)
    signature = hmac.new(
        secretKey.encode('utf-8'),
        query_string.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).hexdigest()

    url = f"https://demo-fapi.binance.com/fapi/v1/order?{query_string}&signature={signature}"
    headers = {
        'X-MBX-APIKEY': apiKey,
        'Content-Type': 'application/json'
    }

    try:
        req = Request(url, headers=headers, method='POST')
        with urlopen(req) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            print(data)
    except HTTPError as exc:
        try:
            body = exc.read().decode('utf-8')
            data = json.loads(body)
        except Exception:
            data = {'status': 'error', 'message': exc.reason}
        print(data)
    except URLError as exc:
        print({'status': 'error', 'message': str(exc.reason)})
        return {'status': 'error', 'message': str(exc.reason)}

def run_place_order():
    # validation API key and SecretKey
    if not secretKey or not apiKey:
        print("error: Missing secretKey or apiKey")
        return

    symbol = str(input("Trading Symbol: ").strip())
    if not symbol:
        print("error: symbol is required")
        return

    side = str(input("BUY or SELL: ").strip()).upper()
    if side not in ('BUY', 'SELL'):
        print("error: side must be BUY or SELL")
        return

    order_type = str(input("MARKET or LIMIT: ").strip()).upper()
    if order_type not in ('MARKET', 'LIMIT'):
        print("error: order_type must be MARKET or LIMIT")
        return

    try:
        quantity = float(input("Asset Quantity: "))
    except ValueError:
        print("error: quantity must be a number")
        return

    price = None
    if order_type == 'LIMIT':
        try:
            price = float(input("at Price: "))
        except ValueError:
            print("error: price must be a number")
            return

    place_order(symbol, side, order_type, quantity, price)

if __name__ == "__main__":
    run_place_order()
    
