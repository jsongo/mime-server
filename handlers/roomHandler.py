#!/usr/bin/env python
# coding=utf-8
# import tornado.web
from tornado import gen
import json as JSON
from time import time

from common.util import rspError, rspSuccess, redisKey 
from mime import genMimeArr, mimeCnt, getInitArr
from myRedis import execRedis
import core

maxUserCnt = 2 # 最多几个人玩

class RoomHandler(object):

    @classmethod
    @gen.coroutine
    def createRoom(self, data):
        # data = self.request.body
        roomNo = None
        if data:
            # data = JSON.loads(data)
            roomNo = data.get('no')
        sid = data.get('sid')
        key = redisKey % roomNo
        room = yield execRedis('hgetall', key)
        if room: # 房间已经开了
            userCnt = int(room.get('cnt', 0))
            mimeData = room.get('data', 0)
            if userCnt < maxUserCnt:
                userCnt += 1 # TODO: 这里可以记录另一个玩家的信息
                yield execRedis('hset', key, 'cnt', userCnt)
                lefts = room.get('lefts', 0)
                rspData = {
                    'map': JSON.loads(mimeData),
                    'count': lefts 
                }
                # self.write(rspSuccess(rspData))
                raise gen.Return(rspData)
            else:
                # self.write(rspError(u'房间%s已经满员' % roomNo))
                raise gen.Return(u'房间%s已经满员' % roomNo)
                # self.finish()
                # return
        else: # 新房间
            mimeData = genMimeArr()
            initData = getInitArr(9)
            room = { # TODO: 这里可以记录用户的信息
                'createTime': int(time()*1000),
                'cnt': 1,
                'online': True,
                'lefts': mimeCnt,
                'answer': JSON.dumps(mimeData),
                'data': JSON.dumps(initData),
                'curId': sid,
                'lastId': 0
            }
            yield execRedis('hmset', key, data=room, expire=60*60*12) # 12小时
            rspData = {
                'map': initData,
                'count': mimeCnt
            }
            print('room number: ', roomNo)
            # self.write(rspSuccess(rspData))
            raise gen.Return(rspData)
