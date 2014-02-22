#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

# blueshift-tray – Systray wrapper for Blueshift
# Copyright © 2014  Mattias Andrée (maandree@member.fsf.org)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import signal
import subprocess

import pygtk
import gettext

pygtk.require("2.0")
import gtk, glib


LOCALEDIR = '/usr/share/locale'
gettext.bindtextdomain('blueshift', LOCALEDIR)
gettext.textdomain('blueshift')


process = subprocess.Popen(['blueshift'] + sys.argv[1:])


def create_menu(menu, image, title, function):
    if image is None:
        menu_item = gtk.MenuItem(gettext.gettext(title))
    else:
        menu_item = gtk.ImageMenuItem(image)
        if title is not None:
            menu_item.set_label(gettext.gettext(title))
    menu_item.connect('activate', function)
    menu.append(menu_item)


def f_toggle(widget, data = None):
    process.send_signal(signal.SIGUSR2)
    if icon.get_icon_name() == 'redshift-status-on':
        icon.set_from_icon_name('redshift-status-off')
    else:
        icon.set_from_icon_name('redshift-status-on')

def f_reload(widget, data = None):
    process.send_signal(signal.SIGUSR1)

def f_quit(widget, data = None):
    icon.set_visible(False)
    gtk.main_quit()
    process.send_signal(signal.SIGTERM)

def f_panic_quit(widget, data = None):
    icon.set_visible(False)
    gtk.main_quit()
    process.send_signal(signal.SIGTERM)
    import time
    time.sleep(0.01)
    process.send_signal(signal.SIGTERM)


def f_popup(widget, button, time, data = None):
    menu.show_all()
    menu.popup(None, None, gtk.status_icon_position_menu, button, time, icon)


try:
    icon = gtk.StatusIcon()
    icon.set_from_icon_name('redshift-status-on')
    icon.set_tooltip('Blueshift')
    
    menu = gtk.Menu()
    create_menu(menu, None, '_Toggle', f_toggle)
    create_menu(menu, gtk.STOCK_REFRESH, '_Reload', f_reload)
    create_menu(menu, None, None, f_reload)
    create_menu(menu, gtk.STOCK_QUIT, '_Quit', f_quit)
    create_menu(menu, gtk.STOCK_QUIT, '_Panic Quit', f_panic_quit)
    
    icon.connect('activate', f_toggle)
    icon.connect('popup-menu', f_popup)
    
    icon.set_visible(True)
    gtk.main()

except KeyboardInterrupt:
    icon.set_visible(False)
    process.send_signal(signal.SIGTERM)

finally:
    try:
        process.wait()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGTERM)

