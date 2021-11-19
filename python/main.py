import event_monitor

if __name__ == '__main__':
    '''monitor Aave protocol events
    '''
    event_monitor.fetch_events(type='Borrow')
