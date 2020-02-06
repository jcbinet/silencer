#!/usr/bin/env python3
from pynput import keyboard
import os
import signal
import gi
import argparse
from threading import Thread

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

dir_path = os.path.dirname(os.path.realpath(__file__))


# Custom wrapper for gtk thread
class GtkThread(Thread):
    def __init__(self, target, stop_target):
        super(GtkThread, self).__init__(target=target)
        self.stop_target = stop_target

    def stop(self):
        self.stop_target()


class Silencer:
    def __init__(self, mic_key, mic_sound_card):
        # Indicator init
        self.app = 'Silencer'
        self.muted_icon_path = dir_path + '/icons/indicator-low.png'
        self.not_muted_icon_path = dir_path + '/icons/indicator-full.png'

        self.indicator = AppIndicator3.Indicator.new(
            self.app,
            self.muted_icon_path,
            AppIndicator3.IndicatorCategory.OTHER
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())

        # Mic key bind init
        self.mic_key = mic_key
        self.mic_sound_card = mic_sound_card
        self.mic_muted = True

        # Threads
        self.threads = []

        # Make sure mic is in nocap mode
        self.set_mic_capture(False)

        # Start silencer
        self.start_processes()

    # Create menu for app indicator
    def create_menu(self):
        menu = Gtk.Menu()
        # About
        about_item = Gtk.MenuItem('Silencer v0.1.0  💀')
        menu.append(about_item)
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        # Quit
        item_quit = Gtk.MenuItem('Quit Silencer')
        item_quit.connect('activate', self.stop_processes)
        menu.append(item_quit)

        menu.show_all()
        return menu

    # Start all processes using threads
    def start_processes(self):
        # To be able to exit with ^C
        signal.signal(signal.SIGINT, self.stop_processes)

        # Key bind listener process
        process = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        process.start()
        self.threads.append(process)

        # App indicator process
        process = GtkThread(target=Gtk.main, stop_target=Gtk.main_quit)
        process.start()
        self.threads.append(process)

        for process in self.threads:
            process.join()

    # Stop all threads
    def stop_processes(self, *source):
        # Reset cap of mic
        self.set_mic_capture(True)

        for process in self.threads:
            process.stop()

    # When a keyboard key is pressed
    def on_press(self, key):
        if self.mic_key in str(key) and self.mic_muted is True:
            self.mic_muted = False
            self.toggle_mic()
            self.indicator.set_icon(dir_path + '/icons/indicator-full.png')

    # When a keyboard key is released
    def on_release(self, key):
        if self.mic_key in str(key) and self.mic_muted is False:
            self.mic_muted = True
            self.toggle_mic()
            self.indicator.set_icon(dir_path + '/icons/indicator-low.png')

    # Toggle mic capture
    def toggle_mic(self):
        os.system('amixer -c {0} set Mic toggle'.format(self.mic_sound_card))

    # Set mic capture manually
    def set_mic_capture(self, on):
        os.system('amixer -c {0} set Mic {1}'.format(self.mic_sound_card, 'cap' if on is True else 'nocap'))


# Parse arguments
parser = argparse.ArgumentParser(description='Silencer')
parser.add_argument('-k', default='f8', help='Toggle key')
parser.add_argument('-c', default=1, help='Sound card id')

args = parser.parse_args()

# Start
Silencer(args.k, args.c)
