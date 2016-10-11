#!/usr/bin/env python
# coding=utf-8
'''
    desc: 工具方法 
    author: jsongo
'''
import json as JSON
import core

redisKey = 'room#%s'

def rspError(msg):
    return JSON.dumps({
        'errCode': 1001,
        'errMsg': msg
    })

def rspSuccess(data, isStr=False):
    result = {
        'errCode': 0
    }
    if data:
        result['data'] = data
    rsp = result if isStr else JSON.dumps(result)
    return rsp
