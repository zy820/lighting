#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socketserver
import struct
import queue,threading,multiprocessing
from sqlalchemy import Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sensor_que = queue.Queue()
sensor_data = {'AirPressure':0,'Humidity':0,'Noise':0,'Pm25':0,'Temperature':0,'WindDirection':0,'WindSpeed':0}

#socket server类
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
                    if pack_data[0] == '#' && pack_data[9] == '#' && pack_data[1] != 0x00:       #pack_data[0]
                        #将sensor数据传到dict(sensor_data)
                        sensor_data['AirPressure']   = pack_data[2]
                        sensor_data['Humidity']      = pack_data[3]
                        sensor_data['Noise']         = pack_data[4]
                        sensor_data['Pm25']          = pack_data[5]
                        sensor_data['Temperature']   = pack_data[6]
                        sensor_data['WindDirection'] = pack_data[7]
                        sensor_data['WindSpeed']     = pack_data[8]
                        sensor_que.put(sensor_data,block=True)      #如果full将一直等待，block=False则引发Full异常
                    else:
                        pass
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


#初始化数据库连接
sqlite_engine = create_engine('sqlite:///lighting.db')    #///后为path
sqlite_session =  sessionmaker(bind=sqlite_engine)

#创建对象基类
Base = declarative_base()

#初始化数据库，创建表
def init_db():
    Base.metadata.create_all(sqlite_engine)

def drop_db():
    Base.metadata.drop_all(sqlite_engine)

#定义Sensor类
class Sensor(Base):
    #表的名字
    __tablename__ = 'sensor'

    #表的结构


#从queue中取出sensor
def getsensor_que():
    while True:
        sensor = sensor_que.get(block=True)       #阻塞，queue为空时，不会Queue.Empty异常
        print(sensor)
        savetosql(sensor)

#将数据存到数据库
def savetosql(sensor):
    #连接数据库，存入sensor数据



for i in range(multiprocessing.cpu_count()):
    t = threading.Thread(target=getsensor_que)
    t.start()

if __name__ == "__main__":
    # HOST, PORT = "localhost", 9999   #windows
    HOST, PORT = "0.0.0.0", 9999  # Linux
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)  # 线程
    server.serve_forever()
