from spzVirtualKeyboard import spzVirtualKeyboard
from Components.config import KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END, KEY_0, KEY_DELETE, KEY_BACKSPACE, KEY_OK, KEY_TOGGLEOW, KEY_ASCII, KEY_TIMEOUT, KEY_NUMBERS, ConfigElement, ConfigText, ConfigPassword, ConfigNumber, config
from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Input import Input
from Tools.BoundFunction import boundFunction

def pondebug(texto):
    if False:
        from os import system
        system('date >> /tmp/modE2.log')
        system("echo '" + texto + "'>>/tmp/modE2.log")
        system("echo '*******************************'>>/tmp/modE2.log")


def testtest(par1 = None, par2 = None, par3 = None, par4 = None):
    from os import system
    system('date >> /tmp/modE2.log')
    system("echo '*******************************'>>/tmp/modE2.log")
    system('echo "[' + str(par1) + ']">>/tmp/modE2.log')
    system("echo '*******************************'>>/tmp/modE2.log")


def ib__init__(self, session, title = '', windowTitle = _('Input'), useableChars = None, **kwargs):
    Screen.__init__(self, session)
    self['text'] = Label(title)
    self['input'] = Input(**kwargs)
    self.titulo = windowTitle
    self.onShown.append(boundFunction(self.setTitle, windowTitle))
    self.mostrado = False
    self.caracteres = useableChars
    if useableChars is not None:
        self['input'].setUseableChars(useableChars)
    self['actions'] = NumberActionMap(['WizardActions',
     'InputBoxActions',
     'InputAsciiActions',
     'KeyboardInputActions'], {'gotAsciiCode': self.gotAsciiCode,
     'ok': self.go,
     'back': self.cancel,
     'left': self.keyLeft,
     'right': self.keyRight,
     'home': self.keyHome,
     'end': self.keyEnd,
     'deleteForward': self.keyDelete,
     'deleteBackward': self.keyBackspace,
     '1': self.keyNumberGlobal,
     '2': self.keyNumberGlobal,
     '3': self.keyNumberGlobal,
     '4': self.keyNumberGlobal,
     '5': self.keyNumberGlobal,
     '6': self.keyNumberGlobal,
     '7': self.keyNumberGlobal,
     '8': self.keyNumberGlobal,
     '9': self.keyNumberGlobal,
     '0': self.keyNumberGlobal}, -1)
    if self['input'].type == Input.TEXT:
        self.onShown.append(boundFunction(abrespzKeyboard, self))


def abrespzKeyboard(instance, parama = None):
    if not instance.mostrado:
        instance.mostrado = True
        cb_func = lambda ret: VirtualKeyBoardCallback(instance, ret)
        inputtitulo = instance.getTitle()
        instance.setTitle('__spzVirtualKeyboard__')
        instance.session.openWithCallback(cb_func, spzVirtualKeyboard, titulo=inputtitulo + '. ' + instance['text'].getText(), texto=instance['input'].getText(), caracteres=instance.caracteres)


def VirtualKeyBoardCallback(obj = None, callback = None):
    if obj is not None:
        if callback is not None:
            try:
                obj['input'].setText(callback)
            except:
                pass

            try:
                obj.go()
            except:
                pass

        else:
            try:
                obj.cancel()
            except:
                pass


def abrespzKeyboard2(instance, parama = None):
    cb_func = lambda ret: VirtualKeyBoardCallback2(instance, ret)
    inputtitulo = instance.getTitle()
    loscar = None
    try:
        loscar = instance['input'].useableChars
    except:
        pass

    try:
        if instance['input'].type == Input.NUMBER:
            loscar = '01223456789'
    except:
        pass

    instance.session.openWithCallback(cb_func, spzVirtualKeyboard, titulo=inputtitulo + '. ' + instance['text'].getText(), texto=instance['input'].getText(), caracteres=loscar)


def VirtualKeyBoardCallback2(obj = None, callback = None):
    if obj is not None:
        if callback is not None:
            try:
                obj['input'].setText(callback)
            except:
                pass


def sispzKeyboard(instance):
    ret = False
    siwizard = False
    try:
        if not instance.session.current_dialog.numSteps == None:
            siwizard = True
            pondebug('sispzKeyboard siwizard true')
    except:
        pondebug('err sispzKeyboard siwizard')

    try:
        if not siwizard and isinstance(instance['config'].getCurrent()[1], ConfigText) and not isinstance(instance['config'].getCurrent()[1], ConfigNumber):
            ret = True
            pondebug('sispzKeyboard ret true')
    except:
        pondebug('err sispzKeyboard ret true')
        return False

    pondebug('sispzKeyboard ret ' + str(ret))
    return ret


def vk_keyLeft(instance):
    pondebug('vk_keyLeft' + str(instance))
    if sispzKeyboard(instance):
        pondebug('sispzKeyboard' + str(instance))
        abrespzKeyboardCL(instance)
    else:
        pondebug('else sispzkeyboare' + str(instance))
        instance['config'].handleKey(KEY_LEFT)
        try:
            instance.__changed()
        except:
            pass


def vk_keyRight(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_RIGHT)
        try:
            instance.__changed()
        except:
            pass


def vk_keyHome(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_HOME)
        try:
            instance.__changed()
        except:
            pass


def vk_keyEnd(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_END)
        try:
            instance.__changed()
        except:
            pass


def vk_keyDelete(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_DELETE)
        try:
            instance.__changed()
        except:
            pass


def vk_keyBackspace(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_BACKSPACE)
        try:
            instance.__changed()
        except:
            pass


def vk_keyToggleOW(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_TOGGLEOW)
        try:
            instance.__changed()
        except:
            pass


def vk_keyGotAscii(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_ASCII)
        try:
            instance.__changed()
        except:
            pass


def vk_KeyText(instance):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)


def vk_keyNumberGlobal(instance, number):
    if sispzKeyboard(instance):
        abrespzKeyboardCL(instance)
    else:
        instance['config'].handleKey(KEY_0 + number)
        try:
            instance.__changed()
        except:
            pass


def abrespzKeyboardCL(instance):
    cb_func = lambda ret: not ret or VirtualKeyBoardCallbackCL(instance, ret)
    pondebug('abrespzKeyboardCL')
    instance.session.openWithCallback(cb_func, spzVirtualKeyboard, titulo=instance['config'].getCurrent()[0], texto=instance['config'].getCurrent()[1].getValue(), caracteres='-(tab)')


def VirtualKeyBoardCallbackCL(obj = None, callback = None):
    if callback is not None and obj is not None:
        try:
            obj['config'].getCurrent()[1].setValue(callback)
        except:
            pass

        try:
            obj['config'].invalidate(obj['config'].getCurrent())
        except:
            pass


def modE2components():
    pondebug('modE2components')
    cambiavke()
    opcionvaliente = True
    from Screens.InputBox import InputBox
    if opcionvaliente:
        try:
            InputBox.__init__ = ib__init__
        except:
            pass

    else:
        try:
            InputBox.keyInsert = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyTab = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyBackspace = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyEnd = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyHome = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyDelete = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyNumberGlobal = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyRight = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.keyLeft = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.gotAsciiCode = abrespzKeyboard2
        except:
            pass

        try:
            InputBox.KeyText = abrespzKeyboard2
        except:
            pass

    from Components.ConfigList import ConfigListScreen
    try:
        ConfigListScreen.keyLeft = vk_keyLeft
    except:
        pondebug('keyLeft error')

    try:
        ConfigListScreen.keyRight = vk_keyRight
    except:
        pass

    try:
        ConfigListScreen.keyHome = vk_keyHome
    except:
        pass

    try:
        ConfigListScreen.keyEnd = vk_keyEnd
    except:
        pass

    try:
        ConfigListScreen.keyDelete = vk_keyDelete
    except:
        pass

    try:
        ConfigListScreen.keyBackspace = vk_keyBackspace
    except:
        pass

    try:
        ConfigListScreen.keyToggleOW = vk_keyToggleOW
    except:
        pass

    try:
        ConfigListScreen.keyGotAscii = vk_keyGotAscii
    except:
        pass

    try:
        ConfigListScreen.keyNumberGlobal = vk_keyNumberGlobal
    except:
        pass

    try:
        ConfigListScreen.KeyText = vk_KeyText
    except:
        pass

    from Screens.InfoBarGenerics import InfoBarSeek
    InfoBarSeek.checkSkipShowHideLock = spa_checkSkipShowHideLock
    from Screens.PVRState import PVRState
    PVRState.__init__ = __init__PVRState


def __init__PVRState(self, session):
    Screen.__init__(self, session)
    self['state'] = Label(text='')
    try:
        self['pixstateplay'] = Pixmap()
        self['pixstatepause'] = Pixmap()
        self['pixstateplay'].hide()
        self['pixstatepause'].hide()
    except:
        pass


def spa_checkSkipShowHideLock(self):
    wantlock = self.seekstate != self.SEEK_STATE_PLAY
    try:
        self.pvrStateDialog['pixstateplay'].hide()
        self.pvrStateDialog['pixstatepause'].hide()
        if self.seekstate == self.SEEK_STATE_PLAY:
            self.pvrStateDialog['pixstateplay'].show()
            self.pvrStateDialog['state'].setText('')
        elif self.seekstate == self.SEEK_STATE_PAUSE:
            self.pvrStateDialog['pixstatepause'].show()
            self.pvrStateDialog['state'].setText('')
    except:
        pass

    if config.usage.show_infobar_on_skip.value:
        if self.lockedBecauseOfSkipping and not wantlock:
            self.unlockShow()
            self.lockedBecauseOfSkipping = False
        if wantlock and not self.lockedBecauseOfSkipping:
            self.lockShow()
            self.lockedBecauseOfSkipping = True


from Screens import VirtualKeyBoard

class openspaVirtualKeyBoard(spzVirtualKeyboard):

    def __init__(self, session, title = '', text = ''):
        spzVirtualKeyboard.__init__(self, session, titulo=_(title), texto=text)


def cambiavke():
    VirtualKeyBoard.VirtualKeyBoard = openspaVirtualKeyBoard


gtexto = ''
gtitulo = ''

def vkos__init__(self, session, title = '', text = ''):
    global gtitulo
    global gtexto
    Screen.__init__(self, session)
    self.keys_list = []
    self.shiftkeys_list = []
    self.lang = None
    self.nextLang = None
    self.shiftMode = False
    self.text = text
    self.title = title
    gtexto = text
    gtitulo = title
    self.selectedKey = 0
    self.smsChar = None
    self['country'] = Label('')
    self['header'] = Label('')
    self['text'] = Label('')
    self['list'] = Label('')
    self.onShow.append(self.switchLang)


def opsswitchLang(self):
    self.session.openWithCallback(self.ok, spzVirtualKeyboard, titulo=self.titulo + '. ' + self.text, texto=self.text)


def opsok(self, resp):
    self.close(resp)
