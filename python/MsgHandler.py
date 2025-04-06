import sys
import time
import json
import socket


class Environment:
    @staticmethod
    def getPOSTData(environ):
        ContentLength = int(environ.get('CONTENT_LENGTH', 0))
        Data = environ['wsgi.input'].read(ContentLength)
        return Data


def application(environ, start_response):

    start_response('200 OK', [('Content-Type', 'application/json; charset=UTF-8')])

    if environ['REQUEST_METHOD'].upper() == 'POST':

        Params = json.loads(Environment.getPOSTData(environ))

        result = {}

        req_params = Params['MetaData']

        with open('/log/msg-in.json', 'a') as fh:
            fh.write(environ['REMOTE_ADDR'])
            fh.write(str(req_params))

        src_ip = environ['REMOTE_ADDR']

        if src_ip == '192.168.11.224':
            src_client = 'c1@one-two-here-we-go.test'

        if src_ip == '192.168.11.222':
            src_client = 'c2@one-two-here-we-go.test'

        req_params['session_src'] = src_client

        #try:
        for i in range(1):
            server_address = '/var/lib/msgserver/messageserver.socket'

            #try:
            for i in range(1):
                received = ''
                if req_params['type'] == 'SET' or req_params['type'] == 'DEL':
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                    sock.connect(server_address)
                    sock.sendall(bytes(json.dumps(req_params), 'utf-8'))
                    received = sock.recv(4096)
                    sock.close()
                if req_params['type'] == 'GET':
                    send_data = bytes(json.dumps(req_params), 'utf-8')
                    for i in range(0, 60):
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
                        sock.connect(server_address)
                        sock.sendall(send_data)
                        received = sock.recv(4096)
                        sock.close()
                        check = json.loads(received)
                        if check['messages'] is not None:
                            break
                        time.sleep(1)

            #except Exception as e:
            #    result['error'] = True
            #    result['exception_id'] = type(e).__name__
            #    result['exception'] = 'Server send error {0}'.format(e)
            #    raise e

            with open('/log/msgserver-rcv.json', 'a') as fh:
                fh.write(str(received))

            yield bytes(json.dumps(json.loads(received)), 'utf-8')

        #except Exception as e:
        #    result['error'] = True
        #    result['exception_id'] = type(e).__name__
        #    result['exception'] = '{0}'.format(e)

        #    with open('/log/exception.log', 'a') as fh:
        #        fh.write(str(e))

        #    yield bytes(json.dumps(result), 'utf-8')
