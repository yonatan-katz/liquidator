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

    eth_1_to_usdc = []
    eth_10_to_usdc = []
    eth_100_to_usdc = []

    for i in range(100):
        # Returns the amount of USDC you get for 1 ETH
        rate = uniswap.get_price_input(eth, usdc, 1*10**18, fee=0.3) / 1e6
        eth_1_to_usdc.append(rate)

        # Returns the amount of USDC you get for 10 ETH
        rate = uniswap.get_price_input(eth, usdc, 10 * 10 ** 18, fee=0.3) / 1e6
        eth_10_to_usdc.append(rate)

        # Returns the amount of USDC you get for 100 ETH
        rate = uniswap.get_price_input(eth, usdc, 100 * 10 ** 18, fee=0.3) / 1e6
        eth_100_to_usdc.append(rate)
        time.sleep(1)

    df = pd.DataFrame({"eth_1_to_usdc":eth_1_to_usdc, "eth_10_to_usdc":eth_10_to_usdc, "eth_100_to_usdc":eth_100_to_usdc})
    pass

if __name__ == "__main__":
    main()
