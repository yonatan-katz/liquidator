import numpy as np

'''Based on :
   https://www.investopedia.com/terms/w/wei.asp
'''
ONE_ETH_IN_WEI = np.float64(1e18)
def convert_wei_to_eth(wei):
    return np.float64(wei) / ONE_ETH_IN_WEI

'''
    it looks like there is a bug in AAVE protocol decsription: https://docs.aave.com/developers/deployed-contracts/deployed-contracts
    AMPL asset has 1e9 decimals!
    encountered when checked transaction on https://etherscan.io/ 
    '''
def convert_decimal_to_float(asset, base):
    if asset == 'GUSD':
        return base / 1e2
    elif asset == 'USDT':
        return base / 1e6
    elif asset == 'USDC':
        return base / 1e6
    elif asset == 'WBTC':
        return base / 1e8
    elif asset == 'AMPL':
        return base / 1e9
    else:
        return base / 1e18