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
from  reserve_asset import convert_crypto_asset_to_addr

def update_cache_reserve_config():
    reseve_list = cache_events.wrapper_getReservesList()
    reserve_config = cache_events.wrapper_getReserveData(reseve_list)
    fname = "{}/reserve_cached.bin".format(CACHE_FOLDER)
    S = {}
    S['reseve_list'] = reseve_list
    S['reserve_config'] = reserve_config
    pickle.dump(S, open(fname, "wb"))
    pass

def load_reserve_from_cache():
    fname = "{}/reserve_cached.bin".format(CACHE_FOLDER)
    S = pickle.load(open(fname, "rb"))
    return S['reseve_list'], S['reserve_config']

"""Collect borrow,repay,swap events for AAVE users"""
def update_cached_events():
    cache_events.update_cache()

"""Cache all active users health factor"""
def check_and_cache_user_health_factor():
    """Load cached events"""
    cached_data, last_cached_block = cache_events.load_events_from_cache()
    borrow = cached_data['Borrow']
    new_cached_user_address = borrow.user.unique()

    """Read latest user cached health factor data"""
    cached_borrowed_accounts, from_cached_block, date, time_of_cache = cache_events.load_latest_health_factor_from_cache()

    """Remove liquidated accounts"""
    I = (cached_borrowed_accounts.col > 0) & (cached_borrowed_accounts.debt > 0)
    alive_borrowed_accounts = cached_borrowed_accounts[I]
    alive_cached_borrowed_accounts = list(alive_borrowed_accounts.user)

    cached_user_account_diff = list(set(new_cached_user_address).difference(cached_borrowed_accounts.user))

    """all user accounts to check for health factor are alive cached and new borrowed"""
    all_user_acounts = alive_cached_borrowed_accounts + cached_user_account_diff
    cache_events.query_user_health_factor_and_cache(user_address=all_user_acounts, last_cached_block=last_cached_block)
    pass

def get_users_for_monitor(threshold=1.1):
    """Read latest user cached health factor data"""
    cached_borrowed_accounts, from_cached_block, date, time_of_cache = cache_events.load_latest_health_factor_from_cache()
    I = (cached_borrowed_accounts.healthFactor < threshold) & (cached_borrowed_accounts.healthFactor > 1.0)
    cached_borrowed_accounts = cached_borrowed_accounts[I]
    return list(cached_borrowed_accounts.user)

def get_chainlink_ratio_from_eth(chainlink_feed_config, to_asset):
    is_direct, address, decimals = chainlink_feed_config[to_asset]
    round_id, price, started_at, timestamp, answered_in_round = chainlink.get_price(address=address, decimals=decimals)
    if is_direct:
        return price
    else:
        return 1.0 / price


def get_user_config(users):
    reserve_list, reserve_config = load_reserve_from_cache()
    User = []
    Col_Type = []
    Borrow_Type = []
    Liquidated_reward = []
    Bonus = []
    Borrow_amount = []
    Col_amount = []
    Liq_threshold = []
    Health_factor = []
    User = []
    chainlink_feed_config = {} #feed address from eth to other asset, direct or inverse!
    is_direct, address = chainlink.get_feed_address(from_asset='ETH', to_asset='USD')
    decimals = chainlink.get_decimals(address)
    chainlink_feed_config['USD'] = [is_direct, address, decimals]
    for user in users:
        user_account = cache_events.wrapper_getUserAccountData([user])
        collateral_type, borrowed_type = cache_events.wrapper_getUserConfiguration(user=user, reserve_to_index=reserve_list)
        if len(borrowed_type) == 1 and len(collateral_type) == 1:
            b_name = borrowed_type[0]
            c_name = collateral_type[0]
            bonus = reserve_config[reserve_config.name == c_name].liq_bonus.values[0]
            max_liquidatable_debt = user_account.debt / 2
            liquidated_reward = max_liquidatable_debt * bonus
            profit_in_eth = liquidated_reward - max_liquidatable_debt
            ratio = get_chainlink_ratio_from_eth(chainlink_feed_config, to_asset='USD')
            profit_in_usd = profit_in_eth * ratio

            if c_name != 'WETH':
                if c_name == 'WBTC':
                    c_name = 'BTC'
                is_direct, address = chainlink.get_feed_address(from_asset='ETH', to_asset=c_name)
                decimals = chainlink.get_decimals(address)
                chainlink_feed_config[c_name] = [is_direct, address, decimals]
                ratio = get_chainlink_ratio_from_eth(chainlink_feed_config, to_asset=c_name)
                col_amount = user_account.debt * ratio  # convert to naitive asset from ETH
            else:
                col_amount = user_account.debt

            if b_name != 'WETH':
                if b_name == 'WBTC':
                    b_name = 'BTC'
                is_direct, address = chainlink.get_feed_address(from_asset='ETH', to_asset=b_name)
                decimals = chainlink.get_decimals(address)
                chainlink_feed_config[b_name] = [is_direct, address, decimals]
                ratio = get_chainlink_ratio_from_eth(chainlink_feed_config, to_asset=b_name)
                borrow_amount = user_account.debt * ratio #convert to naitive asset from ETH
            else:
                borrow_amount = user_account.debt

            print(is_direct, ratio, borrow_amount, 'eth/{}'.format(b_name))

            #my_health_factor = user_account.liquidation_threshold * user_account.col / user_account.debt

            Liquidated_reward.append(liquidated_reward)

            Bonus.append(bonus)
            Col_Type.append(c_name)
            Col_amount.append(col_amount.values[0])
            Borrow_Type.append(b_name)
            Borrow_amount.append(borrow_amount)
            Liq_threshold.append(user_account.liquidation_threshold[0]/100.0)
            Health_factor.append(user_account.healthFactor.values[0])
            User.append(user)
        else:
            print('Skip user due to multiple assets possession!')

    df = pd.DataFrame({'bonus':Bonus,'col_type':Col_Type,'col_amount':Col_amount,
                       'borrow_type':Borrow_Type, 'borrow_amount':Borrow_amount,
                       'liq_threshold':Liq_threshold,'health_factor':Health_factor},
                      index=User)

    return df, chainlink_feed_config



def main():
    #update_cache_reserve_config()
    """snapshot of the health factor for all active users"""
    #update_cached_events()
    #check_and_cache_user_health_factor()
    """monitor most likely liquidable users"""
    users = get_users_for_monitor()
    user_config,chainlink_feed_config  = get_user_config(users)
    pass


if __name__ == '__main__':
    main()