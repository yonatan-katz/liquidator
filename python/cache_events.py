import os
import datetime
import pandas as pd
import pickle
import glob
from web3 import Web3
from web3._utils.abi import get_constructor_abi, merge_args_and_kwargs
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params

import config
import aave_events

CACHE_FOLDER = 'C:/Users/yonic/junk/liquidator/cache'

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

def load_debt_account_from_cache():
    cached_data, last_cached_block = load_from_cache()
    pass



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
            logs = contract.events.Borrow.web3.eth.getLogs(event_filter_params)
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
    update_cache()

