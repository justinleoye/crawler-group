import gevent
import grequests
import requests

#from socketIO_client import SocketIO
from gevent_socketio_client import SocketIO

from pyutils import *
from .response import Response

def fetch(req, **kwargs):
    url = req.get('url')
    socketio = req.get('socketio')
    binary = req.get('binary')
    streaming = req.get('streaming')
    headers = req.get('headers')
    timeout = req.get('timeout')
    chunk_size = req.get('chunk_size') or 512
    params = req.get('params')
    data = req.get('data')

    DEBUG("fetch url: %s" % url)

    if socketio:
        host = socketio.get('host')
        port = socketio.get('port')
        s= SocketIO(host, port)
        response = {
            '__socketio__': s,
            'headers': {}
        }
    else:
        if not streaming and timeout is None:
            timeout = 30
        r = grequests.get(url, stream=streaming, headers=headers, params=params, data=data, timeout=timeout)
        resp = r.send()

        response = {
            '__resp__': resp,
            'headers': resp.headers,
        }
    resp = Response(response)
    resp.set_encoding(req.encoding)
    return resp


