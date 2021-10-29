import pandas as pd
import numpy as np
import json
from web3 import Web3
import asyncio

# add your blockchain connection information
infura_url = 'https://mainnet.infura.io/v3/fd3ac79f46ba4500be8e92da9632b476'
web3 = Web3(Web3.HTTPProvider(infura_url))

Lending_Pool_V1_Address = '0x398eC7346DcD622eDc5ae82352F02bE94C62d119'
Lending_Pool_V1_ABI = json.load(open('C:/Users/yonic/repos/liquidator/abi/LendingPool_V1.json'))

Contract = web3.eth.contract(address=Lending_Pool_V1_Address, abi=Lending_Pool_V1_ABI)

# define function to handle events and print to the console
def handle_event(event):
    print(Web3.toJSON(event))
    # and whatever


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        print('log_loop')
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = Contract.events.Borrow.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == '__main__':
    main()


