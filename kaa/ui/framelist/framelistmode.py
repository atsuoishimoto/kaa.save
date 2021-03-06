import kaa
from kaa.command import Commands, command
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.keyboard import *

FrameListThemes = {
    'default':
        Theme([
            Style('default', 'default', 'Blue'),
            Style('caption', 'red', 'Blue'),
            Style('activemark', 'default', 'red', nowrap=True),
            Style('nonactivemark', 'default', 'Blue', nowrap=True),
        ])
}

framelist_keys = {
    left: 'framelist.prev',
    right: 'framelist.next',
    '\r': 'framelist.close',
    '\n': 'framelist.close',
}

class FrameListCommands(Commands):
    def _itermarks(self, wnd):
        ret = []
        names = dict(('childframe_{}'.format(id(frame)), frame)
                     for frame in kaa.app.get_frames())
        for name, pos in wnd.document.marks.items():
            if name in names:
                ret.append((names[name], pos))
        ret = sorted(ret, key=lambda e:e[1])
        return [f for f, pos in ret]

    def _get_frames(self):
        return []

    # todo: refactor
    @command('framelist.prev')
    def prev(self, wnd):
        cur = kaa.app.get_activeframe()
        frames = self._itermarks(wnd)
        for n, frame in enumerate(frames):
            if cur is frame:
                if n:
                    frames[n-1].bring_top()
                    wnd.get_label('popup').bring_top()
                    wnd.document.mode._update_style(wnd)
                    return

    @command('framelist.next')
    def next(self, wnd):
        cur = kaa.app.get_activeframe()
        frames = self._itermarks(wnd)

        for n, frame in enumerate(frames):
            if cur is frame:
                if n < len(frames)-1:
                    frames[n+1].bring_top()
                    wnd.get_label('popup').bring_top()
                    wnd.document.mode._update_style(wnd)
                    return

    @command('framelist.close')
    def close(self, wnd):
        # Destroy popup window
        popup = wnd.get_label('popup')
        if popup:
            popup.destroy()

class FrameListMode(dialogmode.DialogMode):
    autoshrink = True
    USE_UNDO = False

    @classmethod
    def build(cls):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)

        f = dialogmode.FormBuilder(doc)
        for frame in kaa.app.get_frames():
            start = f.document.endpos()
            markname = '_{}'.format(id(frame))
            f.append_text('default', frame.get_title().replace('&', '&&'))

            f.document.marks['childframe'+markname] = (start, f.document.endpos())

            f.append_text('default', ' ')

        mode._update_style(None)
        return doc

    def _update_style(self, wnd):
        activeframe = kaa.app.get_activeframe()
        cursorpos = None
        for frame in kaa.app.get_frames():
            markname = '_{}'.format(id(frame))

            f, t = self.document.marks['childframe'+markname]
            if activeframe is frame:
                self.document.styles.setints(f, t, self.get_styleid('activemark'))
                cursorpos = f
            else:
                self.document.styles.setints(f, t, self.get_styleid('nonactivemark'))

        if wnd and cursorpos is not None:
            wnd.cursor.setpos(cursorpos)

    def init_keybind(self):
        self.keybind.add_keybind(framelist_keys)

    def init_commands(self):
        super().init_commands()

        self.framelist_commands = FrameListCommands()
        self.register_command(self.framelist_commands)

    def init_themes(self):
        super().init_themes()
        self.themes.append(FrameListThemes)

    def get_cursor_visibility(self):
        return 0   # hide cursor

    def on_esc_pressed(self, wnd, event):
        self.framelist_commands.close(wnd)

    def on_str(self, wnd, s):
        pass
