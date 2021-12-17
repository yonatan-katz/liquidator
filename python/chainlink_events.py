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


AccessControlledOffchainAggregator_ABI='[{"inputs":[{"internalType":"uint32","name":"_maximumGasPrice","type":"uint32"},{"internalType":"uint32","name":"_reasonableGasPrice","type":"uint32"},{"internalType":"uint32","name":"_microLinkPerEth","type":"uint32"},{"internalType":"uint32","name":"_linkGweiPerObservation","type":"uint32"},{"internalType":"uint32","name":"_linkGweiPerTransmission","type":"uint32"},{"internalType":"address","name":"_link","type":"address"},{"internalType":"int192","name":"_minAnswer","type":"int192"},{"internalType":"int192","name":"_maxAnswer","type":"int192"},{"internalType":"contract AccessControllerInterface","name":"_billingAccessController","type":"address"},{"internalType":"contract AccessControllerInterface","name":"_requesterAccessController","type":"address"},{"internalType":"uint8","name":"_decimals","type":"uint8"},{"internalType":"string","name":"description","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"user","type":"address"}],"name":"AddedAccess","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"int256","name":"current","type":"int256"},{"indexed":true,"internalType":"uint256","name":"roundId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"updatedAt","type":"uint256"}],"name":"AnswerUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"contract AccessControllerInterface","name":"old","type":"address"},{"indexed":false,"internalType":"contract AccessControllerInterface","name":"current","type":"address"}],"name":"BillingAccessControllerSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"maximumGasPrice","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"reasonableGasPrice","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"microLinkPerEth","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"linkGweiPerObservation","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"linkGweiPerTransmission","type":"uint32"}],"name":"BillingSet","type":"event"},{"anonymous":false,"inputs":[],"name":"CheckAccessDisabled","type":"event"},{"anonymous":false,"inputs":[],"name":"CheckAccessEnabled","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"previousConfigBlockNumber","type":"uint32"},{"indexed":false,"internalType":"uint64","name":"configCount","type":"uint64"},{"indexed":false,"internalType":"address[]","name":"signers","type":"address[]"},{"indexed":false,"internalType":"address[]","name":"transmitters","type":"address[]"},{"indexed":false,"internalType":"uint8","name":"threshold","type":"uint8"},{"indexed":false,"internalType":"uint64","name":"encodedConfigVersion","type":"uint64"},{"indexed":false,"internalType":"bytes","name":"encoded","type":"bytes"}],"name":"ConfigSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"roundId","type":"uint256"},{"indexed":true,"internalType":"address","name":"startedBy","type":"address"},{"indexed":false,"internalType":"uint256","name":"startedAt","type":"uint256"}],"name":"NewRound","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"aggregatorRoundId","type":"uint32"},{"indexed":false,"internalType":"int192","name":"answer","type":"int192"},{"indexed":false,"internalType":"address","name":"transmitter","type":"address"},{"indexed":false,"internalType":"int192[]","name":"observations","type":"int192[]"},{"indexed":false,"internalType":"bytes","name":"observers","type":"bytes"},{"indexed":false,"internalType":"bytes32","name":"rawReportContext","type":"bytes32"}],"name":"NewTransmission","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"transmitter","type":"address"},{"indexed":false,"internalType":"address","name":"payee","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"OraclePaid","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferRequested","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"transmitter","type":"address"},{"indexed":true,"internalType":"address","name":"current","type":"address"},{"indexed":true,"internalType":"address","name":"proposed","type":"address"}],"name":"PayeeshipTransferRequested","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"transmitter","type":"address"},{"indexed":true,"internalType":"address","name":"previous","type":"address"},{"indexed":true,"internalType":"address","name":"current","type":"address"}],"name":"PayeeshipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"user","type":"address"}],"name":"RemovedAccess","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"contract AccessControllerInterface","name":"old","type":"address"},{"indexed":false,"internalType":"contract AccessControllerInterface","name":"current","type":"address"}],"name":"RequesterAccessControllerSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"requester","type":"address"},{"indexed":false,"internalType":"bytes16","name":"configDigest","type":"bytes16"},{"indexed":false,"internalType":"uint32","name":"epoch","type":"uint32"},{"indexed":false,"internalType":"uint8","name":"round","type":"uint8"}],"name":"RoundRequested","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"contract AggregatorValidatorInterface","name":"previousValidator","type":"address"},{"indexed":false,"internalType":"uint32","name":"previousGasLimit","type":"uint32"},{"indexed":true,"internalType":"contract AggregatorValidatorInterface","name":"currentValidator","type":"address"},{"indexed":false,"internalType":"uint32","name":"currentGasLimit","type":"uint32"}],"name":"ValidatorConfigSet","type":"event"},{"inputs":[],"name":"LINK","outputs":[{"internalType":"contract LinkTokenInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_transmitter","type":"address"}],"name":"acceptPayeeship","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"addAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"billingAccessController","outputs":[{"internalType":"contract AccessControllerInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"checkEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"disableAccessCheck","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"enableAccessCheck","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_roundId","type":"uint256"}],"name":"getAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getBilling","outputs":[{"internalType":"uint32","name":"maximumGasPrice","type":"uint32"},{"internalType":"uint32","name":"reasonableGasPrice","type":"uint32"},{"internalType":"uint32","name":"microLinkPerEth","type":"uint32"},{"internalType":"uint32","name":"linkGweiPerObservation","type":"uint32"},{"internalType":"uint32","name":"linkGweiPerTransmission","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_roundId","type":"uint256"}],"name":"getTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"bytes","name":"_calldata","type":"bytes"}],"name":"hasAccess","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestAnswer","outputs":[{"internalType":"int256","name":"","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestConfigDetails","outputs":[{"internalType":"uint32","name":"configCount","type":"uint32"},{"internalType":"uint32","name":"blockNumber","type":"uint32"},{"internalType":"bytes16","name":"configDigest","type":"bytes16"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRound","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestTransmissionDetails","outputs":[{"internalType":"bytes16","name":"configDigest","type":"bytes16"},{"internalType":"uint32","name":"epoch","type":"uint32"},{"internalType":"uint8","name":"round","type":"uint8"},{"internalType":"int192","name":"latestAnswer","type":"int192"},{"internalType":"uint64","name":"latestTimestamp","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"linkAvailableForPayment","outputs":[{"internalType":"int256","name":"availableBalance","type":"int256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maxAnswer","outputs":[{"internalType":"int192","name":"","type":"int192"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minAnswer","outputs":[{"internalType":"int192","name":"","type":"int192"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_signerOrTransmitter","type":"address"}],"name":"oracleObservationCount","outputs":[{"internalType":"uint16","name":"","type":"uint16"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_transmitter","type":"address"}],"name":"owedPayment","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"removeAccess","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"requestNewRound","outputs":[{"internalType":"uint80","name":"","type":"uint80"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"requesterAccessController","outputs":[{"internalType":"contract AccessControllerInterface","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint32","name":"_maximumGasPrice","type":"uint32"},{"internalType":"uint32","name":"_reasonableGasPrice","type":"uint32"},{"internalType":"uint32","name":"_microLinkPerEth","type":"uint32"},{"internalType":"uint32","name":"_linkGweiPerObservation","type":"uint32"},{"internalType":"uint32","name":"_linkGweiPerTransmission","type":"uint32"}],"name":"setBilling","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract AccessControllerInterface","name":"_billingAccessController","type":"address"}],"name":"setBillingAccessController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_signers","type":"address[]"},{"internalType":"address[]","name":"_transmitters","type":"address[]"},{"internalType":"uint8","name":"_threshold","type":"uint8"},{"internalType":"uint64","name":"_encodedConfigVersion","type":"uint64"},{"internalType":"bytes","name":"_encoded","type":"bytes"}],"name":"setConfig","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address[]","name":"_transmitters","type":"address[]"},{"internalType":"address[]","name":"_payees","type":"address[]"}],"name":"setPayees","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract AccessControllerInterface","name":"_requesterAccessController","type":"address"}],"name":"setRequesterAccessController","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract AggregatorValidatorInterface","name":"_newValidator","type":"address"},{"internalType":"uint32","name":"_newGasLimit","type":"uint32"}],"name":"setValidatorConfig","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_transmitter","type":"address"},{"internalType":"address","name":"_proposed","type":"address"}],"name":"transferPayeeship","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"_report","type":"bytes"},{"internalType":"bytes32[]","name":"_rs","type":"bytes32[]"},{"internalType":"bytes32[]","name":"_ss","type":"bytes32[]"},{"internalType":"bytes32","name":"_rawVs","type":"bytes32"}],"name":"transmit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"transmitters","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"typeAndVersion","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"},{"inputs":[],"name":"validatorConfig","outputs":[{"internalType":"contract AggregatorValidatorInterface","name":"validator","type":"address"},{"internalType":"uint32","name":"gasLimit","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdrawFunds","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_transmitter","type":"address"}],"name":"withdrawPayment","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

'''ETH/USD aggregator address'''
AccessControlledOffchainAggregator_Address ='0x37bC7498f4FF12C19678ee8fE19d713b87F6a9e6'

ETH_addr = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

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

def handle_event(event_data, block, tx_hash, decimals):
    print(block, tx_hash, event_data)
    price = event_data['answer']/10**decimals
    return price

def query_chainlink_event(aggregator_addr, from_block, to_block):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=aggregator_addr, abi=AccessControlledOffchainAggregator_ABI)
    decimals = contract.functions.decimals().call()
    #event_name = 'AnswerUpdated'
    event_name = 'NewTransmission'
    event_handler = handle_event
    event = getattr(contract.events, event_name)
    event_filter_params, abi, abi_codec = make_event_handler(event=event,
                                                             from_block=from_block,
                                                             to_block=to_block)
    logs = event.web3.eth.getLogs(event_filter_params)
    if len(logs) > 0:
        for entry in logs:
            data = dict(get_event_data(abi_codec, abi, entry))
            block_number = data['blockNumber']
            tx_hash = data['transactionHash'].hex()
            price = event_handler(block=block_number, tx_hash=tx_hash, event_data=dict(data['args']), decimals=decimals)
        return block_number, price
    else:
        return None,None

def query_aave_liquidation_event(from_block, to_block):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=config.Lending_Pool_V2_Address, abi=config.Lending_Pool_V2_ABI)
    event = getattr(contract.events, 'LiquidationCall')
    event_filter_params, abi, abi_codec = make_event_handler(event=event, from_block=from_block, to_block=to_block)
    logs = event.web3.eth.getLogs(event_filter_params)
    collected_events = []
    for entry in logs:
        data = dict(get_event_data(abi_codec, abi, entry))
        block_number = data['blockNumber']
        transaction_hash = data['transactionHash'].hex()
        block_number = data['blockNumber']
        transaction_hash = data['transactionHash'].hex()
        d = aave_events.handle_liquidation_call(event_data=dict(data['args']))
        d['block_number'] = [block_number]
        d['transaction_hash'] = [transaction_hash]
        df = pd.DataFrame(d)
        collected_events.append(df)

    collected_events = pd.concat(collected_events)
    return collected_events


def query_chainlink_state(aggregator_addr):
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=aggregator_addr,
                                 abi=AccessControlledOffchainAggregator_ABI)

    ret = contract.functions.description().call()
    print(ret)
    decimals = contract.functions.decimals().call()

    ret = contract.functions.latestRoundData().call()
    round_id, price, started_at, timestamp, answered_in_round = ret
    print(round_id, price, price / 10 ** decimals, started_at, timestamp, answered_in_round)

"""Find chainlink oracale aggregator
   Input args: base, quote
   Return: aggregator address
   Examples for ETH/USD base='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 
    quite='0x0000000000000000000000000000000000000348' based on https://en.wikipedia.org/wiki/ISO_4217
"""
def get_aggregator(base, quote):
    abi = chainlink.CHAIN_LINK_FEED_REG_ABI
    address = chainlink.CHAIN_LINK_FEED_REG_ADDR
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    contract = web3.eth.contract(address=address, abi=abi)
    aggregator = contract.functions.getFeed(base=base, quote=quote).call()
    return aggregator

def test1():
    aggregator = get_aggregator(base='0x6B175474E89094C44Da98b954EedeAC495271d0F',
                                quote='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
    print(aggregator)
    event_block = 13562896
    query_chainlink_event(aggregator_addr=aggregator, from_block=event_block-15, to_block=event_block+1)


def test2():

    def find_pair_aggregator(base, quote):
        try:
            aggregator = get_aggregator(base=base, quote=quote)
            failed = False
            direct = True
        except:
            failed = True

        if failed:
            try:
                aggregator = get_aggregator(base=quote, quote=base)
                failed = False
                direct = False
            except:
                failed = True

        if not failed:
            return direct, aggregator
        else:
            return None, None

    def convert_to_eth(ratio, is_direct, amount):
        if is_direct:
            return amount * ratio
        else:
            return amount / ratio

    reserve_list, reserve_config = bot_v1.load_reserve_from_cache()
    def reserve_name_to_add(name):
        return reserve_config[reserve_config.name == name].addr.values[0]

    def find_chainlink_update_block(asset_addr, from_block, to_block):
        if asset_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':
            asset_addr = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        if asset_addr == '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599':
            asset_addr = '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'

        if asset_addr != ETH_addr:
            direct, aggregator = find_pair_aggregator(base=asset_addr, quote=ETH_addr)

            if aggregator is not None:
                block, _ = query_chainlink_event(aggregator_addr=aggregator,from_block=from_block,to_block=to_block)
                return block
            else:
                return None


    #liq_events = query_aave_liquidation_event(from_block=13393888, to_block='latest')
    #liq_events.to_csv("{}/liq_events_for_test.csv".format('C:/Users/yonic/junk/liquidator/cache'))
    liq_events = pd.read_csv("{}/liq_events_for_test.csv".format(CACHE_FOLDER),
                             index_col=False)

    blocks_diff = []
    missed_index = []
    Profit = []
    Blocks = []
    Tx = []

    for n, g in liq_events.iterrows():
        print(n)
        collateral, borrowed = cache_events.wrapper_getUserConfiguration(g.user, reserve_list)
        C = []
        B = []
        for c in collateral:
            C.append(reserve_name_to_add(c))
        for b in borrowed:
            B.append(reserve_name_to_add(b))

        col_addr = g.collateralAsset
        debt_addr = g.debtAsset
        liq_block = g.block_number
        debt_to_eth_price = None
        col_to_eth_price = None

        more_col_assets = list(set(C).difference([col_addr]))
        more_debt_assets = list(set(B).difference([debt_addr]))

        """chainlink uses ETH instead of WETH"""
        if col_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':
            col_addr = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        if col_addr == '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599':
            col_addr = '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'

        if debt_addr == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2':
            debt_addr = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

        if debt_addr == '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599':
            debt_addr = '0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB'

        if debt_addr != ETH_addr:
            debt_to_eth = find_pair_aggregator(base=debt_addr, quote=ETH_addr)
        else:
            debt_to_eth = [True, None]
            debt_to_eth_price = 1.0


        if col_addr != ETH_addr:
            col_to_eth = find_pair_aggregator(base=col_addr, quote=ETH_addr)
        else:
            col_to_eth = [True, None]
            col_to_eth_price = 1.0

        chainlink_link_debt_block = None
        chainlink_link_col_block = None

        if debt_to_eth[1] is not None:
            chainlink_link_debt_block, debt_to_eth_price = query_chainlink_event(aggregator_addr=debt_to_eth[1],
                                                                                 from_block=liq_block-1600,
                                                                                 to_block=liq_block)

        if col_to_eth[1] is not None:
            chainlink_link_col_block, col_to_eth_price = query_chainlink_event(aggregator_addr=col_to_eth[1],
                                                                               from_block=liq_block-1600,
                                                                               to_block=liq_block)

        chainlink_link_latest_block = None
        if chainlink_link_debt_block is not None and chainlink_link_col_block is not None:
            chainlink_link_latest_block = max(chainlink_link_col_block, chainlink_link_debt_block)
        elif chainlink_link_debt_block is not None:
            chainlink_link_latest_block = chainlink_link_debt_block
        elif chainlink_link_col_block is not None:
            chainlink_link_latest_block = chainlink_link_col_block


        if chainlink_link_latest_block is not None:
            for col_asset in more_col_assets:
                b = find_chainlink_update_block(asset_addr=col_asset, from_block=liq_block - 1600, to_block=liq_block)
                if b is not None:
                    chainlink_link_latest_block = max(chainlink_link_latest_block, b)

            for debt_asset in more_debt_assets:
                b = find_chainlink_update_block(asset_addr=debt_asset, from_block=liq_block - 1600, to_block=liq_block)
                if b is not None:
                    chainlink_link_latest_block = max(chainlink_link_latest_block, b)

            blocks_diff.append(liq_block - chainlink_link_latest_block)

            debt_decimals = chainlink.get_decimals(g.debtAsset)
            col_decimals = chainlink.get_decimals(g.collateralAsset)
            debt_to_pay = int(g.debtToCover) / 10**debt_decimals
            col_collected = int(g.liquidatedCollateralAmount) / 10**col_decimals

            if debt_to_eth_price is not None and col_to_eth_price is not None:
                debt_to_pay_eth = convert_to_eth(ratio=debt_to_eth_price, is_direct=debt_to_eth[0], amount=debt_to_pay)
                collected_col_eth = convert_to_eth(ratio=col_to_eth_price, is_direct=col_to_eth[0], amount=col_collected)
                profit = collected_col_eth - debt_to_pay_eth
                print(liq_block-chainlink_link_latest_block, profit)
                Profit.append(profit)
                Blocks.append(liq_block-chainlink_link_latest_block)
                Tx.append(g.transaction_hash)
        else:
            missed_index.append(n)



    df = pd.DataFrame({'profit':Profit, 'blocks_from_oracle_update':Blocks, 'tx':Tx})
    fname = "{}/liq_events_latency_multi_leg.csv".format(CACHE_FOLDER)
    df.to_csv(fname)
    pass

def test3():
    fname = "{}/liq_events_latency_multi_leg.csv".format(CACHE_FOLDER)
    df = pd.read_csv(fname, index_col=False)
    tx = '0xb8962849cb82425248d1e3af10718439d15b71504031856af16d3dabef70c932'
    web3 = Web3(Web3.HTTPProvider(config.Infura_EndPoint))
    Gas_payed = []
    for n, g in df.iterrows():
        tx = g.tx
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx)
        gas_payed = tx_receipt['gasUsed'] * tx_receipt['effectiveGasPrice'] / 10 ** 18
        Gas_payed.append(gas_payed)
    df['gas_payed'] = Gas_payed
    fname = "{}/liq_events_latency_multi_leg_with_gas.csv".format(CACHE_FOLDER)
    df.to_csv(fname)
    pass

def test4():
    fname = "{}/liq_events_latency_multi_leg_with_gas.csv".format(CACHE_FOLDER)
    df_multi = pd.read_csv(fname, index_col=False)

    fname = "{}/liq_events_latency_with_gas.csv".format(CACHE_FOLDER)
    df = pd.read_csv(fname, index_col=False)
    pass




if __name__ == '__main__':
    #test2()
    #test3()
    test4()



