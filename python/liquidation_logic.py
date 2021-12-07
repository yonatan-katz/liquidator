import pandas as pd
import numpy as np
import cache_events
import datetime
import time
import datetime
import chainlink
from config import CACHE_FOLDER
from  reserve_asset import convert_crypto_asset_to_addr
import matplotlib.pyplot as plt


def main():
    reserves = cache_events.wrapper_getReservesList()
    reserve_config = cache_events.wrapper_getConfiguration(reserves)
    reserve_config = reserve_config.set_index(reserve_config.addr).drop('addr', axis=1)
    pass
    borrowed_accounts, from_cached_block, date, time = cache_events.load_latest_health_factor_from_cache()
    liquidated_events = cache_events.query_liquidation_call_event(from_block=from_cached_block,
                                                                  to_block='latest')
    liquidated_events = liquidated_events.set_index(liquidated_events.user)
    ###
    #liquidated_account = df.set_index(df.user).loc[liquidated_events.user]
    #liquidated_account_status = cache_events.wrapper_getUserAccountData(liquidated_account.user.values)
    ###
    '''Remove liquidated accounts'''
    I = (borrowed_accounts.col > 0) & (borrowed_accounts.debt > 0)
    alive_borrowed_accounts = borrowed_accounts[I]
    alive_borrowed_accounts = alive_borrowed_accounts.set_index(alive_borrowed_accounts.user).drop('user', axis=1)
    '''List not healthy accounts'''
    not_healthy_accounts = alive_borrowed_accounts[alive_borrowed_accounts.healthFactor < 1.0]
    t1 = datetime.datetime.now()
    updated_not_healthy_accounts = cache_events.wrapper_getUserAccountData(list(not_healthy_accounts.index.values))
    t2 = datetime.datetime.now()
    call_time = (t2 - t1).total_seconds()

    updated_not_healthy_accounts = updated_not_healthy_accounts.set_index(updated_not_healthy_accounts.user).drop('user', axis=1)

    '''Calculate liquidation reward'''
    Liquidated_reward = []
    for user, v in updated_not_healthy_accounts.iterrows():
        collateral, borrowed = cache_events.wrapper_getUserConfiguration(user, reserves)
        bonus = []
        for c_name in collateral:
            b = reserve_config[reserve_config.name == c_name].liq_bonus.values[0]
            bonus.append(b)
        print(user, bonus)
        bonus = np.mean(bonus) / 100.0  # assuming qually weighted!
        max_liquidatable_debt = v.debt / 2
        liquidated_reward = max_liquidatable_debt * bonus
        Liquidated_reward.append(liquidated_reward)

    updated_not_healthy_accounts['liquidated_reward'] = Liquidated_reward

    now = datetime.datetime.now()
    updated_not_healthy_accounts.to_hdf('{}/updated_not_healthy_accounts_{}.h5'.format(CACHE_FOLDER, now.strftime("%Y%m%d_%H%M%S")),key='account_health_data')
    pass
    '''
    healed_not_healthy_accounts = updated_not_healthy_accounts[updated_not_healthy_accounts.healthFactor > 1.0]
    liquidated_not_healthy_accounts = set(liquidated_events.index).intersection(updated_not_healthy_accounts.index)


    print('borrowed accounts:{},not healthy:{}, healed:{}, liquidated:{}'.
          format(
                 len(alive_borrowed_accounts),
                 len(not_healthy_accounts),
                 len(healed_not_healthy_accounts),
                 len(liquidated_not_healthy_accounts)))

    '''
    pass



def test1():
    fname = '{}/LiquidationCall_20211123_203253.csv'.format(CACHE_FOLDER,index_col=False)
    lliq_evnt = pd.read_csv(fname)
    fname='{}/updated_not_healthy_accounts_20211123_192440.h5'.format(CACHE_FOLDER)
    df = pd.read_hdf(fname, key='account_health_data')
    pass

def test2():
    user = '0x763bF487D386AFBf9c476e047D37B74636B9e831'
    reserves = cache_events.wrapper_getReservesList()
    reserve_config = cache_events.wrapper_getReserveData(reserves)
    reserve_config = reserve_config.set_index(reserve_config.addr).drop('addr', axis=1)
    collateral_type, borrowed_type = cache_events.wrapper_getUserConfiguration(user=user, reserve_to_index=reserves)
    user_account = cache_events.wrapper_getUserAccountData([user])
    if len(collateral_type) == 1 and len(borrowed_type) == 1:
        col_asset_name = collateral_type[0]
        borrow_asset_name = borrowed_type[0]
        col_reserve_config = reserve_config[reserve_config.name == col_asset_name]
        debt_reserve_config = reserve_config[reserve_config.name == borrow_asset_name]
        liq_bonus = col_reserve_config.liq_bonus.values[0]
        col_reserve_addr = col_reserve_config.index.values[0]
        debt_reserve_addr = debt_reserve_config.index.values[0]

    col_to_eth_contract_addr = chainlink.get_contract_addr_from_local_reg(base=collateral_type[0], quote='ETH')
    debt_to_eth_contract_addr = chainlink.get_contract_addr_from_local_reg(base=borrowed_type[0], quote='ETH')

    col_to_eth_decimals = chainlink.get_decimals(col_to_eth_contract_addr)
    debt_to_eth_decimals = chainlink.get_decimals(debt_to_eth_contract_addr)

    round_id, col_to_eth_price, started_at,timestamp, answered_in_round = chainlink.get_price(address=col_to_eth_contract_addr, decimals=col_to_eth_decimals)
    round_id, debt_to_eth_price, started_at,timestamp, answered_in_round = chainlink.get_price(address=debt_to_eth_contract_addr, decimals=debt_to_eth_decimals)

    print('col:{}, to ETH price:{}'.format(col_asset_name, col_to_eth_price))
    print('debt:{}, to ETH price:{}'.format(borrow_asset_name, debt_to_eth_price))

    for i in range(100):
        ret = cache_events.wrapper_getUserAccountData([user])
        print(ret[['debt','healthFactor']])
        time.sleep(1)
    pass

def test3():
    fname='C:/Users/yonic/junk/liquidator/liquidation_calls.csv'
    df = pd.read_csv(fname, index_col=0)
    #assuming average block time is 13 seconds, there are on average 3600*24 / 13 = 6646 blocks in a day
    start_block = df.block_number[0] #13648625 - 17 days 16 hrs ago (Nov-19-2021 11:59:22 PM +UTC)
    end_block = df.block_number[-1]
    #df.block_number = block_number - start_block
    bins = range(start_block-6646,end_block+6646,6646)
    labels = range(len(bins))
    cuted = pd.cut(df.block_number.values, bins=bins, labels=range(len(bins)-1))
    bincount = np.bincount(cuted.codes)
    now = datetime.datetime.now()
    date_range = pd.date_range('Nov-20-2021', now)
    pd.DataFrame({'Events':bincount},index=date_range).plot()
    plt.show()
    pass

if __name__ == '__main__':
    #main()
    #test1()
    #test2()#evaluate health factor of the user
    test3()
