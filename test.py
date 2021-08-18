import selectors
import socket
import threading
import queue

from selector_epoll_exclusive import EpollExclusiveSelector

SOCKET_ARGS = ('localhost', 1234)
SETUP_DONE = "anyway"
READ_DONE = "hereswonderwall"


def selector_thread(q: queue.Queue):
    sel = EpollExclusiveSelector()

    def accept(sock, mask):
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    def read(conn, mask):
        data = conn.recv(1000)  # Should be ready
        print("recv", data)
        sel.unregister(conn)
        conn.close()

    sock = socket.socket()
    sock.bind(SOCKET_ARGS)
    sock.listen(100)
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept)

    q.put(SETUP_DONE)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

            if callback is read:
                q.put(READ_DONE)
                return


def write_to_selector():
    sock = socket.create_connection(SOCKET_ARGS)
    sock.send(b"Anyway, here's wonderwall")


def main():
    sel_queue = queue.Queue()
    sel_thread_obj = threading.Thread(target=selector_thread, args=(sel_queue,), daemon=True)
    sel_thread_obj.start()
    status = sel_queue.get(timeout=15)
    if status != SETUP_DONE:
        raise Exception("Unexpected status from epoll thread:", status)

    write_to_selector()

    status = sel_queue.get(timeout=15)
    if status != READ_DONE:
        raise Exception("Unexpected status from epoll thread:", status)


if __name__ == "__main__":
    main()