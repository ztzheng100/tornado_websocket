# tornado_websocke
- tornadowebsocket聊天室例子，增加多房间


## WebSocket
- WebSocket是HTML5规范中新提出的客户端-服务器通讯协议，协议本身使用新的ws://URL格式。
- WebSocket 是独立的、创建在 TCP 上的协议，和 HTTP 的唯一关联是使用 HTTP 协议的101状态码进行协议切换，使用的 TCP 端口是80，可以用于绕过大多数防火墙的限制。
- 允许服务端直接向客户端推送数据而不需要客户端进行请求，两者之间可以创建持久性的连接，并允许数据进行双向传送。
- 目前常见的浏览器如 Chrome、IE、Firefox、Safari、Opera 等都支持 WebSocket，同时需要服务端程序支持 WebSocket。

### 1. Tornado的WebSocket模块
Tornado提供支持WebSocket的模块是tornado.websocket，++其中提供了一个WebSocketHandler类用来处理通讯++。

#### WebSocketHandler.open()（接口）
- 当一个WebSocket连接建立后被调用。

#### WebSocketHandler.on_message(message)(接口)
- 当客户端发送消息message过来时被调用，注意此方法必须被重写。

#### WebSocketHandler.on_close()(接口)
- 当WebSocket连接关闭后被调用

#### WebSocketHandler.write_message(message, binary=False)（方法）
- 向客户端发送消息messagea，message可以是字符串或字典（字典会被转为json字符串）。
- 若binary为False，则message以utf8编码发送；二进制模式（binary=True）时，可发送任何字节码。

#### WebSocketHandler.close()方法
关闭WebSocket连接

#### WebSocketHandler.check_origin(origin)（接口）
判断源origin，对于符合条件（返回判断结果为True）的请求源origin允许其连接，否则返回403。可以重写此方法来解决WebSocket的跨域请求（如始终return True）。
### 示例
- 前端

```
<script src="http://cdn.bootcss.com/jquery/3.1.1/jquery.min.js"></script>
<div>
    <textarea id="msg"></textarea>
    <a href="javascript:;" onclick="sendMsg()">发送</a>
</div>
<script type="text/javascript">
    var ws = new WebSocket("ws://192.168.114.177:8000/chat");
    ws.onmessage = function(e) {
        $("#contents").append("<p>" + e.data + "</p>");
    }
    function sendMsg() {
        var msg = $("#msg").val();
        ws.send(msg);
        $("#msg").val("");
    }
</script>
```
- 后端代码 server.py

```
class ChatHandler(WebSocketHandler):

    users = set()  # 用来存放在线用户的容器

    def open(self):
        self.users.add(self)  # 建立连接后添加用户到容器中
        for u in self.users:  # 向已在线用户发送消息
            u.write_message(u"[%s]-[%s]-进入聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def on_message(self, message):
        for u in self.users:  # 向在线用户广播消息
            u.write_message(u"[%s]-[%s]-说：%s" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))

    def on_close(self):
        self.users.remove(self) # 用户关闭连接后从容器中移除用户
        for u in self.users:
            u.write_message(u"[%s]-[%s]-离开聊天室" % (self.request.remote_ip, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求
```

