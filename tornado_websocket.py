import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
# import tornado.autoreload

from tornado.options import define, options

define('port', default=8000, help='run on the given port', type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/room/(?P<room>.*)', RoomHandler),
            (r'/chatsocket/(?P<room>.*)', ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret = '__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__',
            template_path = os.path.join(os.path.dirname(__file__), 'templates'),
            static_path = os.path.join(os.path.dirname(__file__), 'static'),
            xsrf_cookies = True,
            autoreload = True
        )
        super(Application, self).__init__(handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', rooms=ChatSocketHandler.waiters)

class RoomHandler(tornado.web.RequestHandler):
    def get(self, room):
        self.render('chat.html', messages=ChatSocketHandler.cache.get(room))

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = { }
    cache = { }
    cache_size = 200

    def __init__(self, application, request, **kwargs):
        self.id = None
        super(ChatSocketHandler, self).__init__(application, request, **kwargs)


    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self, room):
        self.id = room
        if self.id not in ChatSocketHandler.waiters:
            ChatSocketHandler.waiters[self.id] = set()
        ChatSocketHandler.waiters[self.id].add(self)

    def on_close(self):
        ChatSocketHandler.waiters[self.id].remove(self)

    @classmethod
    def update_cache(cls, chat, id):
        if id not in cls.cache:
            cls.cache[id] = list()
        cls.cache[id].append(chat)
        if len(cls.cache[id]) > cls.cache_size:
            cls.cache[id] = cls.cache[id][-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat, id):
        logging.info("sending message to %d waiters", len(cls.waiters[id]))
        for waiter in cls.waiters[id]:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
        }
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))

        ChatSocketHandler.update_cache(chat,self.id)
        ChatSocketHandler.send_updates(chat,self.id)

def main():
    tornado.options.parse_command_line() # 解析命令行参数
    app = Application()
    app.listen(options.port) # 监听端口
    tornado.ioloop.IOLoop.current().start()  # 开启事件循环

if __name__ == '__main__':
    main()
