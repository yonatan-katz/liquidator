'''
Crypto assets addresses from:
https://docs.aave.com/developers/v/1.0/deployed-contracts/deployed-contract-instances#reserves-assets
'''
CRYPTO_ASSET_ADDRESS_TO_NAME = {
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE' : 'ETH',
    '0x6B175474E89094C44Da98b954EedeAC495271d0F' : 'DAI',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' : 'USDC',
    '0x57Ab1ec28D129707052df4dF418D58a2D46d5f51' : 'SUSD',
    '0x0000000000085d4780B73119b644AE5ecd22b376' : 'TUSD',
    '0xdAC17F958D2ee523a2206206994597C13D831ec7' : 'USDT',
    '0x4Fabb145d64652a948d72533023f6E7A623C7C53' : 'BUSD',
    '0x0D8775F648430679A709E98d2b0Cb6250d2887EF' : 'BAT',
    '0xF629cBd94d3791C9250152BD8dfBDF380E2a3B9c' : 'ENJ',
    '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984' : 'UNI',
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2' : 'WETH',
    '0xD533a949740bb3306d119CC777fa900bA034cd52' : 'CRV',
    '0x514910771AF9Ca656af840dff83E8264EcF986CA' : 'LINK',
    '0xE41d2489571d322189246DaFA5ebDe1F4699F498' : 'ZRX',
    '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e' : 'YFI',
    '0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272' : 'xSUSHI',
    '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599' : 'WBTC',
    '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F' : 'SNX',
    '0xD5147bc8e386d91Cc5DBE72099DAC6C9b99276F5' : 'renFIL',
    '0x408e41876cCCDC0F92210600ef50372656052a38' : 'REN',
    '0x03ab458634910AaD20eF5f1C8ee96F1D6ac54919' : 'RAI',
    '0x8e870d67f660d95d5be530380d0ec0bd388289e1' : 'PAX',
    '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2' : 'MKR',
    '0x0F5D2fB29fb7d3CFeE444a200298f468908cC942' : 'MANA',
    '0xdd974D5C2e2928deA5F71b9825b8b646686BD200' : 'KNC',
    '0x056Fd409E1d7A124BD7017459dFEa2F387b6d5Cd' : 'GUSD',
    '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9' : 'AAVE',
    '0xba100000625a3754423978a60c9317c58a424e3D' : 'BAL',
    '0xD46bA6D942050d489DBd938a2C909A5d5039A161' : 'AMPL',
    '0x1494CA1F11D487c2bBe4543E90080AeBa4BA3C2b' : 'DeFiPulse',
    '0x8E870D67F660D95d5be530380D0eC0bd388289E1' : 'USDP',
    '0x853d955aCEf822Db058eb8505911ED77F175b99e' : 'FRAX',
    '0x956F47F50A910163D8BF957Cf5846D573E7f87CA' : 'FEI'

    #TODO: add more assets from the protocol
}

CRYPTO_ASSET_NAME_TO_ADDRESS = {value:key for key, value in CRYPTO_ASSET_ADDRESS_TO_NAME.items()}

'''split binary mask to the borrowed, collateral assets according to:
   https://docs.aave.com/developers/the-core-protocol/lendingpool#getconfiguration 
'''
def split_user_loan_deposit_bitmask(bitmask):
    bitmask_ascii = str(bin(bitmask))
    asset_index = 0
    S = {}
    print(bitmask_ascii)
    for i in range(len(bitmask_ascii)-1,2,-2):
        is_borrowed = int(bitmask_ascii[i])
        is_col = int(bitmask_ascii[i-1])
        S[asset_index] = (is_col, is_borrowed)
        asset_index += 1
    return S



def merge_with_default_bitmask(ascii_bitmsak):
    ascii_bitmsak = list(ascii_bitmsak)[2:]
    default_bitmask = list(str(bin(2 ** 255))[2:])
    default_bitmask[-len(ascii_bitmsak):] = ascii_bitmsak
    default_bitmask[0] = '0'
    return "".join(default_bitmask)



'''split reserve asset config bitmask based on
   https://github.com/aave/protocol-v2/blob/master/aave-v2-whitepaper.pdf,
   chapter 4.4
'''
def split_asset_config_bitmask(bitmask):
    bitmask_ascii = str(bin(bitmask))
    ltv = int(bitmask_ascii[-15:], 2) / 100.0  # maximum ltv of the asset
    print(ltv)
    print(bitmask_ascii)
    bitmask_ascii = merge_with_default_bitmask(bitmask_ascii)
    ltv = int(bitmask_ascii[-15:], 2) / 100.0 #maximum ltv of the asset
    print(ltv)
    liq_threshold = int(bitmask_ascii[-31:-16], 2) / 100.0
    liq_bonus = int(bitmask_ascii[-47:-32], 2) / 100.0
    decimals = int(bitmask_ascii[-55:-48], 2)
    is_active = int(bitmask_ascii[-56], 2)
    is_freezed = int(bitmask_ascii[-57], 2)
    is_borrowing_enabled = int(bitmask_ascii[-58], 2)
    stable_borrowing_enabled = int(bitmask_ascii[-59], 2)
    reserved = int(bitmask_ascii[-64:-60], 2)
    reserved_factor = int(bitmask_ascii[-80:-65], 2)
    return ltv, liq_threshold, liq_bonus, decimals



def convert_addr_in_crypto_asset(addr):
    if addr in CRYPTO_ASSET_ADDRESS_TO_NAME.keys():
        return CRYPTO_ASSET_ADDRESS_TO_NAME[addr]
    else:
        raise Exception('Not known addr:{}'.format(addr))

def convert_crypto_asset_to_addr(name):
    if name in CRYPTO_ASSET_NAME_TO_ADDRESS:
        return CRYPTO_ASSET_NAME_TO_ADDRESSp[name]
    else:
         raise Exception('Not known name:{}'.format(name))

'''Rougly crypto asset estimation based on google on 2021/11/05
'''
CRYPTO_ASSETS_VALUES_IN_USD = {
    'WETH': 4528.0,
    'USDC': 1.0,
    'LINK': 33.29,
    'USDT': 1.0,
    'WBTC': 60700.0,
    'AAVE': 341.60,
    'DAI': 1.0,
    'BAL': 27.3,
    'xSUSHI': 14.67,
    'REN': 0.9672,
    'SUSD': 1.0,
    'CRV': 4.15,
    'UNI': 25.45,
    'AMPL': 1.59,
    'MKR': 2927,
    'MANA': 2.5216,
    'BAT': 1.02,
    'DeFiPulse': 379.93,
    'USDP': 0.9667,
    'FRAX': 1.0,
    'BUSD': 1.0,
    'GUSD': 0.9946,
    'YFI': 106.090,
    'TUSD': 1.0,
    'ENJ': 2.92,
    'SNX': 113.8
}

def get_crypto_asset_usd_price(crypto_asset):
    if crypto_asset in CRYPTO_ASSETS_VALUES_IN_USD:
        return CRYPTO_ASSETS_VALUES_IN_USD[crypto_asset]

    raise Exception('Cannot convert to usd crypto asset:{}'.formatg(crypto_asset))


if __name__ == '__main__':
    split_asset_config_bitmask(36894427193683303209816)