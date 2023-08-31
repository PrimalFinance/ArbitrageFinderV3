from ArbitrageFinder.arbitrage_finderV3 import ArbitrageFinder

from Oracle.coin_oracle import CoinOracle

import time

from concurrent.futures import ThreadPoolExecutor




def find_arbitrage_routes():
    tickers = ["0x0", "CYBER", "FLEX", "FET", "VEGA"]

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

    coin.get_dex_pairs()
    

if __name__ == "__main__":
    find_arbitrage_routes()
    add_new_coin("OX") 
    #test()