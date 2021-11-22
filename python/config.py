import json

'''V1 contract is here: https://github.com/aave/aave-protocol/blob/master/abi/LendingPool.json
'''
#Lending_Pool_V1_Address = '0x398eC7346DcD622eDc5ae82352F02bE94C62d119'
#Lending_Pool_V1_ABI = json.load(open('C:/Users/yonic/repos/liquidator/abi/LendingPool_V1.json'))

Lending_Pool_V2_Address = '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9'
Lending_Pool_V2_ABI = json.load(open('C:/Users/yonic/repos/liquidator/abi/LendingPool_V2.json'))

#this is my test free account in Infura, 100,000 Requests/Day
Infura_EndPoint = 'https://mainnet.infura.io/v3/fd3ac79f46ba4500be8e92da9632b476'

CACHE_FOLDER = 'C:/Users/yonic/junk/liquidator/cache'