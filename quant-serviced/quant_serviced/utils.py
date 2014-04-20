
import os
from pyutils.env_utils import Env

env = Env('quant_serviced')

QUANT_SERVICED_DEV = env.get('dev')=='1'
QUANT_SERVICED_DEBUG = env.get('debug')=='1'

