import zmq
import sys
from util import run_daemon
import logging

logger = logging.getLogger(__name__)
    
# --------------- SETUP CONNECTION --------------- #    
def get_response_server(addr):
    return get_server_conn(addr, zmq.REP)
    
def get_publisher_server(addr):
    return get_server_conn(addr, zmq.PUB)
    
def get_subscriber_server(addr, filter):
    return get_server_conn(addr, zmq.SUB, filter)
    
def get_server_conn(addr, type, filter=None):
    logger.debug("Opening server @ {0}".format(addr))
    context = zmq.Context()
    replier = context.socket(type)
    replier.bind(addr)
    if type == zmq.SUB:
        replier.setsockopt(zmq.SUBSCRIBE, filter)
    logger.info("Server open @ {0}".format(addr))
    return replier
    
def get_request_client(addr):
    return get_client_conn(addr, zmq.REQ)
    
def get_subscriber_client(addr, filter):
    return get_client_conn(addr, zmq.SUB, filter)
    
def get_publisher_client(addr):
    return get_client_conn(addr, zmq.PUB)
    
def get_client_conn(addr, type, filter=None):
    logger.debug("Connecting to {0}".format(addr))
    context = zmq.Context()
    client = context.socket(type)
    client.connect(addr)
    if type == zmq.SUB:
        client.setsockopt(zmq.SUBSCRIBE, filter)
    return client
    
def get_address(proto, name):
    translate_table = { "ipc": "ipc:///", "tcp": "tcp://" }
    return translate_table.get(proto, "{0}://".format(proto))+name
    
def get_tcp_address(ip, port):
    return get_address("tcp", "{0}:{1}".format(ip, port))
    
def get_icp_address(path):
    return get_address("ipc", path)
  
 
# --------------------- ADVANCED STUFFS ----------------- #
keep_listening = {}
    
def run_listener(name, conn, callback, preprocessor=None, use_main_thread=False):
    def run(name, conn, callback):
        keep_listening[name] = True
        while keep_listening[name] is True:
            try:
                try:
                    msg = conn.recv_string()
                except:
                    pass
                else:
                    if preprocessor is not None:
                        msg = preprocessor(msg)
                    #run_daemon(target=callback, args=(name, msg,))
                    callback(name, msg)
            except:
                logger.warning("WARNING: Got an exception while reading server messages!", exc_info=True)
                break
        conn.close()
        
    if use_main_thread:
        run(name, conn, callback)
    else:
        run_daemon(target=run, args=(name, conn, callback))
    
def stop_server(name):
    keep_listening[name] = False
    
def perform_request(requester, request, callback):
    requester.send(request)
    msg = requester.recv()
    if callback is not None:
        callback(msg)
  