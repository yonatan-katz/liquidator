import pandas as pd
import numpy as np
import cache_events
import datetime
import datetime
from config import CACHE_FOLDER
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



def test():
    fname = '{}/LiquidationCall_20211123_203253.csv'.format(CACHE_FOLDER,index_col=False)
    lliq_evnt = pd.read_csv(fname)
    fname='{}/updated_not_healthy_accounts_20211123_192440.h5'.format(CACHE_FOLDER)
    df = pd.read_hdf(fname, key='account_health_data')
    pass

if __name__ == '__main__':
    #main()
    test()