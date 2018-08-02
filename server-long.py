#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socketserver
import struct
import queue, threading, multiprocessing
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

# socket server类
class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):  # 所有请求的交互都是在handle里执行的,
        while True:
            try:
                data = bytearray(
                    self.request.recv(1024).strip())  # 每一个请求都会实例化MyTCPHandler(socketserver.BaseRequestHandler):
                ip = self.client_address[0]  # ip
                print("ip:{} wrote:{}".format(ip, data))
                if len(data) == 35:
                    pack_data = struct.unpack('>5sBiiiiiiic', data)
                    print(pack_data)
                    #pack_data[0]为设备号
                    if pack_data[0] == b'zy820' and pack_data[9] == b'#' and pack_data[1] != 0:
                        # 将sensor数据传到dict(sensor_data)
                        sensor_data['DeviceId'] = pack_data[0]
                        sensor_data['AirPressure'] = pack_data[2]
                        sensor_data['Humidity'] = pack_data[3]
                        sensor_data['Noise'] = pack_data[4]
                        sensor_data['Pm25'] = pack_data[5]
                        sensor_data['Temperature'] = pack_data[6]
                        sensor_data['WindDirection'] = pack_data[7]
                        sensor_data['WindSpeed'] = pack_data[8]
                        sensor_que.put(sensor_data, block=True)  # 如果full将一直等待，block=False则引发Full异常
                        print('sensor put in queue!')
                    else:
                        #pass
                        print('data error!')
                else:
                    #pass
                    print('len!=35')
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


def connect_sql():
    # 初始化数据库连接
    sqlite_engine = create_engine('sqlite:///lighting.db')  # ///后为path
    # 创建session类型，为后边创建session实例
    sqlite_session = sessionmaker(bind=sqlite_engine)


# 创建对象基类
Base = declarative_base()


# 定义Sensor类
class Sensor(Base):
    # 表的名字
    __tablename__ = 'sensor'

    # 表的结构
    dev_id = Column(String(10), primary_key=True)
    AirPressure = Column(Integer)
    Humidity = Column(Integer)
    Noise = Column(Integer)
    Pm25 = Column(Integer)
    Temperature = Column(Integer)
    WindDirection = Column(Integer)
    WindSpeed = Column(Integer)
    date = Column(String(20))


# 初始化数据库，创建表
def init_db():
    Base.metadata.create_all(sqlite_engine)


def drop_db():
    Base.metadata.drop_all(sqlite_engine)

# 从queue中取出sensor
def getsensor_que():
    while True:
        sensor = sensor_que.get(block=True)  # 阻塞，queue为空时，不会Queue.Empty异常
        print(sensor)
        savetosql(sensor)


# 将数据存到数据库
def savetosql(sensor):
    # 创建session对象
    session = sqlite_session()
    datet_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_sensor = Sensor(dev_id=sensor['DeviceId'], AirPressure=sensor['AirPressure'], Humidity=sensor['Humidity'],
                        Noise=sensor['Noise'], Pm25=sensor['Pm25'], Temperature=sensor['Temperature'],
                        WindDirection=sensor['WindDirection'], WindSpeed=sensor['WindSpeed'], date=datet_time)
    session.add(new_sensor)
    session.commit()
    session.close()


if __name__ == "__main__":
    sensor_que = queue.Queue()
    sensor_data = {'DeviceId': '', 'AirPressure': 0, 'Humidity': 0, 'Noise': 0, 'Pm25': 0, 'Temperature': 0,
                   'WindDirection': 0, 'WindSpeed': 0}
    # HOST, PORT = "localhost", 9999   #windows
    HOST, PORT = "0.0.0.0", 9999  # Linux
    server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)  # 线程
    server.serve_forever()
    print('before init_db!')
    connect_sql()
    init_db()
    print('after init_db!')
    for i in range(multiprocessing.cpu_count()):
        t = threading.Thread(target=getsensor_que)
        t.start()
