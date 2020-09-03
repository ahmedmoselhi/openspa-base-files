instanceTab = []

class DelayedFunction:

    def __init__(self, delay, function, *params):
        global instanceTab
        from enigma import eTimer
        try:
            instanceTab.append(self)
            self.function = function
            self.params = params
            self.timer = None
            self.timer = eTimer()
            self.timer.timeout.get().append(self.timerLaunch)
            self.timer.start(delay, False)
        except Exception as e:
            print '[spDF] __init__ exception:\n%s:%s' % (str(self.function), str(e))

    def cancel(self):
        try:
            instanceTab.remove(self)
            self.timer.stop()
            self.timer.timeout.get().remove(self.timerLaunch)
            self.timer = None
        except Exception as e:
            print '[spDF] timer cancel exception:\n%s:%s' % (str(self.function), str(e))

    def timerLaunch(self):
        try:
            instanceTab.remove(self)
            self.timer.stop()
            self.timer.timeout.get().remove(self.timerLaunch)
            self.timer = None
            self.function(*self.params)
        except Exception as e:
            print '[spDF] timerLaunch exception:\n%s:%s' % (str(self.function), str(e))
