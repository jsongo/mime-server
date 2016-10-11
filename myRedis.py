#!/usr/bin/env python
# coding=utf-8
'''
    desc: redis相关的方法
    author: jsongo
'''
import tornadis
from tornado import gen

pool = 10
# host = '127.0.0.1'
host = 'redis-server'
port = 6379
pwd = ''
POOL = tornadis.ClientPool(max_size=pool, host=host, port=port, autoconnect=True, password=pwd)

getRedis = POOL.connected_client

@gen.coroutine
def execRedis(*args, **kwargs):
    result = None
    with (yield getRedis()) as redis:
        if not isinstance(redis, tornadis.TornadisException):
            data = kwargs.get('data')
            if args[0] == 'hmset' and data:
                params = []
                [params.extend(x) for x in data.items()]
                tmpList = list(args)
                tmpList.extend(params)
                args = tuple(tmpList)
                print args
            result = yield redis.call(*args)
            expire = kwargs.get('expire')
            if expire and len(args) > 1:
                key = args[1]
                yield redis.call('expire', key, expire)
            if args[0] == 'hgetall' and result and type(result)==list:
                from itertools import izip
                i = iter(result)
                result = dict(izip(i, i))
    raise gen.Return(result)
