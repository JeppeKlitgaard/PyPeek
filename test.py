import unittest
import peek
from timeit import timeit
import platform
from time import sleep

unix = True
if platform.system().lower() == "windows":
    unix = False


## This is an unintelligent test.
## Only tests if they actually run without errors.
class PeekTestDefault(unittest.TestCase):
    @unittest.skipIf(unix, "This peeker only works on Windows.")
    def test_peek_PIL(self):
        peek.peek_PIL()

    @unittest.skipIf(unix, "This peeker only works on Windows.")
    def test_peek_pywin32(self):
        peek.peek_pywin32()

    def test_peek_gtk(self):
        peek.peek_gtk()

    def test_peek_qt(self):
        peek.peek_qt()

    def test_peek_wx(self):
        peek.peek_wx()

    @unittest.skipIf(not unix, "This peeker only works on unix.")
    def test_peek_scrot(self):
        peek.peek_scrot()

    @unittest.skipIf(not unix, "This peeker only works on unix.")
    def test_peek_imagemagick(self):
        peek.peek_imagemagick()


def test_peek_time(num=10, gc=False, average=True):
    setupstr = ""
    if gc:
        setupstr += "gc.enable();"
    setupstr += "import peek"
    times = {}

    if not unix:
        times["PIL"] = timeit("peek.peek_PIL()",
                              setup=setupstr, number=num)

    if not unix:
        times["pywin32"] = timeit("peek.peek_pywin32()",
                                  setup=setupstr, number=num)

    times["gtk"] = timeit("peek.peek_gtk()",
                          setup=setupstr, number=num)

    times["qt"] = timeit("peek.peek_qt()",
                         setup=setupstr, number=num)

    times["wx"] = timeit("peek.peek_wx()",
                         setup=setupstr, number=num)

    if unix:
        times["scrot"] = timeit("peek.peek_scrot()",
                                setup=setupstr, number=num)

    if unix:
        times["imagemagick"] = timeit("peek.peek_imagemagick()",
                                      setup=setupstr, number=num)

    #AVERAGE NUMBERS
    if average:
        times = {k: v/num for k, v in times.iteritems()}

    return times


if __name__ == "__main__":
    print("\n###UNITTEST###\n")
    unittest.main(exit=False)

    sleep(3)

    print("\n###TIMES###\n")
    times = test_peek_time(num=1)
    for v in sorted(times, key=times.get):
        print "%-10s: %s" % (v, times[v])
