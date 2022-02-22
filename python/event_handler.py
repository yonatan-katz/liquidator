import pandas as pd
import numpy as np
import cache_events
import datetime
import time
import datetime
import chainlink
import chainlink_events
import config
import pickle
import json
from config import CACHE_FOLDER

def load_reserve_from_cache():
    fname = "{}/reserve_cached.bin".format(CACHE_FOLDER)
    S = pickle.load(open(fname, "rb"))
    return S['reseve_list'], S['reserve_config']


def test(from_block):
    events = cache_events.query_liquidation_call_event(from_block=from_block, to_block='latest')
    if events is not None:
        events.to_csv('/home/yonic/junk/liq_events_{}.csv'.format(from_block))
        chainlink_events.query_historic_event_meta(from_block=from_block)


def main():
    reseve_list, reserve_config = load_reserve_from_cache()
    df = pd.read_csv('/home/yonic/junk/chainlink_aggregator_to_eth_20211221.csv', index_col=False)
    cached_borrowed_accounts, from_cached_block, date, time_of_cache = cache_events.load_latest_health_factor_from_cache()
    events = cache_events.query_liquidation_call_event(from_block=13920184, to_block='latest')
    if events is not None:
        events.to_csv('/home/yonic/junk/liq_events_13920184.csv')
        return
        users = list(events.user)
        for n,e in events.iterrows():
            debt_decimals = chainlink.get_decimals(e.debtAsset)
            col_decimals = chainlink.get_decimals(e.collateralAsset)
            debt_to_pay = int(e.debtToCover) / 10 ** debt_decimals
            col_collected = int(e.liquidatedCollateralAmount) / 10 ** col_decimals

            debt_to_eth_price = chainlink.get_price(e.debtAsset, debt_decimals)
            col_to_eth_price = chainlink.get_price(e.collateralAsset, col_decimals)
            reward = col_to_eth_price*col_collected - debt_to_eth_price*debt_to_pay
    pass

if __name__ == '__main__':
    main()
    test(from_block=13920184)
