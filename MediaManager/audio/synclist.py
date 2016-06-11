import curses

from MediaManager.util.numbers import humanize

class SyncList(dict):
    def __init__(self, filepath):
        self.__filepath = filepath

    def load(self):
        try:
            for line in open(self.__filepath, 'rt'):
                line = line.split('#', 1)[0]
                line = line.rstrip()
                if not line:
                    continue

                cmd, title = line.split(' ', 1)
                self[title] = cmd
        except IOError:
            pass
        return self

    def save(self):
        with open(self.__filepath, 'wt') as file:
            for name in sorted(self):
                line = '%s %s\n' % (self[name], name)
                file.write(line)


class SyncSelect(object):
    def __init__(self, from_lib, to_lib, sync_list):
        self.__sync_list = sync_list
        self.__src = from_lib
        self.__dst = to_lib
        self.__dst_size = to_lib.available_space

    def show_selection_window(self):

        # Ratify actions
        for name, action in [(n, a) for n, a in self.__sync_list.items()]:
            if action == '+':
                if not self.__src.has_album(name):
                    continue
                if self.__dst.has_album(name):
                    del self.__sync_list[name]
            elif action == '-':
                if not self.__dst.has_album(name):
                    del self.__sync_list[name]
            else:
                continue

        def get_color(name):
            if self.__dst.has_album(name):
                if name in self.__sync_list:
                    if self.__sync_list[name] == '-':
                        return 22
                return 4
            if self.__src.has_album(name):
                if name in self.__sync_list:
                    if self.__sync_list[name] == '+':
                        return 21
                return 1
            return 3

        src_names = [a.name for a in self.__src]
        dst_names = [a.name for a in self.__dst]
        action_names = [n for n in self.__sync_list]

        names = set(src_names)
        names.update(dst_names)
        names.update(action_names)

        items = []
        for name in sorted(names):
            items.append((get_color(name), name))
        items.sort(key=lambda a: a[1])

        try:
            w = None

            color_map = {
            }

            pair_map = {
                1: (curses.COLOR_WHITE, curses.COLOR_BLACK),
                2: (curses.COLOR_BLUE, curses.COLOR_WHITE),
                3: (curses.COLOR_RED, curses.COLOR_BLACK),
                4: (curses.COLOR_CYAN, curses.COLOR_BLACK),
                #10: (curses.COLOR_BLACK, curses.COLOR_WHITE),
                #11: (curses.COLOR_GREEN, curses.COLOR_WHITE),
                #12: (curses.COLOR_BLUE, curses.COLOR_WHITE),
                21: (curses.COLOR_BLACK, curses.COLOR_GREEN),
                22: (curses.COLOR_BLACK, curses.COLOR_RED),
            }

            w = Window(color_map, pair_map)
            max_y, max_x = w.getmaxyx()

            w.refresh()
            title = TextBox((0, 0), max_x, ' * Album Selection *  (ESC to accept, ^C to exit) ', 2, 2)
            t = ToggleList((2, 0, max_y - 2, max_x), items, 1)
            match = TextBox((0, 50), 25, '<match>', 2, 11)
            dst = TextBox((1, 0), max_x, ' Sync to: %s' % self.__dst.base_dir, 2, 2)
            space = TextBox((max_y - 1, 0), 80, '', 2, 2)

            w.refresh()

            def set_space():
                used = 0
                for album in self.__dst:
                    used += album.total_size

                add = 0
                remove = 0
                for name, cmd in self.__sync_list.items():
                    if cmd == '+':
                        if self.__src.has_album(name):
                            add += self.__src.get_album(name).total_size
                    elif cmd == '-':
                        remove += self.__dst.get_album(name).total_size

                avail = humanize(self.__dst_size)
                final = humanize(used + add - remove)
                write = humanize(add)
                str = " Free: %s   Final: %s   Write: %s" % (avail, final, write)
                space.set_value(str)


            def state_toggle(line):
                name = items[line][1]

                if self.__dst.has_album(name):
                    if name in self.__sync_list:
                        del self.__sync_list[name]
                        self.__dst_size += self.__dst.get_album(name).total_size
                    else:
                        self.__sync_list[name] = '-'
                        self.__dst_size -= self.__dst.get_album(name).total_size
                elif self.__src.has_album(name):
                    if name in self.__sync_list:
                        del self.__sync_list[name]
                        self.__dst_size -= self.__src.get_album(name).total_size
                    else:
                        self.__sync_list[name] = '+'
                        self.__dst_size += self.__src.get_album(name).total_size
                else:
                    pass
                set_space()
                t.set_color(line, get_color(name))


            def getch():
                char = w.getch()
                with open('log', 'at') as fh:
                    fh.write('%s\n' % repr(char))
                if char == curses.KEY_PPAGE:   t.key_pgup()
                elif char == curses.KEY_NPAGE: t.key_pgdn()
                elif char == curses.KEY_LEFT:  t.key_pgup()
                elif char == curses.KEY_RIGHT: t.key_pgdn()
                elif char == curses.KEY_UP:    t.key_up()
                elif char == curses.KEY_DOWN:  t.key_dn()
                elif char == ord(' '):
                    state_toggle(t.current_line)
                elif char == ord('s'):
                    state_toggle(t.current_line)
                    t.key_dn()
                else:
                    #raise Exception(repr(char))
                    return char

            set_space()
            while True:
                try:
                    ch = getch()
                except KeyboardInterrupt:
                    return False
                if ch == 27:
                    return True
                if ch is not None:
                    match.putch(ch)

        finally:
            if w:
                w.close()

        return False


class ToggleList(object):
    __pad = None

    def __init__(self, xxx_todo_changeme, items, color=None):
        (t, l, b, r) = xxx_todo_changeme
        self.__tlbr = (t, l, b, r)
        self.__items = items
        page_size = b - t + 1

        width = 0
        for item in items:
            width = max(width, len(item))
        width += 8
        width = max(width, r - l)

        self.__pager = LinePager(len(items), page_size)

        self.__pad = Pad((len(items), width), self.__tlbr, color)

        for y, (color, string) in enumerate(self.__items):
            self.__draw_line(y, string, color)

        #self.__refresh()
        self.__set_select()

    def __refresh(self):
        self.__pad.refresh((self.__pager.page_top, 0))

    def __draw_line(self, y, string, color):
        self.__pad.addstr((y, 1), "%d %s" % (y, string), color)

    def key_up(self):
        self.__clear_select()
        self.__pager.move_cursor(-1)
        self.__set_select()

    def key_dn(self):
        self.__clear_select()
        self.__pager.move_cursor(1)
        self.__set_select()

    def key_pgup(self):
        self.__clear_select()
        self.__pager.move_page(-1)
        self.__set_select()

    def key_pgdn(self):
        self.__clear_select()
        self.__pager.move_page(1)
        self.__set_select()

    def set_color(self, y, color):
        self.__draw_line(y, self.__items[y][1], color)
        self.__refresh()

    @property
    def current_line(self):
        return self.__pager.cursor_line

    def __clear_select(self):
        self.__pad.addstr((self.__pager.cursor_line, 0), ' ')

    def __set_select(self):
        self.__pad.addstr((self.__pager.cursor_line, 0), '*')
        self.__refresh()


class TextBox(object):
    def __init__(self, xxx_todo_changeme1, w, default_string=None, color=None, default_color=None):
        (t, l) = xxx_todo_changeme1
        self.__width = w
        self.__default_string = default_string
        self.__color = color
        self.__default_color = default_color
        assert self.__width > 0
        assert t >= 0
        assert l >= 0
        self.__pad = Pad((1, self.__width), (t, l, t+1, l+self.__width), default_color)
        self.__buffer = ''
        self.__draw()
        self.__refresh()

    def __draw(self):
        if not self.__buffer:
            string = self.__default_string
            color = self.__default_color
        else:
            string = self.__buffer
            color = self.__color
            string += ' ' * max(0, (self.__width - len(string) - 1))
        self.__pad.addstr((0, 0), string, color)

    def __refresh(self):
        self.__pad.refresh((0, 0))

    def putch(self, ch):
        #raise Exception(type(ch))
        if ch == 127: #curses.KEY_BACKSPACE:
            self.__buffer = self.__buffer[:len(self.__buffer)-1]
        elif ch >= ord('A') and ch <= ord('z') or ch == ord(' '):
            if len(self.__buffer) == self.__width - 1:
                return
            self.__buffer += chr(ch)
        else:
            return
        self.__draw()
        self.__refresh()

    def value(self):
        return self.__buffer

    def set_value(self, string):
        self.__buffer = string
        self.__draw()
        self.__refresh()


class LinePager(object):
    def __init__(self, size, page_size):
        self.__size = size
        self.__page_size = page_size
        self.__page_top = 0
        self.__cursor_line = 0

    def move_cursor(self, distance):
        self.__move_cursor_line(distance)
        self.__page_track_cursor()

    def move_page(self, pages):
        distance = pages*self.__page_size
        self.__move_page_top(distance)
        self.__move_cursor_line(distance)

    def __move_cursor_line(self, distance):
        self.__cursor_line = min(max(0, self.__cursor_line + distance), self.__size-1)

    def __move_page_top(self, distance):
        self.__page_top = min(max(0, self.__page_top + distance), self.__size-self.__page_size)

    def __page_track_cursor(self):
        if self.__cursor_line < self.__page_top:
            self.__move_page_top(-(self.__page_top - self.__cursor_line))
        elif self.__cursor_line >= self.__page_top + self.__page_size:
            self.__move_page_top(self.__cursor_line - self.__page_top - self.__page_size + 1)

    @property
    def page_top(self):
        return self.__page_top

    @property
    def cursor_line(self):
        return self.__cursor_line


class Window(object):
    __stdscr = None

    def __init__(self, color_map, pair_map):
        self.__stdscr = curses.initscr()
        self.__stdscr.keypad(1)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()

        for number, (r, b, g) in color_map.items():
            curses.init_color(number, r, b, g)

        for number, (fg, bg) in pair_map.items():
            curses.init_pair(number, fg, bg)

    def getmaxyx(self):
        return self.__stdscr.getmaxyx()

    def close(self):
        if not self.__stdscr:
            return
        self.__stdscr.keypad(0)

        curses.nocbreak()
        curses.echo()
        curses.endwin()
        self.__stdscr = None

    def getch(self):
        return self.__stdscr.getch()

    def addstr(self, xxx_todo_changeme2, string, color):
        (y, x) = xxx_todo_changeme2
        meta = curses.color_pair(color)
        self.__stdscr.addstr(y, x, string, meta)

    def refresh(self):
        self.__stdscr.refresh()


class Pad(object):
    __tlbr = None
    __pad = None

    def __init__(self, xxx_todo_changeme3, xxx_todo_changeme4, color=None):
        (h, w) = xxx_todo_changeme3
        (t, l, b, r) = xxx_todo_changeme4
        self.__h, self.__w = (h, w)
        self.__tlbr = (t, l, b, r)
        self.__pad = curses.newpad(h, w)
        #self.__w.close()
        #print dir(self.__pad)
        if color:
            self.__pad.bkgd(curses.color_pair(color))


    def close(self):
        if self.__pad:
            self.__pad.clear()
            self.__pad.erase()

        self.__pad = None

    def refresh(self, xxx_todo_changeme5):
        (y, x) = xxx_todo_changeme5
        self.__pad.refresh(y, x, *self.__tlbr)

    def addstr(self, xxx_todo_changeme6, string, color=None):
        (y, x) = xxx_todo_changeme6
        string = string.encode('ascii','ignore')
        try:
            if color:
                meta = curses.color_pair(color)
                self.__pad.addstr(y, x, string, meta)
            else:
                self.__pad.addstr(y, x, string)
        except curses.error as e:
            if y >= self.__h:
                raise curses.error('%s: %s' % (e.message, 'Y bounds exceeded'))
            if x + len(string) >= self.__w:
                raise curses.error('%s: %s' % (e.message, 'X bounds exceeded'))
