import numpy as np

'''Based on :
   https://www.investopedia.com/terms/w/wei.asp
'''
ONE_ETH_IN_WEI = np.float64(10e18)
def convert_wei_to_eth(wei):
    return np.float64(wei) / ONE_ETH_IN_WEI