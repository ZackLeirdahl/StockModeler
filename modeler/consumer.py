from multiprocessing import Process
from task import ClientTask, FireTask, APITask
class Consumer(Process):
    def __init__(self, queue):
        Process.__init__(self)
        self.queue = queue
        self.start()

    def run(self):
        while True:
            while not self.queue.empty():
                task = self.queue.get()
                task.__class__ = eval(task.type)
                print(task)
                list(map(self.queue.put,task.do()))
