from uniswap import Uniswap
import config
import crypto_utils
import time
import pandas as pd

address = None
private_key = None
version = 2
provider = config.Infura_EndPoint
uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider)

# Some token addresses we'll be using later in this guide
eth = "0x0000000000000000000000000000000000000000"
usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
dai = "0x6B175474E89094C44Da98b954EedeAC495271d0F"


def main():
    usdc_to_eth = []
    eth_to_usdc = []

    for i in range(100):
        # Returns the amount of USDC you get for 1 ETH (10^18 wei)
        rate = uniswap.get_price_input(eth, usdc, 10 ** 18) / 1e6
        print("1 ETH to USDC rate: {}".format(rate))
        usdc_to_eth.append(rate)

        # Returns the amount of ETH you need to pay (in wei) to get 1 USDC
        rate = uniswap.get_price_output(eth, dai, 1 * 10 ** 6) / 1e6
        print("1 USDC to 1 ETH rate:{}".format(rate))
        eth_to_usdc.append(rate)
        time.sleep(1)

    df = pd.DataFrame({"usdc_to_eth":usdc_to_eth, "eth_to_usdc":eth_to_usdc})
    pass

if __name__ == "__main__":
    main()
