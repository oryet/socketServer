import sys
sys.path.append('../')

import logging.config
import threading
from PublicLib.Socket import socketServer as ss
from PublicLib import public as pub


if __name__ == "__main__":
    pub.loggingConfig('logging.conf')
    defaultSocketConfig = pub.loadDefaultSettings("socket.json")

    ip = defaultSocketConfig['ip']
    ipport = defaultSocketConfig['ipport']
    ADDRESS = (ip, ipport)
    logger = logging.getLogger('main')
    logger.info(ADDRESS)
    t = threading.Thread(target=ss.ServerMonitor, args=(None,logger))
    t.start()
    ts = threading.Thread(target=ss.SocketSendThread)
    ts.start()
    ss.ServerStart(ADDRESS)