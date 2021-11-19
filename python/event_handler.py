from web3.auto import w3
from web3 import Web3
import time
import json

import event_monitor

def handle_event(event):
    print(event)
    print(json.loads(event))


def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

def main():
    web3 = Web3(Web3.HTTPProvider(event_monitor.Infura_EndPoint))
    block_filter = web3.eth.filter('latest')
    log_loop(block_filter, 2)

if __name__ == '__main__':
    main()
