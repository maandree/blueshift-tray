#!/usr/bin/env python2
# -*- coding: utf-8 -*-

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
import time
import signal
import subprocess

import pygtk
import gettext

pygtk.require("2.0")
import gtk, glib


LOCALEDIR = '/usr/share/locale'
gettext.bindtextdomain('blueshift', LOCALEDIR)
gettext.textdomain('blueshift')


def process_quit(signum, frame):
    '''
    Invoked when a child process exists
    
    @param  signum:int   The signal (SIGCHLD)
    @param  frame:=None  Will probably be `None`
    '''
    global running
    process.wait()
    if running:
        running = False
        icon.set_visible(False)
        gtk.main_quit()
    time.sleep(0.1)
    sys.exit(0)


def term(count = 1, kill = False):
    '''
    Terminate the blueshift if alive
    
    @param  count:int  Number of times to send SIGTERM
    @param  kill:bool  Whether to also send SIGKILL and the exit
    '''
    if process is not None:
        process.send_signal(signal.SIGTERM)
        if count > 1:
            for i in range(count - 1):
                if process.poll() is None:
                    time.sleep(0.1)
                    process.send_signal(signal.SIGTERM)
    if kill:
        time.sleep(0.1)
        process.send_signal(signal.SIGKILL)
        sys.exit(0)


def create_menu(menu, image, title, function):
    '''
    Create a menu item
    
    @param  menu:gtk.Menu                       The menu to place the item inside
    @param  image:str?                          The icon on the menu item
    @param  title:str?                          The text on the menu item
    @param  function:(gtk.Widget, (=None))→void  The function invoked when the item is pressed
    '''
    if image is None:
        menu_item = gtk.MenuItem(gettext.gettext(title))
    else:
        menu_item = gtk.ImageMenuItem(image)
        if title is not None:
            menu_item.set_label(gettext.gettext(title))
    menu_item.connect('activate', function)
    menu.append(menu_item)


def f_popup(widget, button, time, data = None):
    '''
    Invoked to open a popup menu
    '''
    menu.show_all()
    menu.popup(None, None, gtk.status_icon_position_menu, button, time, icon)


def f_toggle(widget, data = None):
    global paused, last_time
    now = time.time()
    if now < last_time + 0.2:
        return
    last_time = now
    if paused is None:
        paused = False
    process.send_signal(signal.SIGUSR2)
    icon.set_from_icon_name('blueshift-on' if paused else 'blueshift-off')
    paused = not paused

def f_reload(widget, data = None):
    process.send_signal(signal.SIGUSR1)

def f_quit(widget, data = None):
    global running
    if running:
        running = False
        icon.set_visible(False)
        gtk.main_quit()
        if paused is None:
            term()
        elif paused:
            term(2, True)
        else:
            term(2, True)

def f_panic_quit(widget, data = None):
    global running
    if running:
        running = False
        icon.set_visible(False)
        gtk.main_quit()
        term(2, True)


signal.signal(signal.SIGCHLD, process_quit)

process = subprocess.Popen(['blueshift'] + sys.argv[1:])
running = True
paused = None
last_time = time.time() - 1


try:
    icon = gtk.StatusIcon()
    icon.set_from_icon_name('blueshift-on')
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
    running = False
    icon.set_visible(False)
    term()
    if paused is not None:
        time.sleep(0.1)
        term()

finally:
    try:
        process.wait()
    except KeyboardInterrupt:
        term()

if process.poll() is None:
    process.send_signal(signal.KILL)

