import ctypes
import ctypes.wintypes as wintypes
from multiprocessing import Process
from threading import Thread
import time
import wx.lib


class take:
    WM_KEYDOWN = 0x100
    WM_KEYUP = 0x101
    VK_K = 0x4B
    DOWN_K = 0x250001
    UP_K = 0xC0250001

    FREQ = 400
    DUR = 70

    user32 = ctypes.windll.user32

    FindWindow = user32.FindWindowW
    FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    # FindWindow.restype = wintypes.HWND

    PostMessage = user32.PostMessageW
    PostMessage.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    # PostMessage.restype = wintypes.BOOL

    beeper = ctypes.windll.Kernel32.Beep
    beeper.argtypes = [wintypes.DWORD, wintypes.DWORD]
    beeper.restype = wintypes.INT


    @staticmethod
    def connection() -> bool:
        if take.FindWindow(None, 'Live View') or take.FindWindow(None, 'Capture One'):
            return True
        else:
            return False

    @staticmethod
    def photo() -> bool:
        hwnd = take.FindWindow(None, 'Live View') or take.FindWindow(None, 'Capture One')
        if hwnd == 0:
            print('cannot find window')
            return False
        take.beep(5)
        print('photo')
        take.PostMessage(hwnd, take.WM_KEYDOWN, take.VK_K, take.DOWN_K)
        take.PostMessage(hwnd, take.WM_KEYUP, take.VK_K, take.UP_K)
        return True

    @staticmethod
    def photos() -> bool:
        hwnd = take.FindWindow(None, 'Live View') or take.FindWindow(None, 'Capture One')
        if hwnd == 0:
            print('cannot find window')
            return False
        else:
            app = wx.App()
            frame = takeframe(app, hwnd)
            app.MainLoop()
            app.Destroy()
            # for i in range(4):
            #     for s in range(6, 0, -1):
            #         if s == 1:
            #             Process(target=take.beep, args=(4,)).start()
            #             time.sleep(.8)
            #         else:
            #             Process(target=take.beep, args=(1,)).start()
            #             time.sleep(1)
            #     print('photo')
            #     take.PostMessage(hwnd, take.WM_KEYDOWN, take.VK_K, take.DOWN_K)
            #     take.PostMessage(hwnd, take.WM_KEYUP, take.VK_K, take.UP_K)
            return True

    @staticmethod
    def beep(rep: int):
        for i in range(rep):
            take.beeper(take.FREQ, take.DUR)
            time.sleep(.05)


class takeframe(wx.Frame):
    def __init__(self, app, hwnd):
        super().__init__(parent=None, title='hi...')
        self.hwnd = hwnd
        self.app = app
        self.SetForegroundColour(wx.Colour(255,255,255))
        self.SetBackgroundColour(wx.Colour(0,0,0))
        self.Show()
        self.Maximize(True)
        # self.SetWindowStyle(wx.STAY_ON_TOP)
        self.winheight = self.GetSize()[1]

        self.beeploop(4, 6)



    def beeploop(self, reps, time):
        if reps == 0:
            self.Destroy()
            self.app.ExitMainLoop()
            return
        self.beeps(time)
        wx.CallLater(6000, self.beeploop, reps-1, time)


    def beeps(self, time):
        if time == 0:
            take.PostMessage(self.hwnd, take.WM_KEYDOWN, take.VK_K, take.DOWN_K)
            take.PostMessage(self.hwnd, take.WM_KEYUP, take.VK_K, take.UP_K)
            return
        elif time == 1:
            self.countdown(time)
            Process(target=take.beep, args=(4,)).start()
            wx.CallLater(800, self.beeps, time-1)
        else:
            self.countdown(time)
            Process(target=take.beep, args=(1,)).start()
            wx.CallLater(900, self.beeps, time-1)


    def countdown(self, count: int):
        self.DestroyChildren()
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        font = wx.Font(wx.FontInfo(self.winheight//1.4))
        label = wx.TextCtrl(panel, -1, value=str(count), style=wx.NO_BORDER | wx.TE_READONLY | wx.TE_CENTER)
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour(255,255,255))
        label.SetBackgroundColour(wx.Colour(0,0,0))
        sizer.Add(label, 1, wx.EXPAND)
        

        self.Layout()
        self.Refresh()
