import collections
import time
from functools import wraps
from typing import List, OrderedDict, Any, Tuple, Union, Dict, Callable


class Machine:
    """
    This is a parallel multitasking processor simulator.
    """

    def __init__(self, T: int, HALT: int) -> None:
        """
        Initialize a parallel simulator.
        :param T: The waiting time of each cycle of the simulator.
        :param HALT: The maximum number of termination cycles of the simulator.
        """
        # This data structure is used to save tasks (functions) waiting to be deployed.
        self.work_queue = collections.OrderedDict()  # type:OrderedDict
        # This data structure is used to record the time for waiting tasks that
        # need to be waited for.
        self.delay_pool = collections.OrderedDict()  # type:OrderedDict
        # This data structure is used to record the initial state of the
        # waiting task.
        self.delay_init = collections.OrderedDict()  # type:OrderedDict
        # This data structure is used to record the waiting task number.
        self.count = 0  # type:int
        # This data structure is used to control whether the simulator needs to
        # block waiting for IO input (standard input) in each cycle.
        self.IO_enable = False  # type:bool
        # This data structure is used to record the signal string to be
        # processed by each task.
        self.input_seq = collections.OrderedDict()  # type:OrderedDict
        # This data structure is used to record the PID of the current task.
        self.count_t = 0  # type: int
        # This data structure is used to record the execution task pool of the simulator.
        self.work_pool = collections.OrderedDict()  # type:OrderedDict
        # This data structure is used to record the status of each task at the end of the cycle.
        self.result_pool = collections.OrderedDict()  # type:OrderedDict
        # This data structure is used to record the global cycle number.
        self.timer = 1  # type:int
        # The waiting time of each cycle of the simulator.
        self.T = T  # type: int
        # The maximum number of termination cycles of the simulator.
        self.HALT = HALT  # type: int
        # This data structure is used to record the execution and termination of tasks.
        self.log_list = {}  # type: Dict
        # This data structure is used to provide a task queue.
        self.queue = []  # type: List
        # This data structure is used to record the input signal string of
        # tasks in the task queue.
        self.queue_temp = []  # type: List
        # This data structure is used to record the initial state of tasks in
        # the task queue.
        self.queue_init = []  # type: List
        # This data structure is used to record the PID of the task that the task queue is waiting for.
        self.current = -1  # type:int
        # This data structure is used to save the one-way interactive path
        # between tasks, the key is the master task, and the value is the slave
        # task list. The return value of the master task will be used as the
        # next signal to be passed to the slave task.
        self.channel = collections.OrderedDict()  # type:OrderedDict

    def call_after_delay(self, delay: int) -> Any:
        """
        This decorator is used to make a task execute after a period of delay.
        :param delay: number of delay cycles
        :return: a decorator
        """
        def decorator(fun: Callable[[str, str], Any]) -> Any:
            @wraps(fun)
            def wrapper(a: str, b: str) -> None:
                self.work_queue[self.count] = fun
                self.delay_pool[self.count] = delay
                self.delay_init[self.count] = b
                fun(a, b)
            return wrapper
        return decorator

    def call_by_queue(self, inp: str) -> Any:
        """
        This decorator is used to make a task enter the queue. When the simulator is running, the tasks in the task
        queue will be executed in sequence.
        :param inp: Task input signal string
        :return: a decorator
        """
        def decorator(fun: Callable[[str, str], Any]) -> Any:
            @wraps(fun)
            def wrapper(a: str, b: str) -> None:
                self.queue.append(fun)
                self.queue_temp.append(inp)
                self.queue_init.append(b)
            return wrapper
        return decorator

    def seq_sup(self, inp: str) -> Any:
        """
        This decorator is used to perform a task and load a string of input signals.
        :param inp: Task input signal string
        :return: a decorator
        """
        def decorator(fun: Callable[[str, str], Any]) -> Any:
            @wraps(fun)
            def wrapfun(a: str, b: str) -> None:
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

    def link_a_channel(self, PID: int):
        """
        This function is used to bind the input signal of a task to the output state of a running task (return value)
        :param PID: PID of the main task
        :return: a decorator
        """

        def decorator(fun: Callable[[str, str], Any]) -> Any:
            @wraps(fun)
            def wrapfun(a: str, b: str) -> None:
                if self.timer not in self.log_list.keys():
                    self.log_list[self.timer] = []
                self.work_pool[self.count_t] = fun
                self.input_seq[self.count_t] = []
                self.result_pool[self.count_t] = b
                self.log_list[self.timer].append(
                    ["Process execute", self.count_t])
                if PID in self.channel.keys():
                    self.channel[PID].append(self.count_t)
                else:
                    self.channel[PID] = [self.count_t]
                self.count_t += 1
                fun(a, b)

            return wrapfun

        return decorator

    def IO_en(self, IO: bool) -> Any:
        """
        This decorator is used to enable the I/O of the simulator (standard input, blocking).
        :param IO: Enable I/O status , True or False
        :return: a decorator
        """
        def decorator(fun: Callable[[str, str], Any]) -> Any:
            @wraps(fun)
            def wrapfun(a: str, b: str) -> None:
                self.IO_enable = IO
                fun(a, b)
            return wrapfun
        return decorator

    def IO_input(self) -> Tuple[Union[str, None], Union[List[str], None]]:
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

    def execute(self) -> None:
        """
        Run our simulator.
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
                    temp = int(a)
                    if isinstance(b, List):
                        for x in b:
                            self.input_seq[temp].append(x)
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
            for i in self.channel:
                for j in self.channel[i]:
                    if i in self.work_pool.keys() and j in self.work_pool.keys():
                        self.input_seq[j].append(self.result_pool[i])
            for i in dellist:
                del self.work_pool[i]
                del self.input_seq[i]
                del self.result_pool[i]
            self.timer += 1
            time.sleep(self.T)
