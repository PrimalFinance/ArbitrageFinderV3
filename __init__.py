from ArbitrageFinder.arbitrage_finderV3 import ArbitrageFinder

from Oracle.coin_oracle import CoinOracle

import time

from concurrent.futures import ThreadPoolExecutor


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


if __name__ == "__main__":
    tickers = ["XDC", "STX", "BCH", "TON", "RUNE", "ARB", "WAGMIGAMES"]
    for t in tickers:
        main(t)