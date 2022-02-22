import config
from config import CACHE_FOLDER
import pandas as pd
import numpy as np
import pickle
import json
import chainlink
import aave_events
import cache_events
import bot_v1
from web3 import Web3
from ens import ENS
import matplotlib.pyplot as plt
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params


def main():
    ETH_USD = Web3.toChecksumAddress('0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419')
    ETH_USDT = '0x7De0d6fce0C128395C488cb4Df667cdbfb35d7DE'
    round_id, price, started_at, timestamp, answered_in_round = chainlink.get_price_from_aggregator(agg_addr=ETH_USD)
    print('ETH_USD:{}'.format(price))

    round_id, price, started_at, timestamp, answered_in_round = chainlink.get_price_from_aggregator(agg_addr=ETH_USDT)
    print('ETH_USDT:{}'.format(price))
    pass


if __name__ == '__main__':
    main()