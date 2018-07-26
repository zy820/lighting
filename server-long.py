#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socketserver
import struct


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):  # 所有请求的交互都是在handle里执行的,
        while True:
            try:
                data = bytearray(
                    self.request.recv(1024).strip())  # 每一个请求都会实例化MyTCPHandler(socketserver.BaseRequestHandler):
                ip = self.client_address[0]  # ip
                print("ip:{} wrote:{}".format(ip, data))
                if len(data) == 31:
                    pack_data = struct.unpack('>cBiiiiiiic', data)
                    print(pack_data)
                else:
                    pass
                # print(data)
                # self.request.sendall(self.data.upper())#sendall是重复调用send.
            except ConnectionResetError as e:
                print("err ", e)
            if not data:
                print("client {} disconnects...".format(self.client_address[0]))
                break

    def setup(self):
        # handle()调用之前，初始化工作
        pass

    def finish(self):
        # handle()调用后，清理工作，setup()异常不会调用该函数
        pass


if __name__ == "__main__":
    # HOST, PORT = "localhost", 9999   #windows
    HOST, PORT = "0.0.0.0", 9999  # Linux
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)  # 线程
    server.serve_forever()
