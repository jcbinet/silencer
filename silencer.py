#!/usr/bin/env python3
from pynput import keyboard
import os
import signal
import gi
import json
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
    def __init__(self, config):
        # Mic key bind init
        self.config = config
        self.mic_key = config['keybind']
        self.mic_sound_card = config['sound_card_id']
        self.mic_muted = True
        self.mic_hold_to_talk = config['hold_to_talk']
        self.mic_keybind_setup_dialog = None
        self.mic_keybind_setup_active = False
        self.mic_keybind_setup_key = None
        self.mic_keybind_setup_dialog_key_label = None

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
        about_item = Gtk.MenuItem('Silencer v0.3.3  💀')
        menu.append(about_item)

        # Hold to talk toggle
        ppt_toggle_item = Gtk.CheckMenuItem('Hold to talk')
        ppt_toggle_item.set_active(self.mic_hold_to_talk)
        ppt_toggle_item.connect('toggled', self.hold_to_talk_mode_toggled)
        menu.append(ppt_toggle_item)

        # Keybind setup item
        keybind_setup_item = Gtk.MenuItem('Keybind setup')
        keybind_setup_item.connect('activate', self.open_set_up_keybind_dialog)
        menu.append(keybind_setup_item)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())

        # Quit
        item_quit = Gtk.MenuItem('Quit Silencer')
        item_quit.connect('activate', self.stop_processes)
        menu.append(item_quit)

        menu.show_all()
        return menu

    # When keybind setup dialog received a response
    def mic_keybind_dialog_setup_response(self, dialog, response):
        if response is 1:
            self.mic_key = self.mic_keybind_setup_key
        self.mic_keybind_setup_active = False
        dialog.destroy()

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
        # Save config
        self.save_config()

        # Reset cap of mic
        self.set_mic_capture(True)

        for process in self.threads:
            process.stop()

    # When a keyboard key is pressed
    def on_press(self, key):
        if self.mic_keybind_setup_active:
            self.mic_keybind_setup_key = str(key)
            self.mic_keybind_setup_dialog_key_label.set_label(self.mic_keybind_setup_key)

        elif self.mic_key in str(key):
            if self.mic_hold_to_talk is True:
                self.unmute_mic()
            elif self.mic_hold_to_talk is False:
                if self.mic_muted is True:
                    self.unmute_mic()
                elif self.mic_muted is False:
                    self.mute_mic()

    # When a keyboard key is released
    def on_release(self, key):
        if self.mic_key in str(key) and self.mic_hold_to_talk is True:
            self.mute_mic()

    # Mute the microphone
    def mute_mic(self):
        if self.mic_muted is False:
            self.mic_muted = True
            self.set_mic_capture(False)
            self.indicator.set_icon(self.muted_icon_path)

    # Unmute the microphone
    def unmute_mic(self):
        if self.mic_muted is True:
            self.mic_muted = False
            self.set_mic_capture(True)
            self.indicator.set_icon(self.not_muted_icon_path)

    # Set mic capture manually
    def set_mic_capture(self, on):
        os.system('amixer -c {0} set Mic {1}'.format(self.mic_sound_card, 'cap' if on is True else 'nocap'))

    # Toggle hold to talk mode
    def hold_to_talk_mode_toggled(self, *source):
        self.mic_hold_to_talk = not self.mic_hold_to_talk

    # Open keybind setup dialog
    def open_set_up_keybind_dialog(self, *source):
        self.mic_keybind_setup_active = True

        self.mic_keybind_setup_dialog = Gtk.Dialog('Keybind setup')
        self.mic_keybind_setup_dialog.set_default_size(300, 100)
        self.mic_keybind_setup_dialog.vbox.pack_start(Gtk.Label('Press desired key for mic keybind:'), False, False, 0)
        self.mic_keybind_setup_dialog_key_label = Gtk.Label()
        self.mic_keybind_setup_dialog.vbox.pack_start(self.mic_keybind_setup_dialog_key_label, False, False, 16)
        self.mic_keybind_setup_dialog.add_button('Confirm', 1)
        self.mic_keybind_setup_dialog.connect('response', self.mic_keybind_dialog_setup_response)

        self.mic_keybind_setup_dialog.show_all()

    # Save config to json file
    def save_config(self):
        self.config['hold_to_talk'] = self.mic_hold_to_talk
        self.config['keybind'] = self.mic_key

        json.dump(self.config, open('silencer-config.json', 'w'), indent=2)


# Start
Silencer(json.load(open('silencer-config.json')))
