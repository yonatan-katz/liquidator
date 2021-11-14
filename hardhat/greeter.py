from web3 import Web3
import json
from web3._utils.abi import get_constructor_abi, merge_args_and_kwargs
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3._utils.contracts import encode_abi

GREETER_ADDR='0x5fbdb2315678afecb367f032d93f642f64180aa3'
GREETER_ABI = json.load(open('greeter_abi.json'))
HARDHAT_END_POINT='http://127.0.0.1:8545'

def main():
    web3 = Web3(Web3.HTTPProvider(HARDHAT_END_POINT))
    greeter = web3.eth.contract(address=Web3.toChecksumAddress(GREETER_ADDR), abi=GREETER_ABI)
    #contract.functions.setGreeting("Hello blockchain!").call()
    tx_hash = greeter.functions.setGreeting('Hello blockchain!').transact()
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    ret = greeter.functions.greet().call()
    print(ret)
    pass


if __name__ == '__main__':
    main()
