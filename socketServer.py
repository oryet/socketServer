import json
import logging
import logging.config
import queue
import socketserver
import threading
import time
from ConnManage import ConnManage
from PublicLib.Protocol.prtl13761 import prtl3761

q = queue.Queue()
server = None
MAX_LIVE_TIME = (10*60*60)  # 1小时

global con
con = ConnManage()

class Myserver(socketserver.BaseRequestHandler):
    def handle(self):
        self.serverClass = {"ip": "", "port": "", "type": "", "recvData": ""}
        conn = self.request
        # 加入连接池
        con.Insert(conn, self.client_address[0], self.client_address[1], MAX_LIVE_TIME)
        # print("link ip:", str(self.client_address[0]), "port:", str(self.client_address[1]))
        p = prtl3761()

        while True:
            time.sleep(0.1)
            try:
                ret_bytes = conn.recv(2048)

                try:
                    ret_str = str(ret_bytes, encoding="utf-8")  # byte 转 字符串(utf8)
                    self.serverClass["type"] = "json"
                except:
                    ret_str = ''.join(['%02x' % b for b in ret_bytes]) # byte 转 字符串(hex)
                    self.serverClass["type"] = "hex"

                if len(ret_str) > 5:
                    self.serverClass["ip"] = str(self.client_address[0])
                    self.serverClass["port"] = str(self.client_address[1])
                    self.serverClass["recvData"] = ret_str

                    con.Updata(conn, self.client_address[0], self.client_address[1], MAX_LIVE_TIME)
                    q.put(self.serverClass)
                    if self.serverClass["type"] == "json":
                        if 'Login' in ret_str or 'Heart' in ret_str or 'Event' in ret_str:
                            conn.sendall(bytes(ret_str+" ",encoding="utf-8"))
                    elif self.serverClass["type"] == "hex":
                        ret_str = p.LoginHeartFrame(ret_str)
                        if ret_str is not None:
                            conn.sendall(bytes.fromhex(ret_str))
                elif len(ret_str) == 0:
                    self.remove()
                    break
            except:  # 意外掉线
                self.remove()
                break

    def finish(self):
        print("client remove!")

    def remove(self):
        print("client offline!", self.request)
        con.Delect(self.request)

def SocketSend(n, data):
    if 0 < con.GetLinkNum():
        if n < con.GetLinkNum():
            conn = con.GetConn(n)
            conn.sendall(bytes(data + " ", encoding="utf-8"))

def ServerMonitor():
    linkNum = 0
    while True:
        time.sleep(0.1)
        con.Live()

        if linkNum != con.GetLinkNum():
            linkNum = con.GetLinkNum()
            print("当前连接数：", linkNum)
            iplist = con.GetIpList()
            portlist = con.GetIpPortList()
            for i in range(con.GetLinkNum()):
                print(iplist[i],portlist[i])

        # if len(recvdata) > 5:
        while not q.empty():
            data = q.get()
            logger.info(data)
            print(data)


# 获取链接数量
def GetLinkNum():
    return con.GetLinkNum()

def ServerClose():
    server.shutdown()
    server.server_close()

def ServerStart(ADDRESS):
    global server
    server = socketserver.ThreadingTCPServer(ADDRESS, Myserver)
    server.serve_forever()
    return

def loggingConfig():
    logging.config.fileConfig('loggingsocket.conf')
    logger = logging.getLogger('main')
    logger.info('Logging main Start')

def loadSocketDefaultSettings():
    try:
        socketConfigFile = open("socket.json")
        defaultSocketConfig = json.load(socketConfigFile)
        print(defaultSocketConfig)
    finally:
        if socketConfigFile:
            socketConfigFile.close()
            return defaultSocketConfig

if __name__ == "__main__":
    loggingConfig()
    defaultSocketConfig = loadSocketDefaultSettings()
    ip = defaultSocketConfig['ip']
    ipport = defaultSocketConfig['ipport']
    ADDRESS = (ip, ipport)
    logger = logging.getLogger('main')
    logger.info(ADDRESS)
    t = threading.Thread(target=ServerMonitor)
    t.start()
    server = socketserver.ThreadingTCPServer(ADDRESS, Myserver)
    server.serve_forever()
