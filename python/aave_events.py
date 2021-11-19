'''
AAve V2 event handlers,
'''

def handle_borrow(event_data):
    S = {}
    S['reserve'] = [event_data['reserve']] #reserve address
    S['onBehalfOf'] = [event_data['onBehalfOf']]
    S['user'] = [event_data['user']]
    S['amount'] = [event_data['amount']]  # amount borrowed, in Wei!
    S['borrowRateMode'] = [event_data['borrowRateMode']]
    S['borrow_rate'] = [event_data['borrowRate']]  # 1-Fixed, 2-Float
    S['referral'] = [event_data['referral']]
    return S

def handle_deposit(event_data):
    S = {}
    S['reserve'] = [event_data['reserve']]
    S['address'] = [event_data['address']]
    S['onBehalfOf'] = [event_data['onBehalfOf']]
    S['amount'] = [event_data['amount']]
    S['referral'] = [event_data['referral']]
    return S

def handle_liquidation_call(event_data):
    S = {}
    S['collateralAsset'] = [event_data['collateralAsset']]
    S['debtAsset'] = [event_data['debtAsset']]
    S['user'] = [event_data['user']]
    S['debtToCover'] = [event_data['debtToCover']]
    S['liquidatedCollateralAmount'] = [event_data['liquidatedCollateralAmount']]
    S['liquidator'] = [event_data['liquidator']]
    S['receiveAToken'] = [event_data['receiveAToken']]
    return S

def handle_repay(event_data):
    S = {}
    S['reserve'] = [event_data['reserve']]
    S['user'] = [event_data['user']]
    S['repayer'] = [event_data['repayer']]
    S['amount'] = [event_data['amount']]
    return S

def handle_swap(event_data):
    S = {}
    S['reserve'] = [event_data['reserve']]
    S['user'] = [event_data['user']]
    S['rateMode'] = [event_data['rateMode']]
    return S

def handle_withdraw(event_data):
    S = {}
    S['reserve'] = [event_data['reserve']]
    S['user'] = [event_data['user']]
    S['to'] = [event_data['to']]
    S['amount'] = [event_data['amount']]
    return S


'''TODO:to impement'''
def handle_flash_loan(event_data):
    pass
def handle_pause(event_data):
    pass
def handle_rebalance_stable_borrowRate(event_data):
    pass
def handle_reserve_data_updated(event_data):
    pass
def handle_reserve_used_as_collateral_disabled(event_data):
    pass
def handle_reserve_used_as_collateral_enabled(event_data):
    pass

def handle_unpause(event_data):
    pass









