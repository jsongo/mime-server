#!/usr/bin/env python
# coding=utf-8

from tornado import gen
import json as JSON

from myRedis import execRedis
import core
from common.util import rspError, rspSuccess, redisKey 

class AnswerHandler(object):

    @classmethod
    @gen.coroutine
    def digMime(self, data, sid):
        x = y = -1
        roomNo = 0
        if data:
            # data = JSON.loads(data)
            x = int(data.get('x'))
            y = int(data.get('y'))
            roomNo = int(data.get('no'))
        if x < 0 or y < 0 or not roomNo:
            raise gen.Return('x or y or roomNo is invalid')
        key = redisKey % roomNo
        room = yield execRedis('hgetall', key)
        lastPlayer = int(room.get('lastId'))
        isValid = True
        if lastPlayer:
            print(lastPlayer, sid)
            if sid == lastPlayer:
                isValid = False
        else:
            curPlayer = int(room.get('curId'))
            print(curPlayer, sid)
            if sid != curPlayer: # 不用管curId不存在的bug，随便谁点谁开始
                isValid = False
        if not isValid:
            raise gen.Return(u'请等待下轮再操作')
        answer = JSON.loads(room.get('answer'))
        data = JSON.loads(room.get('data'))
        print answer, data
        result = answer[y][x]
        data[y][x] = result
        # update redis
        updateData = {
            'data': JSON.dumps(data),
            'lastId': sid
        }
        yield execRedis('hmset', key, data=updateData)
        if result < 0: # 挖到金子了，要把剩余的个数减1
            yield execRedis('hincrby', key, 'lefts', -1)
            info = core.socketPool[roomNo][sid]
            info['score'] += 1
        raise gen.Return(result)
