import collections
import time
from functools import wraps


class machine:
    """
    This is a parallel multitasking processor simulator
    """

    def __init__(self, T, HALT):
        """
        Initialize a parallel simulator
        :param T: The waiting time of each cycle of the simulator
        :param HALT: The maximum number of termination cycles of the simulator
        """
        # This data structure is used to save tasks (functions) waiting to be
        # deployed
        self.work_queue = collections.OrderedDict()
        # This data structure is used to record the time for waiting tasks that
        # need to be waited for
        self.delay_pool = collections.OrderedDict()
        # This data structure is used to record the initial state of the
        # waiting task
        self.delay_init = collections.OrderedDict()
        # This data structure is used to record the waiting task number
        self.count = 0
        # This data structure is used to control whether the simulator needs to
        # block waiting for IO input (standard input) in each cycle
        self.IO_enable = False
        # This data structure is used to record the signal string to be
        # processed by each task
        self.input_seq = collections.OrderedDict()
        # This data structure is used to record the PID of the current task
        self.count_t = 0
        # This data structure is used to record the execution task pool of the
        # simulator
        self.work_pool = collections.OrderedDict()
        # This data structure is used to record the status of each task at the
        # end of the cycle
        self.result_pool = collections.OrderedDict()
        # This data structure is used to record the global cycle number
        self.timer = 1
        # The waiting time of each cycle of the simulator
        self.T = T
        # The maximum number of termination cycles of the simulator
        self.HALT = HALT
        # This data structure is used to record the execution and termination
        # of tasks
        self.log_list = {}
        # This data structure is used to provide a task queue
        self.queue = []
        # This data structure is used to record the input signal string of
        # tasks in the task queue
        self.queue_temp = []
        # This data structure is used to record the initial state of tasks in
        # the task queue
        self.queue_init = []
        # This data structure is used to record the PID of the task that the
        # task queue is waiting for
        self.current = -1

    def call_after_delay(self, delay):
        """
        This decorator is used to make a task execute after a period of delay
        :param delay: number of delay cycles
        :return: a decorator
        """
        def decorator(fun):
            @wraps(fun)
            def wrapper(a, b):
                self.work_queue[self.count] = fun
                self.delay_pool[self.count] = delay
                self.delay_init[self.count] = b
                fun(a, b)
            return wrapper
        return decorator

    def call_by_queue(self, inp):
        """
        This decorator is used to make a task enter the queue. When the simulator is running, the tasks in the task queue will be executed in sequence
        :param inp: Task input signal string
        :return: a decorator
        """
        def decorator(fun):
            @wraps(fun)
            def wrapper(a, b):
                self.queue.append(fun)
                self.queue_temp.append(inp)
                self.queue_init.append(b)
            return wrapper
        return decorator

    def seq_sup(self, inp):
        """
        This decorator is used to perform a task and load a string of input signals
        :param inp: Task input signal string
        :return: a decorator
        """
        def decorator(fun):
            @wraps(fun)
            def wrapfun(a, b):
                if self.timer not in self.log_list.keys():
                    self.log_list[self.timer] = []
                self.work_pool[self.count_t] = fun
                self.input_seq[self.count_t] = inp
                self.result_pool[self.count_t] = b
                self.log_list[self.timer].append(
                    ["Process execute", self.count_t])
                self.count_t += 1
                fun(a, b)
            return wrapfun
        return decorator

    def IO_en(self, IO):
        """
        This decorator is used to enable the IO of the simulator (standard input, blocking)
        :param IO: Enable IO status , True or False
        :return: a decorator
        """
        def decorator(fun):
            @wraps(fun)
            def wrapfun(a, b):
                self.IO_enable = IO
                fun(a, b)
            return wrapfun
        return decorator

    def IO_input(self):
        """
        This function is used to process the IO input in the simulator.
        In a certain test method, I use unittest to modify the return value of this function to provide a test on the standard input.
        In the latest version, I used input redirection.
        :return: standard input.  a: index   b: string of signal
        """
        a = input()
        if a:
            b = input().split(" ")
            return a, b
        else:
            return None, None

    def execute(self):
        """
        Run our simulator
        :return: nothing
        """

        while True:
            if self.timer not in self.log_list.keys():
                self.log_list[self.timer] = []
            if self.current == -1:
                if len(self.queue) > 0:
                    self.work_pool[self.count_t] = self.queue[0]
                    self.input_seq[self.count_t] = self.queue_temp[0]
                    self.result_pool[self.count_t] = self.queue_init[0]
                    self.log_list[self.timer].append(
                        ["Process execute", self.count_t])
                    self.current = self.count_t
                    self.count_t += 1
                    del self.queue[0]
                    del self.queue_temp[0]
                    del self.queue_init[0]

            if self.timer == self.HALT:
                break
            for i in self.delay_pool:
                if self.delay_pool[i] == 0:
                    self.work_pool[self.count_t] = self.work_queue[i]
                    self.input_seq[self.count_t] = []
                    self.result_pool[self.count_t] = self.delay_init[i]
                    self.log_list[self.timer].append(
                        ["Process execute", self.count_t])
                    self.count_t += 1
                self.delay_pool[i] = self.delay_pool[i] - 1
            if self.IO_enable:
                a, b = self.IO_input()
                if a:
                    a = int(a)
                    for x in b:
                        self.input_seq[a].append(x)
            dellist = []
            for i in self.result_pool:
                if len(self.input_seq[i]) != 0:
                    self.result_pool[i], Terminal = self.work_pool[i](
                        self.result_pool[i], self.input_seq[i][0])
                    del self.input_seq[i][0]
                else:
                    self.result_pool[i], Terminal = self.work_pool[i](
                        self.result_pool[i], None)
                if Terminal:
                    self.log_list[self.timer].append(
                        ["Process termination", i])
                    dellist.append(i)
                    if self.current == i:
                        if len(self.queue) > 0:
                            self.work_pool[self.count_t] = self.queue[0]
                            self.input_seq[self.count_t] = self.queue_temp[0]
                            self.result_pool[self.count_t] = self.queue_init[0]
                            self.log_list[self.timer].append(
                                ["Process execute", self.count_t])
                            self.current = self.count_t
                            self.count_t += 1
                            del self.queue[0]
                            del self.queue_temp[0]
                            del self.queue_init[0]
            for i in dellist:
                del self.work_pool[i]
                del self.input_seq[i]
                del self.result_pool[i]
            self.timer += 1
            time.sleep(self.T)
