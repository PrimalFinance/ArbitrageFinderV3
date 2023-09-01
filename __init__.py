# ArbitrageFinder related imports
from ArbitrageFinder.arbitrage_finderV3 import ArbitrageFinder
# Oracle related imports
from Oracle.coin_oracle import CoinOracle
# Time & Date related imports
import time
# Asynchronous imports
from concurrent.futures import ThreadPoolExecutor
# Wallet imports
from Wallet.wallet import ArbitrumWallet, OptimismWallet



def find_arbitrage_routes(tickers: list):

    for t in tickers:
        main(t)

def main(t: str):
    coin = CoinOracle()
    start = time.time()

    arb = ArbitrageFinder()
    
    
    arb.find_arbitrage_routes(t, ticker=True)
    print(f"----------------------------------------------------")
    arb.display_routes(routes_displayed=3)
    
    end = time.time()

    elapse = end - start

    print(f"Elapse: {elapse}")



def add_new_coin(ticker: str):
    coin = CoinOracle()
    
    coin.add_new_row(ticker)
    coin.write_cg_ids_to_csv()

def test():
    coin = CoinOracle()

    #coin.get_dex_pairs()
    coin.convert_addresses_to_uppercase()

def wallet():

    #w = OptimismWallet()
    w = ArbitrumWallet()
    w.get_token_balances()


if __name__ == "__main__":
    tickers = ["PYR", "UFT", "JOE", "WAIT"]
    ticker = "RETH"
    #find_arbitrage_routes(tickers=tickers)
    wallet()
    #add_new_coin(ticker) 
    #test()