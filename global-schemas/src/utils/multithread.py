from queue import Queue
from threading import Thread


def start_threads_and_queues(nbr_threads, function, args: Dict = {}):

    for _ in range(nbr_threads):
        t = Thread(target=function, args=(args,))
        t.daemon = True
        t.start()
