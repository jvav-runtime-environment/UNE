import socket
import json
import logging as log


class Connection:
    def __init__(
        self, ip=socket.gethostbyname(socket.gethostname()), port=23783, is_server=True
    ):
        self.ip = ip
        self.port = port
        self.__socket = socket.socket()
        self.__conn = None

        self.is_server = is_server

    def server(self):
        # 切换为服务端模式
        if not self.__conn:
            self.is_server = True
        else:
            raise RuntimeWarning("不能在已有连接的情况下更改状态")

    def client(self):
        # 切换为客户端模式
        if not self.__conn:
            self.is_server = False
        else:
            raise RuntimeWarning("不能在已有连接的情况下更改状态")

    def listen(self, conns=5):
        # 服务端初始化
        if not self.is_server:
            raise TypeError("这个方法只能由服务端调用")

        self.__socket.bind((self.ip, self.port))
        self.__socket.listen(conns)

    def accept(self):
        # 服务端开始监听
        if not self.is_server:
            raise TypeError("这个方法只能由服务端调用")

        self.__conn, addr = self.__socket.accept()
        return addr  # 返回连接的(ip, port)

    def connect(self, ip):
        # 客户端尝试建立连接
        if self.is_server:
            raise TypeError("这个方法只能由客户端调用")

        self.__socket.connect((ip, self.port))
        self.__conn = self.__socket

    def send(self, msg: str | dict):
        # 发送消息
        if isinstance(msg, str):
            self.send_raw(msg.encode())
        elif isinstance(msg, dict):
            self.send_raw(json.dumps(msg).encode())
        else:
            raise TypeError(f"消息类型错误, 不支持的消息类型: {type(msg)}")

    def recv(self):
        # 接收消息
        msg = self.recv_raw()

        try:
            msg = msg.decode()
        except UnicodeDecodeError:
            raise UnicodeDecodeError("消息解码失败")

        return msg

    def close(self):
        # 关闭连接
        self.__conn.close()
        self.__conn = None

    def send_raw(self, msg: bytes):
        # 发送原始消息
        self.__conn.send(self.__formate_msg(msg))

    def recv_raw(self):
        # 接收原始消息
        return self.__recv_all()

    def set_timeout(self, timeout):
        # 设置超时
        self.__socket.settimeout(timeout)

    def remove_timeout(self):
        # 移除超时
        self.__socket.settimeout(None)

    def __recv_all(self):
        # 根据数据大小尝试接收全部数据
        msg_len = int.from_bytes(self.__conn.recv(8))  # 首位8字节为数据包大小

        msg = b""
        while msg_len > 0:  # 接收全部数据
            recv = self.__conn.recv(1024 if msg_len > 1024 else msg_len)
            if recv:
                # 判断接收内容不为空
                msg += recv
                msg_len -= len(recv)
            else:
                # 如果为空则连接已断开
                log.error("接收过程中断!")
                return None

        return msg

    def __formate_msg(self, msg: str | bytes):
        # 生成格式化消息
        # 数据包结构: 8字节长度 + json数据

        return len(msg).to_bytes(8) + msg


if __name__ == "__main__":
    server = Connection(ip="127.0.0.1")
    server.listen(1)
    server.accept()
    server.send("hello")
    server.close()
