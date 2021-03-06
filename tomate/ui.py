# -*- coding: utf-8 -*-

# Copyright 2012 Jerry Peng
#
# Tomate is a time management tool inspired by the
# pomodoro technique(http://www.pomodorotechnique.com/).
#
# Tomate is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option
# any later version.
#
# Tomate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with Foobar. If not, see http://www.gnu.org/licenses/.


import pygtk
pygtk.require('2.0')
import gtk
import gobject
import logging
import webbrowser

from tomate import __version__
from tomate import timequotes
from tomate import util

from tomate.activity import TodoView, PlanView
from tomate.history import HistoryView

icontheme = gtk.icon_theme_get_default()

MENU_ICON_SIZE = 32

PAGES = [
        (_('ToDo'),        'TodoView',          'stock_task'),
        (_('Plan'),        'PlanView',          'stock_notes'),
        (_('History'),     'HistoryView',       'stock_calendar'),
    ]


class MainWindow(gtk.Window):
    """Activity Window Class"""
    def __init__(self):
        super(MainWindow, self).__init__()
        self.notebook = self._create_notebook()
        self.menu_view = self._create_menuview()
        self.menu_view.set_size_request(120, -1)
        self.menu_model = self.menu_view.get_model()
        self._setup_pages()

        left_pane = gtk.Viewport()
        left_pane.add(self.menu_view)

        mainpane = gtk.HPaned()
        mainpane.pack1(left_pane, shrink=False)
        mainpane.pack2(self.notebook, shrink=False)

        quote, author = timequotes.random_quote()
        quotelabel = gtk.Label(shorten_quote(quote))
        spacing = ' ' * 50
        quotelabel.set_tooltip_markup('%s\n%s<i><s>    </s> %s</i>' % (quote, spacing, author))

        option_btn = util.new_small_button(
                'gtk-preferences',
                self._on_options,
                tooltip=_('Preferences'))

        about_btn = util.new_small_button(
                'dialog-info',
                self._on_about,
                tooltip=_('About Tomate'))

        bottombox = gtk.HBox(False, 0)
        bottombox.pack_start(quotelabel, False, False)
        bottombox.pack_end(about_btn, False, False)
        #bottombox.pack_end(option_btn, False, False)

        mainbox = gtk.VBox(False, 5)
        mainbox.pack_start(mainpane, True, True)
        mainbox.pack_end(bottombox, False, False)
        self.add(mainbox)

        self.set_title('Tomate')
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_name('tomate')
        self.set_border_width(5)
        self.set_geometry_hints(mainbox, min_width=750, min_height=515)

        self.connect('destroy', self._on_close)

    def _create_notebook(self):
        notebook = gtk.Notebook()
        notebook.set_show_tabs(False)
        return notebook

    def _create_menuview(self):
        def _icon_render_func(col, renderer, model, iter, user_data=None):
            icon = model.get_value(iter, 0)
            if icon:
                renderer.set_property('pixbuf', icon)
            else:
                renderer.set_property('stock-id', gtk.STOCK_EDIT)
                renderer.set_property('stock-size', MENU_ICON_SIZE)

        menu_model = gtk.ListStore(gtk.gdk.Pixbuf, str, int)
        menu_view = gtk.TreeView()
        menu_view.set_model(menu_model)
        menu_view.set_headers_visible(False)
        icon_renderer = gtk.CellRendererPixbuf()
        icon_col = gtk.TreeViewColumn('Icon', icon_renderer)
        icon_col.set_cell_data_func(icon_renderer, _icon_render_func)
        text_col = gtk.TreeViewColumn('Text', gtk.CellRendererText(), text=1)
        menu_view.append_column(icon_col)
        menu_view.append_column(text_col)
        menu_view.get_selection().set_mode(gtk.SELECTION_SINGLE)
        return menu_view

    def _setup_pages(self):
        g = globals()
        for idx, (name, viewcls, iconname) in enumerate(PAGES):
            view = g[viewcls](self)
            label = gtk.Label(name)
            try:
                icon = icontheme.load_icon(iconname, MENU_ICON_SIZE, 0)
            except:
                icon = None
                logging.error('icon %s not found in current theme' % iconname)
            self.notebook.append_page(view, label)
            self.menu_model.append((icon, name, idx))
        self.notebook.set_current_page(0)
        self.menu_view.get_selection().connect('changed', self._on_select_change)

    def _on_close(self, widget, data=None):
        gtk.main_quit()

    def _on_options(self, widget):
        pass

    def _on_about(self, widget):
        about_dlg = TomateAboutDialog()
        about_dlg.run()
        about_dlg.destroy()

    def _on_select_change(self, widget):
        (model, it) = self.menu_view.get_selection().get_selected()
        if model and it:
            pgnum = model.get_value(it, 2)
            self.notebook.set_current_page(pgnum)
            view = self.notebook.get_nth_page(pgnum)
            if hasattr(view, 'refresh'):
                view.refresh()


AUTHORS = (_('Jerry Peng<pr2jerry@gmail.com>'),)
COMMENT = _('Tomate is a time management tool inspired by the pomodoro technique')

class TomateAboutDialog(gtk.AboutDialog):
    """docstring for TomateAboutDialog"""
    def __init__(self):
        super(TomateAboutDialog, self).__init__()
        self.set_name(_('Tomate'))
        self.set_program_name(_('Tomate'))
        self.set_logo_icon_name('tomate')
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_comments(COMMENT)
        self.set_version(__version__)
        self.set_copyright('\xc2\xA9Copyright 2012, Jerry Peng')
        self.set_website('https://github.com/moonranger/tomate')
        self.set_website_label(_('Homepage on github'))
        self.set_authors(AUTHORS)


QUOTE_MAX_CHARS = 80

def shorten_quote(quote):
    if len(quote) <= QUOTE_MAX_CHARS:
        return quote
    substr = quote[:QUOTE_MAX_CHARS]
    p = substr.rfind(' ')
    if p:
        substr = substr[:p]
    return substr + '...'


main_window = MainWindow()

def start_app():
    main_window.show_all()
    gtk.main()

if __name__ == '__main__':
    start_app()
