import pandas as pd
import numpy as np
import cache_events
import datetime
import time
import datetime
import chainlink
import config
import pickle
from config import CACHE_FOLDER
from web3 import Web3

def main():
    #threshold = 1.1
    #cached_borrowed_accounts, from_cached_block, date, time_of_cache = cache_events.load_latest_health_factor_from_cache()
    #I = (cached_borrowed_accounts.healthFactor < threshold) & (cached_borrowed_accounts.healthFactor > 1.0)
    #cached_borrowed_accounts = cached_borrowed_accounts[I]

    asset_addr='0x7476c1bAFb54426B9D893dfb7eeBe8f4DC1dAfF4'
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    #ret = contract.functions.getUserConfiguration(asset_addr).call()

    ret0 = web3.eth.getStorageAt(config.Lending_Pool_V2_Address, 0)
    ret4 = web3.eth.getStorageAt(config.Lending_Pool_V2_Address, 4)

    '''WBTC reserve'''
    #hash = Web3.soliditySha3(['uint256', 'uint256'], [2, 0x7476c1bAFb54426B9D893dfb7eeBe8f4DC1dAfF4])
    #ret1 = web3.eth.getStorageAt(config.Lending_Pool_V2_Address, hash.hex())



    pass

if __name__ == '__main__':
    main()