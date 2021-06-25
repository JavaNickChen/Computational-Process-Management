import unittest
import io
import sys
from main import machine
# from main import Process_Termination
# from main import Process_execute

class Lab3Test(unittest.TestCase):
    def test_call_after_delay(self):
        cnc = machine(1,10)
        @cnc.call_after_delay(3)
        def t(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == 0:
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False
        t(None, "0")
        cnc.execute()
        self.assertEqual(cnc.log_list[4][0][0], "Process execute")
        self.assertEqual(cnc.log_list[4][0][1], 0)

    def test_seq_sup(self):
        cnc = machine(1, 10)
        @cnc.seq_sup(['0','0','0','1'])
        def t(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == 0:
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False
        t(None, "0")
        cnc.execute()
        self.assertEqual(cnc.log_list[1][0][0], "Process execute")
        self.assertEqual(cnc.log_list[4][0][0], "Process termination")



    def test_IO(self):
        cnc = machine(1, 10)
        @cnc.IO_en(True)
        @cnc.seq_sup(["0"])
        def t(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == 0:
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False
        t(None, "0")
        def stub_stdin(testcase_inst, inputs):
            stdin = sys.stdin
            def cleanup():
                sys.stdin = stdin
            testcase_inst.addCleanup(cleanup)
            sys.stdin = io.StringIO(inputs)
        stub_stdin(self,'0\n0 0 0 1\n\n\n\n\n\n\n\n\n\n\n\n\n')
        cnc.execute()
        self.assertEqual(cnc.log_list[1][0][0], "Process execute")
        self.assertEqual(cnc.log_list[1][0][1], 0)
        self.assertEqual(cnc.log_list[5][0][0], "Process termination")
        self.assertEqual(cnc.log_list[5][0][1], 0)


    def test_parallel(self):
        cnc = machine(1, 10)
        @cnc.IO_en(True)
        @cnc.seq_sup(['0','0','0','0','0','1'])
        def num(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == 0:
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False

        @cnc.IO_en(True)
        @cnc.call_after_delay(1)
        def char(inp, out):
            if not inp:
                return "a", False
            elif inp == "a":
                if out == "a":
                    return "a", False
                elif out == "b":
                    return "b", True
            return inp, False

        num(None, "0")
        char(None, 'a')

        def stub_stdin(testcase_inst, inputs):
            stdin = sys.stdin

            def cleanup():
                sys.stdin = stdin

            testcase_inst.addCleanup(cleanup)
            sys.stdin = io.StringIO(inputs)

        stub_stdin(self, '\n1\na a b\n\n\n\n\n\n\n\n\n\n\n\n\n')
        cnc.execute()
        self.assertEqual(cnc.log_list[1][0][0], "Process execute")
        self.assertEqual(cnc.log_list[1][0][1], 0)
        self.assertEqual(cnc.log_list[2][0][0], "Process execute")
        self.assertEqual(cnc.log_list[2][0][1], 1)
        self.assertEqual(cnc.log_list[4][0][0], "Process termination")
        self.assertEqual(cnc.log_list[4][0][1], 1)
        self.assertEqual(cnc.log_list[6][0][0], "Process termination")
        self.assertEqual(cnc.log_list[6][0][1], 0)

    def test_queue(self):
        cnc = machine(1, 10)
        @cnc.call_by_queue(['0', '0', '0', '0','1'])
        def num(inp, out):
            if not inp:
                return "0", False
            elif inp == "0":
                if out == 0:
                    return "0", False
                elif out == "1":
                    return "1", True
            return inp, False


        @cnc.call_by_queue(['a', 'a', 'a', 'b'])
        def char(inp, out):
            if not inp:
                return "a", False
            elif inp == "a":
                if out == "a":
                    return "a", False
                elif out == "b":
                    return "b", True
            return inp, False

        num(None, "0")
        char(None, 'a')
        cnc.execute()
        self.assertEqual(cnc.log_list[1][0][0], "Process execute")
        self.assertEqual(cnc.log_list[1][0][1], 0)
        self.assertEqual(cnc.log_list[5][0][0], "Process termination")
        self.assertEqual(cnc.log_list[5][0][1], 0)
        self.assertEqual(cnc.log_list[5][1][0], "Process execute")
        self.assertEqual(cnc.log_list[5][1][1], 1)
        self.assertEqual(cnc.log_list[9][0][0], "Process termination")
        self.assertEqual(cnc.log_list[9][0][1], 1)