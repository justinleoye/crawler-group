from pyutils.create_obj import *

def test_create_obj():
    print create_obj_from_config({'class': 'quant_screener.screeners.random_screener.RandomScreener'})

if __name__ == '__main__':
    test_create_obj()

