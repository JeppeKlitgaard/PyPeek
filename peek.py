from StringIO import StringIO  # Can't use cStringIO, as we cannot subclass it.
from tempfile import gettempdir
from platform import system
import os.path


class PeekDependencyMissing(Exception):
    pass


class PeekUnableToPeek(Exception):
    pass


class Screenshot(StringIO):
    """This object represents a screenshot, and has all the ordinary file-like
    methods.
    It also has a save method, give it an output path and it'll save it."""
    def save(self, outfile):
        with open(outfile, "wb") as f:
            f.write(self.getvalue())

    def addvalue(self, value):
        self.write(value)
        self.seek(0)


def tryimport(funcname):
    """Decorator for peekers"""  # Full disclosure, I have no idea how to
    # make decorators. I am fairly certain I am doing something horribly wrong
    def wrap(func):
        def new_func(*args, **kwargs):
            try:
                x = func(*args, **kwargs)
            except ImportError as error:
                raise PeekDependencyMissing("Couldn't import %s. Error: %s"
                                            % (funcname, error))
            return x
        return new_func
    return wrap


def _file2screen(path):
    """Takes a file from path and turns it into a screenshot object.
    Used for backends that don't support memory-buffers etc."""
    screenshot = Screenshot()
    with open(path, "rb") as f:
        screenshot.addvalue(f.read())

    return screenshot


def _gettempfile():
    """Returns a temporary file path.
    Used for backends that don't support memory-buffers etc."""
    fn = "dsktp_cache_framebuff.dat"
    f = os.path.join(gettempdir(), fn)
    return f


##############################################################################


@tryimport("PIL")
def peek_PIL(fmt="jpeg"):
    """Takes a screenshot using PIL."""
    from PIL import ImageGrab

    image = ImageGrab.grab()
    screenshot = Screenshot()
    image.save(screenshot, fmt)
    screenshot.seek(0)

    return screenshot


def _pywin32capture(path):
    import win32gui
    import win32ui
    import win32con
    import win32api

    hwin = win32gui.GetDesktopWindow()
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    bmp.SaveBitmapFile(memdc, path)


# See:
# http://stackoverflow.com/questions/4589206/python-windows-7-screenshot-without-pil
@tryimport("pywin32")
def peek_pywin32():
    """Takes a screenshot using pywin32."""
    path = _gettempfile()

    _pywin32capture(path)
    screenshot = _file2screen(path)

    return screenshot


# See:
# http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
@tryimport("gtk")
def peek_gtk():
    """Takes a screenshot using gtk."""
    from gtk import gdk
    window = gdk.get_default_root_window()
    size = window.get_size()
    buff = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, size[0], size[1])
    buff = buff.get_from_drawable(window, window.get_colormap(),
                                  0, 0, 0, 0, size[0], size[1])
    if buff is None:
        raise PeekUnableToPeek()

    path = _gettempfile()
    buff.save(path, "png")
    screenshot = _file2screen(path)

    return screenshot


# See:
# http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
@tryimport("qt")
def peek_qt(fmt="png"):
    """Takes a screenshot using QT."""
    import sys
    from PyQt4.QtGui import QPixmap, QApplication
    from PyQt4.Qt import QBuffer, QIODevice

    app = QApplication(sys.argv)
    buff = QBuffer()
    buff.open(QIODevice.ReadWrite)
    QPixmap.grabWindow(QApplication.desktop().winId()).save(buff, fmt)

    screenshot = Screenshot()
    screenshot.addvalue(buff.data())
    buff.close()
    del app

    return screenshot


# His implementation was far from working. :(
# http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
@tryimport("wx")
def peek_wx():
    """Takes a screenshot using wx."""
    import wx

    app = wx.App()

    screen = wx.ScreenDC()
    size = screen.GetSize()
    bmp = wx.EmptyBitmap(size[0], size[1])
    mem = wx.MemoryDC(bmp)
    mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
    del mem
    del app

    path = _gettempfile()
    bmp.SaveFile(path, wx.BITMAP_TYPE_PNG)
    screenshot = _file2screen(path)

    return screenshot


@tryimport("scrot")
def peek_scrot(multimonitor=False):
    """Takes a screenshot using subprocess and scrot."""
    import subprocess

    path = _gettempfile()
    COMMAND = "scrot"
    arg = ""

    if multimonitor:
        arg = "--multidisp"

    try:
        subprocess.call((COMMAND, path, arg))
    except OSError:  # scrot command wasn't found.
        raise ImportError

    screenshot = _file2screen(path)

    return screenshot


@tryimport("imagemagick")
def peek_imagemagick(fmt="png"):
    """Takes a screenshot using subprocess and imagemagick(import)."""
    import subprocess

    path = _gettempfile()
    path += "." + fmt

    COMMAND = "import -window root"

    try:
        subprocess.call((COMMAND, path))
    except OSError:  # import command wasn't found.:
        raise ImportError

    screenshot = _file2screen(path)

    return screenshot


PEEKERS = []
if system().lower() == "windows":  # If platform is windows:
    PEEKERS.append(peek_pywin32)
    PEEKERS.append(peek_PIL)
    pass


def peek():
    pass