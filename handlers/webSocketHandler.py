#!/usr/bin/env python
# coding=utf-8
'''
    desc: webSocket的处理逻辑 
    author: jsongo
'''
import tornado.websocket
from tornado import gen
import json as JSON
from time import time
from tornado.ioloop import IOLoop

from handlers.answerHandler import AnswerHandler
from handlers.roomHandler import RoomHandler, maxUserCnt 
import core
from myRedis import execRedis
from common.util import rspError, rspSuccess, redisKey 

class MainSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.sid = 0
        self.roomNo = 0
        self.isValid = True 

    def open(self):
        self.sid = int(time()*1000)
        self.roomNo = self.get_argument('no')
        if not self.roomNo or not self.roomNo.isdigit() or len(self.roomNo) > 10:
            print('Room number is invalid', core.socketPool, self.roomNo)
            self.isValid = False 
            self.close()
        self.roomNo = int(self.roomNo)
        if core.socketPool.has_key(self.roomNo):
            if len(core.socketPool[self.roomNo]) < maxUserCnt:
                core.socketPool[self.roomNo][self.sid] = {
                    'sock': self,
                    'score': 0
                }
                print("WebSocket opened: ", self.sid, self.roomNo, core.socketPool)
            else:
                print('init fail, room is full', core.socketPool, self.roomNo)
                self.isValid = False 
                self.close()
        else:
            core.socketPool[self.roomNo] = {
                self.sid: {
                    'sock': self,
                    'score': 0
                }
            }

    def on_message(self, msg): # this method doesn't support coroutine
        try:
            msg = JSON.loads(msg)
            msgType = msg.get('type')
        except Exception, ex:
            pass
        if msgType ==  'dig':
            IOLoop.current().spawn_callback(self.processDigAction, msg)
        elif msgType == 'create':
            IOLoop.current().spawn_callback(self.processRoomAction)

    @gen.coroutine  
    def processDigAction(self, msg):
        result = yield AnswerHandler.digMime(msg, self.sid)
        if type(result) == int:
            print('digging')
            # 推送到房间内的所有人
            data = {
                'type': 'dig',
                'answer': result,
                'isMe': False, # 下面赋值
                'x': msg.get('x'),
                'y': msg.get('y')
            }
            sockets = core.socketPool[self.roomNo]
            # print(self.roomNo, sockets)
            key = redisKey % self.roomNo
            lefts = yield execRedis('hget', key, 'lefts')
            lefts = int(lefts)
            for sid in sockets:
                info = sockets[sid]
                ws = info.get('sock')
                data['isMe'] = (self==ws)
                ws.write_message(rspSuccess(data))
                # 判断是否是最后一个
                if result < 0 and lefts <= 0: # 结束了
                    score = info.get('score')
                    endData = {
                        'type': 'over',
                        'score': info['score']
                    }
                    ws.write_message(rspSuccess(endData))
            print('push done')

    @gen.coroutine  
    def processRoomAction(self):
        data = {
            'no': self.roomNo,
            'sid': self.sid
        }
        result = yield RoomHandler.createRoom(data)
        d = {
            'type': 'create',
        }
        if type(result) == dict:
            d.update(result) 
            rsp = rspSuccess(d)
        else:
            d['data'] = result
            rsp = rspError(d)
        print rsp
        self.write_message(rsp)

    def on_close(self):
        print("WebSocket closed")
        # 在socket关掉的时候，把用户从房间里删除
        if self.isValid:
            core.socketPool[self.roomNo].pop(self.sid)
            key = redisKey % self.roomNo
            yield execRedis('hincrby', key, 'cnt', -1)

    # 测试的时候一定要设置这个方法，要不然会可能返回403，安全域名限制
    def check_origin(self, origin):
        return True
