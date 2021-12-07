import os
import datetime
import numpy as np
import pandas as pd
import pickle
import glob
from web3 import Web3
from web3._utils.abi import get_constructor_abi, merge_args_and_kwargs
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params

from reserve_asset import convert_addr_in_crypto_asset
from reserve_asset import split_user_loan_deposit_bitmask
from reserve_asset import split_asset_config_bitmask

import config
from config import CACHE_FOLDER
import aave_events


def make_event_handler(event, from_block, to_block):
    abi = event._get_event_abi()
    abi_codec = event.web3.codec
    argument_filters = dict()
    _filters = dict(**argument_filters)
    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=event.address,
        argument_filters=_filters,
        fromBlock=from_block,
        toBlock=to_block,
        address=None,
        topics=None,
    )

    return event_filter_params, abi, abi_codec


def get_latest_block_meta():
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    latest_block_meta = web3.eth.get_block('latest')
    return latest_block_meta

def load_from_cache():
    cached_block_to_fname = {}
    for fname in glob.glob('{}/cached_events_*.bin'.format(CACHE_FOLDER)):
        block = int(fname.split('_')[-1].split('.')[0])
        cached_block_to_fname[block] = fname

    if len(cached_block_to_fname) > 0:
        cached_blocks = sorted(cached_block_to_fname.keys())
        last_cached_block = cached_blocks[-1]
        print('Load cached data from:{}'.format(cached_block_to_fname[last_cached_block]))
        cached_data = pickle.load(open(cached_block_to_fname[last_cached_block],'rb'))
    else:
        cached_data = None, None

    return cached_data, last_cached_block

def wrapper_getUserAccountData(user_address):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address,
                                 abi=config.Lending_Pool_V2_ABI)
    user_account = []
    for user in user_address:
        S = {}
        ret = contract.functions.getUserAccountData(user).call()
        S['col'] = [ret[0] / 1e18]
        S['debt'] = ret[1] / 1e18
        S['availableBorrow'] = ret[2] / 1e18
        S['liquidation_threshold'] = ret[3] / 100.0
        S['ltv'] = ret[4] / 100.0
        S['healthFactor'] = ret[5] / 1e18
        S['user'] = user
        df = pd.DataFrame(S)
        user_account.append(df)

    df = pd.concat(user_account)
    return df

'''Get assets index'''
def wrapper_getReservesList():
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    reserve_to_index = []
    ret = contract.functions.getReservesList().call()
    for i in range(len(ret)):
        #print('reserved asset:',convert_addr_in_crypto_asset(ret[i]))
        reserve_to_index.append(ret[i])

    return reserve_to_index
'''Call getConfiguration, input args:
   @reserve_to_index - list of the AAVE reserve asset from getReservesList() function!
   Returns reserve asset configuratios
'''
def wrapper_getConfiguration(reserve_to_index):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    S = {}
    c = []
    for asset_addr in reserve_to_index:
        ret = contract.functions.getConfiguration(asset_addr).call()
        print("asset:{}, config:{}".format(convert_addr_in_crypto_asset(asset_addr), ret[0]))
        ltv, liq_threshold, liq_bonus, decimals = split_asset_config_bitmask(ret[0])
        asset_name = convert_addr_in_crypto_asset(asset_addr)
        S['name'] = [asset_name]
        S['addr'] = [asset_addr]
        S['ltv'] = [ltv]
        S['liq_threshold'] = [liq_threshold]
        S['liq_bonus'] = [liq_bonus]
        S['decimals'] = [decimals]
        df = pd.DataFrame(S)
        c.append(df)
    c = pd.concat(c)
    return c

'''18447685934079306374476'''
def wrapper_getReserveData(reserve_to_index):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    S = {}
    c = []
    for asset_addr in reserve_to_index:
        ret = contract.functions.getReserveData(asset_addr).call()
        print("asset:{}, config:{}".format(convert_addr_in_crypto_asset(asset_addr), ret[0][0]))
        ltv, liq_threshold, liq_bonus, decimals = split_asset_config_bitmask(ret[0][0])
        asset_name = convert_addr_in_crypto_asset(asset_addr)
        S['name'] = [asset_name]
        S['addr'] = [asset_addr]
        S['ltv'] = [ltv]
        S['liq_threshold'] = [liq_threshold]
        S['liq_bonus'] = [liq_bonus]
        S['decimals'] = [decimals]
        S['variable_rate'] = ret[4]/1e27
        S['stable_rate'] = ret[5] / 1e27
        df = pd.DataFrame(S)
        c.append(df)
    c = pd.concat(c)
    return c


''' Call getUserConfiguration, input args:
    @user AAVE protocol user address
    @reserve_to_index - list of the AAVE reserve asset from getReservesList() function!    
    Returns list of the borrowed and collateral assets for the user
    https://docs.aave.com/developers/the-core-protocol/lendingpool
'''
def wrapper_getUserConfiguration(user, reserve_to_index):
    '''Get user asset config'''
    borrowed = []
    collateral = []
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    ret = contract.functions.getUserConfiguration(user).call()
    s = split_user_loan_deposit_bitmask(ret[0])
    for k in s.keys():
        is_col, is_borrowed = s[k]
        asset_addr = reserve_to_index[k]
        asset_name = convert_addr_in_crypto_asset(asset_addr)
        if is_col:
            collateral.append(asset_name)
        if is_borrowed:
            borrowed.append(asset_name)

    return collateral, borrowed

def query_liquidation_call_event(from_block, to_block='latest'):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    event_name = 'LiquidationCall'
    event_handler = aave_events.handle_liquidation_call
    event = getattr(contract.events, event_name)
    event_filter_params, abi, abi_codec = make_event_handler(event=event,
        from_block=from_block, to_block=to_block)
    logs = contract.events.Borrow.web3.eth.getLogs(event_filter_params)
    collected_events = []
    for entry in logs:
        data = dict(get_event_data(abi_codec, abi, entry))
        block_number = data['blockNumber']
        transaction_hash = data['transactionHash'].hex()
        d = event_handler(event_data=dict(data['args']))
        d['block_number'] = [block_number]
        d['transaction_hash'] = [transaction_hash]
        df = pd.DataFrame(d)
        collected_events.append(df)

    if len(collected_events) > 0:
        collected_events = pd.concat(collected_events)
    else:
        collected_events = None

    return collected_events



def query_user_health_factor_from_cache():
    cached_data, last_cached_block = load_from_cache()
    borrow  = cached_data['Borrow']
    user_address = borrow.user.unique()
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address,
                                 abi=config.Lending_Pool_V2_ABI)
    user_account = []
    t1 = datetime.datetime.now()
    for user in user_address:
        S = {}
        ret = contract.functions.getUserAccountData(user).call()
        S['col'] = [ret[0]/1e18]
        S['debt'] = [ret[1]/1e18]
        S['available'] = [ret[2]/1e18]
        S['liquidation_threshold'] = [ret[3] / 100.0]
        S['ltv'] = [ret[4] / 100.0]
        S['healthFactor'] = [ret[5] / 1e18]
        S['user'] = [user]

        df = pd.DataFrame(S)
        user_account.append(df)
    t2 = datetime.datetime.now()
    print('time:{}'.format((t2 - t1).total_seconds()))
    user_account = pd.concat(user_account)
    now = datetime.datetime.now()
    user_account.to_hdf('{}/user_data_{}_{}.h5'.format(CACHE_FOLDER, now.strftime("%Y%m%d_%H%M%S"), last_cached_block),
                        key='user_account')
    pass

''' Cached health factor over all cached borrowd accounts
    date and time is when getUserAccountData() called,
    latest_cached_block is when account list is created!
'''
def load_latest_health_factor_from_cache():
    S = {}
    for fname in glob.glob('{}/user_data_*.h5'.format(CACHE_FOLDER)):
        date = int(fname.split('_')[-3])
        time = int(fname.split('_')[-2])
        block = int(fname.split('_')[-1].split('.')[0])
        S[block] = (fname, date, time)

    latest_cached_block = sorted(S.keys())[-1]
    fname = S[latest_cached_block][0]
    date = S[latest_cached_block][1]
    time = S[latest_cached_block][2]
    df = pd.read_hdf(fname, key='user_account')
    return df, latest_cached_block, date, time



def update_cache():
    event_handlers = {'Borrow': aave_events.handle_borrow,
                      'Repay': aave_events.handle_repay,
                      'Swap':  aave_events.handle_swap}
    event_cache, from_block = load_from_cache()
    if from_block is None:
        from_block = 11363357 #Dec-01-2020 12:17:34
        event_cache = {}
        print('Empty cache!')

    latest_block_meta = get_latest_block_meta()
    latest_block = latest_block_meta['number']
    print('Collect event from: {} to {}'.format(from_block, latest_block))

    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    blocks_for_query = list(range(from_block, latest_block, 100000))
    blocks_for_query.append(latest_block)
    for i in range(len(blocks_for_query)-1):
        t1 = datetime.datetime.now()
        b1 = blocks_for_query[i]
        b2 = blocks_for_query[i+1]
        for event_name in event_handlers.keys():
            event = getattr(contract.events, event_name)
            event_filter_params, abi, abi_codec = make_event_handler(event=event, from_block=b1, to_block=b2)
            #logs = contract.events.Borrow.web3.eth.getLogs(event_filter_params)
            logs = event.web3.eth.getLogs(event_filter_params)
            collected_events = []
            for entry in logs:
                data = dict(get_event_data(abi_codec, abi, entry))
                block_number = data['blockNumber']
                transaction_hash = data['transactionHash'].hex()
                d = event_handlers[event_name](event_data=dict(data['args']))
                d['block_number'] = [block_number]
                d['transaction_hash'] = [transaction_hash]
                df = pd.DataFrame(d)
                collected_events.append(df)

            if len(collected_events) > 0:
                collected_events = pd.concat(collected_events)
                if event_name in event_cache:
                    event_cache[event_name] = pd.concat([event_cache[event_name], collected_events], ignore_index=True)
                else:
                    event_cache[event_name] = df
        t2 = datetime.datetime.now()
        query_time = t2 - t1
        print('query start:{}, stop:{}, time:{}'.format(b1, b2, query_time.total_seconds()))
        fname = '{}/cached_events_{}_{}.bin'.format(CACHE_FOLDER, t2.strftime("%Y%m%d"), b2)
        pickle.dump(event_cache, open(fname, 'wb'))


    now = datetime.datetime.now()
    fname = '{}/cached_events_{}_{}.bin'.format(CACHE_FOLDER, now.strftime("%Y%m%d"), latest_block)
    pickle.dump(event_cache, open(fname, 'wb'))
    pass

if __name__ == '__main__':
    #update_cache()
    #query_user_health_factor_from_cache()
    wrapper_getReserveData(['0x6B175474E89094C44Da98b954EedeAC495271d0F'])


