import os
import pickle
import socket
import sys
import thread
import threading
import time

rank = 0
size = 1
WORLD = (0,)
ANY_SOURCE = None
ready = threading.Event()

_base_port = None
_recv_lock = threading.Lock()
# (from_rank, type, tag, msg)
_recv_queue = []

_bcast_id = 0
_barrier_id = 0
_gather_id = 0
_reduce_id = 0

_debug_enabled = False

# internal functions:

def _debug(msg):
    if _debug_enabled:
        print >>sys.stderr, '(%d) %s' % (rank, msg)

def _recv_thread():
    port = _base_port + rank
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', port))
    ready.set()
    s.listen(1025)

    # loop until we're the only thread left
    _debug('start _recv_thread loop')
    while threading.activeCount() > 0:
        _debug('loop...')

        # accept a connection, read its data, and add it to the queue
        s.settimeout(3)
        try:
            conn, addr = s.accept()
        except socket.timeout, e:
            continue
        s.settimeout(None)

        pieces = []
        while True:
            try:
                data = conn.recv(512)
            except socket.error, e:
                _debug('Warning in recv: %s' % `e`)
                continue
            if data:
                pieces.append(data)
            else:
                break
        conn.close()

        data = pickle.loads(''.join(pieces))
        q_rank, q_type, q_tag, q_msg = data
        _debug('received %s with (type=%s, tag=%s) from node %s ***' % (`q_msg`, `q_type`, `q_tag`, `q_rank`))

        _recv_lock.acquire()
        _recv_queue.append(data)
        _recv_lock.release()

    _debug('exited because activeCount was %d' % threading.activeCount())

    s.close()

def _send(type, msg, node, tag):
    if node == rank:
        # sending to ourself
        _recv_lock.acquire()
        _recv_queue.append((rank, type, tag, msg))
        _recv_lock.release()
    else:
        # sending to another node
        port = _base_port + node
        enc_data = pickle.dumps((rank, type, tag, msg))

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', port))
        s.sendall(enc_data)
        s.close()

def _recv(type, node, tag):
    found = False

    while not found:
        _recv_lock.acquire()
        for i, (q_rank, q_type, q_tag, q_msg) in enumerate(_recv_queue):
            if type == q_type and (node is None or node == q_rank) and \
              (tag is None or tag == q_tag):
                found = True
                _recv_queue.pop(i)
                break
        _recv_lock.release()
        if not found:
            time.sleep(0.01)

    return (q_msg, Status(q_rank, q_tag))

def _init():
    global rank
    global size
    global WORLD
    global _base_port

    if 'CCT_MPI_PARAMS' in os.environ:
        pieces = os.environ['CCT_MPI_PARAMS'].split(',')
        if len(pieces) == 3:
            rank, size, _base_port = map(int, pieces)
        else:
            raise Exception('Unexpected value for CCT_MPI_PARAMS')

        WORLD = range(size)
        thread.start_new_thread(_recv_thread, ())

        # give the servers a chance to start before any clients try to connect
        # time.sleep(4)
        ready.wait()
        time.sleep(1)
    else:
        print 'CCT_MPI_PARAMS not set. Wrong mpiexec?'
        sys.exit(0)

# helpful classes:

class Status:
    def __init__(self, source, tag):
        self.source = source
        self.tag = tag

# exposed functions:

def send(msg, node, tag=None):
    _debug('entering send (to %s, tag %s)...' % (`node`, `tag`))
    _send('send', msg, node, tag)
    _debug('...leaving send')

def recv(node=None, tag=None):
    _debug('entering recv (from %s, tag %s)...' % (`node`, `tag`))
    retval = _recv('send', node, tag)
    _debug('...leaving recv')
    return retval

def bcast(msg=None):
    global _bcast_id

    if msg is None:
        retval = _recv('bcast', None, _bcast_id)[0]
    else:
        for node in range(0, rank):
            _send('bcast', msg, node, _bcast_id)
        for node in range(rank + 1, size):
            _send('bcast', msg, node, _bcast_id)
        retval = msg

    _bcast_id = (_bcast_id + 1) % 100

    return retval

def barrier():
    global _barrier_id

    _debug('entering barrier...')

    # all send to node 0; node 0 sends to all

    if rank == 0:
        for node in range(1, size):
            _recv('barrier', node, _barrier_id)
        for node in range(1, size):
            _send('barrier', 'OK', node, _barrier_id)
    else:
        _send('barrier', 'OK', 0, _barrier_id)
        _recv('barrier', 0, _barrier_id)

    _barrier_id = (_barrier_id + 1) % 100

    _debug('...leaving barrier')

def gather(data):
    global _gather_id

    if rank == 0:
        retval = list(data)
        for node in range(1, size):
            retval.extend(_recv('gather', node, _gather_id)[0])
    else:
        _send('gather', data, 0, _gather_id)
        retval = None

    _gather_id = (_gather_id + 1) % 100

    return retval

def allgather(data):
    temp = gather(data)
    if rank == 0:
        bcast(temp)
    else:
        temp = bcast()
    return temp

def reduce(data, function, target=0):
    global _reduce_id

    if rank == target:
        retval = data
        for node in range(0, target):
            retval = function(retval, _recv('reduce', node, _reduce_id)[0])
        for node in range(target + 1, size):
            retval = function(retval, _recv('reduce', node, _reduce_id)[0])
    else:
        _send('reduce', data, target, _reduce_id)
        retval = None

    _reduce_id = (_reduce_id + 1) % 100

    return retval

def allreduce(data, function):
    temp = reduce(data, function)
    if rank == 0:
        bcast(temp)
    else:
        temp = bcast()
    return temp

# reduction functions:
BAND = lambda a, b: a & b
BOR = lambda a, b: a | b
BXOR = lambda a, b: a ^ b
LAND = lambda a, b: bool(a) and bool(b)
LOR = lambda a, b: bool(a) or bool(b)
LXOR = lambda a, b: bool(a) ^ bool(b)
MAX = lambda a, b: max(a, b)
MIN = lambda a, b: min(a, b)
PROD = lambda a, b: a * b
SUM = lambda a, b: a + b

_init()

