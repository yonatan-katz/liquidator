import json
import datetime
from web3 import Web3
from web3._utils.abi import get_constructor_abi, merge_args_and_kwargs
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3._utils.contracts import encode_abi

from crypto_utils import convert_wei_to_eth
from reserve_asset import CRYPTO_ASSET_ETH_ADDRESS
from reserve_asset import convert_addr_in_crypto_asset


'''V1 contract is here: https://github.com/aave/aave-protocol/blob/master/abi/LendingPool.json
'''
#Lending_Pool_V1_Address = '0x398eC7346DcD622eDc5ae82352F02bE94C62d119'
#Lending_Pool_V1_ABI = json.load(open('C:/Users/yonic/repos/liquidator/abi/LendingPool_V1.json'))

Lending_Pool_V2_Address = '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9'
Lending_Pool_V2_ABI = json.load(open('C:/Users/yonic/repos/liquidator/abi/LendingPool_V2.json'))

#this is my test free account in Infura, 100,000 Requests/Day
Infura_EndPoint = 'https://mainnet.infura.io/v3/fd3ac79f46ba4500be8e92da9632b476'


'''Parse Borrowd event based on AAVE V1 protocol:
   https://docs.aave.com/developers/v/1.0/developing-on-aave/the-protocol/lendingpool#borrow-1
'''
def handle_borrow_event_V1(event_data):
    collateral_crypto_address = event_data['_reserve']
    crypto_collatera_asset = convert_addr_in_crypto_asset(collateral_crypto_address)

    #TODO: convert Wei to USD
    user_who_borrowed_address = event_data['_user']
    amount = event_data['_amount'] #amount borrowed, in Wei!
    borrow_rate_mode = event_data['_borrowRateMode']
    borrow_rate = event_data['_borrowRate'] #1-Fixed, 2-Float
    origination_fee = event_data['_originationFee']
    borrow_balance_increase = event_data['_borrowBalanceIncrease'] #in Wei!
    timestamp = event_data['_timestamp']
    datetime_time = datetime.datetime.fromtimestamp(timestamp)

    print('Borrow \n'
          'collateral_asset:{}, borrowed_amount(ETH):{}, balance_increase(ETH):{}, borrow_rate_mode:{}\n'
          'user:{}, datetime_time:{}, '.
          format(crypto_collatera_asset,
                 convert_wei_to_eth(amount),
                 convert_wei_to_eth(borrow_balance_increase),
                 borrow_rate_mode,
                 user_who_borrowed_address,
                 datetime_time))


def handle_borrow_event_V2(event_data):
    collateral_crypto_address = event_data['reserve']
    crypto_collatera_asset = 'not_known'
    if collateral_crypto_address in CRYPTO_ASSET_ETH_ADDRESS.keys():
        crypto_collatera_asset = CRYPTO_ASSET_ETH_ADDRESS[collateral_crypto_address]

    #TODO: convert Wei to USD
    on_BehalfOf_borrowed_address = event_data['onBehalfOf']
    user_who_borrowed_address = event_data['user']
    amount = event_data['amount'] #amount borrowed, in Wei!
    borrow_rate_mode = event_data['borrowRateMode']
    borrow_rate = event_data['borrowRate'] #1-Fixed, 2-Float
    referral = event_data['referral']


    print('Borrow \n'
          'collateral_asset:{}, borrowed_amount(ETH):{}, borrow_rate_mode:{}\n'
          'user:{}, on_BehalfOf:{}'.
          format(crypto_collatera_asset,
                 convert_wei_to_eth(amount),
                 borrow_rate_mode,
                 user_who_borrowed_address,
                 on_BehalfOf_borrowed_address))

    return convert_wei_to_eth(amount)


def handle_liqudation_call_event_V2(event_data):
    collateralAsset = event_data['collateralAsset']
    debtAsset = event_data['debtAsset']
    user = event_data['user']
    debtToCover = event_data['debtToCover']
    liquidatedCollateralAmount = event_data['liquidatedCollateralAmount']
    liquidator = event_data['liquidator']
    receiveAToken = event_data['receiveAToken']

    collateralAsset_name = convert_addr_in_crypto_asset(collateralAsset)
    debtAsset_name  = convert_addr_in_crypto_asset(debtAsset)
    debtToCover_eth = convert_wei_to_eth(debtToCover)
    liquidatedCollateralAmount_eth = convert_wei_to_eth(liquidatedCollateralAmount)

    print("LiquidationCall\n"
          "collateralAsset_name:{}"
          ",debtAsset_name:{},"
          ",debtToCover_eth:{},"
          ",liquidatedCollateralAmount_eth:{}"
          ",user:{},liquidator:{}".
          format(collateralAsset_name, debtAsset_name, debtToCover_eth,
                 liquidatedCollateralAmount_eth, user, liquidator))

    return liquidatedCollateralAmount_eth, liquidator

'''Based on: https://github.com/aave/protocol-v2/blob/ice/mainnet-deployment-03-12-2020/contracts/interfaces/ILendingPool.sol
'''
def fetch_events(type):
    web3 = Web3(Web3.HTTPProvider(Infura_EndPoint))
    from_block = 13333357 #2021-10-01 12:11:05
    to_block = 'latest'
    address = None
    topics = None

    contract = web3.eth.contract(address=Lending_Pool_V2_Address, abi=Lending_Pool_V2_ABI)
    if type == 'Borrow':
        event = contract.events.Borrow
    elif type == 'LiquidationCall':
        event = contract.events.LiquidationCall
    else:
        raise Exception('Not supported event type!')

    abi = event._get_event_abi()
    abi_codec = event.web3.codec

    # Set up any indexed event filters if needed
    argument_filters = dict()
    _filters = dict(**argument_filters)

    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=event.address,
        argument_filters=_filters,
        fromBlock=from_block,
        toBlock=to_block,
        address=address,
        topics=topics,
    )

    # Call node over JSON-RPC API
    logs = event.web3.eth.getLogs(event_filter_params)

    # Convert raw binary event data to easily manipulable Python objects
    Stats = []
    for entry in logs:
        data = dict(get_event_data(abi_codec, abi, entry))

        block_number = data['blockNumber']
        address = data['address'] #Lending Pool Contract address

        event_type = data['event']
        if event_type == 'Borrow':
            ret = handle_borrow_event_V2(event_data=dict(data['args']))
        elif event_type == 'LiquidationCall':
            ret = handle_liqudation_call_event_V2(event_data=dict(data['args']))

        Stats.append(ret)

    collected_eth_summary = 0.0
    liquidator_accounts_eth = {}
    liquidator_accounts_stat = {}
    if type == 'LiquidationCall':
        for collected_eth, liq_account in Stats:
            collected_eth_summary += collected_eth
            if liq_account in liquidator_accounts_stat.keys():
                liquidator_accounts_eth[liq_account] += collected_eth
                liquidator_accounts_stat[liq_account] +=1
            else:
                liquidator_accounts_eth[liq_account] = collected_eth
                liquidator_accounts_stat[liq_account] =1


    print('Total collected eth:{}'.format(collected_eth_summary))
    print('liquidator collected eth:{}'.format(liquidator_accounts_eth))
    print('liquidator collected num:{}'.format(liquidator_accounts_stat))

    #Accounts balance could be found here: https://etherscan.io/address
    #Example - https://etherscan.io/address/0x3909336de913344701C6F096502d26208210b39F



def call_getUserAccountData_V2(account='0x8d30e4b4C8D461d99Ee3FD67B3f7f0Ddaf9d3dD6'):
    web3 = Web3(Web3.HTTPProvider(Infura_EndPoint))
    contract = web3.eth.contract(address=Lending_Pool_V2_Address, abi=Lending_Pool_V2_ABI)
    ret = contract.functions.getUserAccountData(account).call()
    print(ret)
    pass




if __name__ == '__main__':
    #fetch_events()
    call_getUserAccountData_V2()