import logging.config
import threading
import PublicLib.Socket.socketServer as ss
import PublicLib.public as pub


if __name__ == "__main__":
    pub.loggingConfig('logging.conf')
    defaultSocketConfig = pub.loadDefaultSettings("socket.json")
    ip = defaultSocketConfig['ip']
    ipport = defaultSocketConfig['ipport']
    ADDRESS = (ip, ipport)
    logger = logging.getLogger('main')
    logger.info(ADDRESS)
    t = threading.Thread(target=ss.ServerMonitor, args=(None,))
    t.start()
    ts = threading.Thread(target=ss.SocketSendThread)
    ts.start()
    server = ss.socketserver.ThreadingTCPServer(ADDRESS, ss.Myserver)
    server.serve_forever()