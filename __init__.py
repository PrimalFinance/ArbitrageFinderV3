# ArbitrageFinder related imports
from ArbitrageFinder.arbitrage_finderV3 import ArbitrageFinder
# Oracle related imports
from Oracle.coin_oracle import CoinOracle
# Time & Date related imports
import time
# Asynchronous imports
from concurrent.futures import ThreadPoolExecutor
# Wallet imports
from Wallet.wallet import ArbitrumWallet, OptimismWallet, PolygonWallet

import logging



arbitrage_text_file = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\arbitrage_routes.txt"

logging.basicConfig(
            filename=arbitrage_text_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )



"""
------------------------------------------------------------------------------------------
ARBITRAGE
------------------------------------------------------------------------------------------
"""



def arbitrage_stager(setting: int = 1, route_limit: int = 3, custom_list: list = []):

    # Clear any previous contents within the logger.
    with open(arbitrage_text_file, 'w') as file:
        # The file is now open in write mode and empty
        pass  # You can perform other operations if needed

    # Create a Coin Oracle Object.
    c = CoinOracle()

    # Setting 1.
    if setting == 1:
        # Get the gainers and losers
        gainers, losers = c.get_gainers_losers(return_data="ticker")
        gainers = gainers[:10]

        for g in gainers.iterrows():
            ticker = g[1]["symbol"]
            find_arbitrage_routes(ticker, route_limit=route_limit)
    # Setting 2
    elif setting == 2:
        tickers = c.get_trending_tickers()
        tickers = [i["ticker"] for i in tickers]
        print(f"Tickers: {tickers}")
        for t in tickers:
            find_arbitrage_routes(t, route_limit=route_limit)
    # Setting 3
    elif setting == 3:
        for t in custom_list:
            find_arbitrage_routes(t, route_limit=route_limit)
    
    # Setting 4
    elif setting == 4:
        arb = ArbitrageFinder()
        for t in custom_list:
            find_arbitrage_routes(t, route_limit=route_limit, func_type=2)

def find_arbitrage_routes(t: str, route_limit: int, func_type: int = 1):
    start = time.time()

    arb = ArbitrageFinder()
    if func_type == 1:
        arb.find_arbitrage_routes(t, ticker=True)
    elif func_type == 2:
        arb.find_arbitrage_routes2(t)
    logging.info(f"-------------------------------------------------------------------------------------------------------------------")
    logging.info(f"[{t}]")
    arb.display_routes(routes_displayed=route_limit)
    
    end = time.time()

    elapse = end - start

    print(f"Elapse: {elapse}")

def test1():

    c = CoinOracle()

    ticker_num = 5

    gainers, losers = c.get_gainers_losers(limit=1000, return_data="ticker")

    data = losers[10:20]

    for i in data.iterrows():
        ticker = i[1]['symbol']
        add_new_coin(ticker)




"""
------------------------------------------------------------------------------------------
CSV Management
------------------------------------------------------------------------------------------
"""

def add_new_coin(ticker: str):
    coin = CoinOracle()
    
    coin.add_new_row(ticker)
    cg_id = coin.get_cg_id(ticker)
    coin.write_cg_id_to_csv(ticker, cg_id=cg_id)
    contract_address = coin.get_address_from_cmc(ticker)
    coin.dump_contracts_to_csv(ticker, contracts=contract_address)

def test():
    coin = CoinOracle()
    #coin.get_dex_pairs()
    coin.convert_addresses_to_uppercase()


"""
------------------------------------------------------------------------------------------
WALLET MANAGEMENT
------------------------------------------------------------------------------------------
"""
def update_all_wallets():

    # Create wallet objects for each wallet tracked. 
    op_wallet = OptimismWallet()
    arb_wallet = ArbitrumWallet()
    pol_wallet = PolygonWallet()

    # Update the token balances in the CSV file. 
    op_wallet.update_token_balances()
    arb_wallet.update_token_balances()
    pol_wallet.update_token_balances()

    # Create a snapshot.
    op_wallet.wallet_db.upload_snapshot()
    arb_wallet.wallet_db.upload_snapshot()
    pol_wallet.wallet_db.upload_snapshot()
    


def test3():
    arb = ArbitrageFinder()
    arb.find_arbitrage_routes2("BTC")


if __name__ == "__main__":

    # NOTE: API Rate limit tends to handle 7 tickers. Any more tickers may exceed API.

    tickers = ["PROM", "PYR", "MC", "BLD", "FET", "UNIBOT", "GALA", "MOON", "BRICK"]
    #tickers = ["NMR"]
    
    arbitrage_stager(4, route_limit=10, custom_list=tickers)
    #add_new_coin("GALA")
    #test3()
    #for t in tickers:
     #   add_new_coin(t)