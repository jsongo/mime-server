#!/usr/bin/env python
# coding=utf-8
'''
    desc: 主服务
    author: jsongo
'''
import tornado.web
import tornado.ioloop
import tornado.options
from tornado.options import define, options

from handlers.webSocketHandler import MainSocket

define("port", default=8080, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/websocket", MainSocket),
            # (r"/room", RoomHandler), # 用http请求的方式
            # (r"/dig", AnswerHandler),# 用http请求的方式
        ]
        settings = dict(
            # cookie_secret="7c1LG3yZhzMJ",
            # xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
