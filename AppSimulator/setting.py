# coding=utf-8
import os

PAGE_SIZE = 20

REDIS_SERVER = 'redis://' + os.environ["REDIS_SERVER_IP"] + '/11'  # 'redis://172.16.55.155'
# REDIS_SERVER = 'redis://172.16.3.2/11'
REDIS_SERVER_RESULT = 'redis://' + os.environ["REDIS_SERVER_IP"] + '/10'
# REDIS_SERVER_RESULT = 'redis://172.16.3.2/10'

MONGODB_SERVER = os.environ["MONGODB_SERVER_IP"]  # "172.16.55.155"
# MONGODB_SERVER = "172.16.3.2"
MONGODB_PORT = 27017


DEVICE_STATUS_RPC_TIMEOUT = 'rpc_timeout'
DEVICE_STATUS_UNKOWN = 'unkown'
DEVICE_STATUS_RUNNING = 'running'
DEVICE_STATUS_SUSPEND = 'suspend'

SCOPE_TIMES = 1 * 60

RPC_CLIENT = "http://172.16.252.238:8003/"
RPC_PORT = 8003
RPC_SERVER_TIMEOUT = 5
