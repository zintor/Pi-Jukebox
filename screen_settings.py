# This file is part of pi-jukebox.
#
# pi-jukebox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pi-jukebox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pi-jukebox. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2015- by Mark Zwart, <mark.zwart@pobox.com>
"""
=======================================
**screen_settings.py**: Settings screen
=======================================
"""
__author__ = 'Mark Zwart'

import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
import socket
from gui_widgets import *
from mpd_client import *
from settings import *
from screen_wifi import *
from config_file import *
from screen_keyboard import *


class ScreenSettings(ScreenModal):
    """ Screen for settings or quitting/shutting down

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen):
        ScreenModal.__init__(self, screen, "Settings")
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        label = "Quit Pi-Jukebox"
        self.add_component(ButtonText('btn_quit', self.surface, button_left, 30, button_width, 32, label))
        label = "Playback options"
        self.add_component(ButtonText('btn_playback', self.surface, button_left, 72, button_width, 32, label))
        label = "MPD related settings"
        self.add_component(ButtonText('btn_mpd', self.surface, button_left, 114, button_width, 32, label))
        label = "System info"
        self.add_component(ButtonText('btn_system_info', self.surface, button_left, 156, button_width, 32, label))
        label = "Back"
        self.add_component(ButtonText('btn_return', self.surface, button_left, 198, button_width, 32, label))

    def on_click(self, x, y):
        tag_name = super(ScreenSettings, self).on_click(x, y)
        if tag_name == 'btn_playback':
            screen_playback_options = ScreenSettingsPlayback(self)
            screen_playback_options.show()
            self.show()
        elif tag_name == 'btn_quit':
            screen_quit = ScreenSettingsQuit(self)
            screen_quit.show()
            self.show()
        elif tag_name == 'btn_mpd':
            screen_mpd = ScreenSettingsMPD(self)
            screen_mpd.show()
            self.show()
        elif tag_name == 'btn_system_info':
            screen_system_info = ScreenSystemInfo(self)
            screen_system_info.show()
            self.show()
        elif tag_name == 'btn_return':
            self.close()


class ScreenSettingsQuit(ScreenModal):
    """ Screen for quitting pi-jukebox.

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen):
        ScreenModal.__init__(self, screen, "Quit")
        self.window_x = 70
        self.window_y = 25
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        button_left = self.window_x + 10
        button_width = self.window_width - 20
        self.outline_shown = True
        self.add_component(
            ButtonText('btn_quit', self.surface, button_left, self.window_y + 30, button_width, 32, "Quit"))
        self.add_component(
            ButtonText('btn_shutdown', self.surface, button_left, self.window_y + 70, button_width, 32, "Shutdown Pi"))
        self.add_component(
            ButtonText('btn_reboot', self.surface, button_left, self.window_y + 110, button_width, 32, "Reboot Pi"))
        self.add_component(
            ButtonText('btn_cancel', self.surface, button_left, self.window_y + 150, button_width, 32, "Cancel"))

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_quit':
            mpd.disconnect()
            print ("Thanks for using pi-jukebox!\nBye!")
            sys.exit()
        elif tag_name == 'btn_shutdown':
            if RUN_ON_RASPBERRY_PI:
                pygame.display.quit()
                os.system("sudo shutdown -h now")
            else:
                sys.exit()
        elif tag_name == 'btn_reboot':
            if RUN_ON_RASPBERRY_PI:
                pygame.display.quit()
                os.system("sudo shutdown -r now")
            else:
                sys.exit()
        elif tag_name == 'btn_cancel':
            self.close()


class ScreenSettingsPlayback(ScreenModal):
    """ Screen for settings playback options

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen):
        ScreenModal.__init__(self, screen, "Playback settings")
        self.add_component(LabelText('lbl_shuffle', self.surface, 10, 30, 40, 20, "Shuffle"))
        self.add_component(Switch('switch_shuffle', self.surface, 60, 23))
        self.add_component(LabelText('lbl_repeat', self.surface, 120, 30, 40, 20, "Repeat"))
        self.add_component(Switch('switch_repeat', self.surface, 170, 23))
        self.add_component(LabelText('lbl_single', self.surface, 230, 30, 40, 20, "Single"))
        self.add_component(Switch('switch_single', self.surface, 280, 23))
        self.add_component(LabelText('lbl_consume', self.surface, 10, 65, 110, 20, "Consume playlist"))
        self.add_component(Switch('switch_consume', self.surface, 125, 58))
        self.add_component(
            ButtonText('btn_rescan', self.surface, 10, 108, self.window_width - 20, 32, "Re-scan library"))
        self.add_component(
            ButtonText('btn_update', self.surface, 10, 150, self.window_width - 20, 32, "Update library"))
        self.add_component(ButtonText('btn_return', self.surface, 10, 192, self.window_width - 20, 32, "Back"))
        self.__initialize()

    def __initialize(self):
        """ Sets the screen controls according to current mpd configuration.
        """
        for key, value in self.components.items():
            if key == 'switch_shuffle':
                value.set_on(mpd.random)
            elif key == 'switch_repeat':
                value.set_on(mpd.repeat)
            elif key == 'switch_single':
                value.set_on(mpd.single)
            elif key == 'switch_consume':
                value.set_on(mpd.consume)

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'switch_shuffle':
            mpd.random_switch()
        elif tag_name == 'switch_repeat':
            mpd.repeat_switch()
        elif tag_name == 'switch_single':
            mpd.single_switch()
        elif tag_name == 'switch_consume':
            mpd.consume_switch()
        elif tag_name == 'btn_rescan':
            mpd.library_rescan()
        elif tag_name == 'btn_update':
            mpd.library_update()
        elif tag_name == 'btn_return':
            self.close()


class ScreenSettingsMPD(ScreenModal):
    """ Screen for settings playback options

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """
    def __init__(self, screen_rect):
        self.host_new = config_file.setting_get('MPD Settings', 'host')
        self.port_new = config_file.setting_get('MPD Settings', 'port')
        self.dir_new = config_file.setting_get('MPD Settings', 'music directory')

        ScreenModal.__init__(self, screen_rect, "MPD settings")
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        label = "Change host: " + self.host_new
        self.add_component(ButtonText('btn_host', self.surface, button_left, 30, button_width, 32, label))
        label = "Change port: " + str(self.port_new)
        self.add_component(ButtonText('btn_port', self.surface, button_left, 72, button_width, 32, label))
        self.add_component(
            ButtonText('btn_music_dir', self.surface, button_left, 114, button_width, 32, "Change music directory"))
        label = "Cancel"
        self.add_component(ButtonText('btn_cancel', self.surface, button_left, 198, button_width / 2 - 5, 32, label))
        label = "Check and save"
        self.add_component(
            ButtonText('btn_save', self.surface, button_width / 2 + 15, 198, button_width / 2 - 5, 32, label))

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        setting_label = ""
        setting_value = None
        if tag_name == 'btn_save':
            if self.save_settings():
                self.close()
                return
        elif tag_name == 'btn_cancel':
            self.close()
            return
        elif tag_name == 'btn_host':
            setting_label = "Set mpd host"
            self.host_new = self.keyboard_setting(setting_label, self.host_new)
            self.per_setting_check('host')
        elif tag_name == 'btn_port':
            setting_label = "Set mpd server port"
            self.port_new = self.keyboard_setting(setting_label, self.port_new)
            self.per_setting_check('port')
        elif tag_name == 'btn_music_dir':
            setting_label = "Set music directory"
            self.dir_new = self.keyboard_setting(setting_label, 'MPD Settings', 'music directory')
            self.per_setting_check('music directory')
        self.update()
        self.show()

    def keyboard_setting(self, caption, value=""):
        keyboard = Keyboard(self, caption)
        keyboard.text = value
        keyboard.title_color = FIFTIES_ORANGE
        new_value = keyboard.show()  # Get entered search text
        return new_value

    def update(self):
        label = "Change host: " + self.host_new
        self.components['btn_host'].draw(label)
        label = "Change port: " + str(self.port_new)
        self.components['btn_port'].draw(label)

    def per_setting_check(self, setting_type):
        if setting_type == 'host' or setting_type == 'port':
            mpd.disconnect()
            host_old = mpd.host
            port_old = mpd.port
            mpd.host = self.host_new
            mpd.port = self.port_new
            if not mpd.connect():
                error_text = "Couldn't connect to the mpd server " + mpd.host + " on port " + str(mpd.port) + "!" \
                                                                                                              "Is the MPD server running? Try the command 'sudo service mpd start' on the CLI."
                msg_show = ScreenMessage(self.surface, "Wrong host or port!", error_text, 'warning')
                msg_show.show()
                mpd.host = host_old
                mpd.port = port_old
                mpd.connect()
                return False
            else:
                mpd.host = host_old
                mpd.port = port_old
                return True
        if setting_type == 'music directory':
            if not os.path.isdir(self.dir_new):
                error_text = "The music directory you specified " + self.dir_new + " does not exist!"
                msg_show = ScreenMessage(self.surface, "Invalid directory", error_text, 'error')
                msg_show.show()
                return False
            else:
                return True

    def save_settings(self):
        if self.per_setting_check('host') and self.per_setting_check('music directory'):
            config_file.setting_set('MPD Settings', 'host', self.host_new)
            config_file.setting_set('MPD Settings', 'port', self.port_new)
            config_file.setting_set('MPD Settings', 'music directory', self.dir_new)
            mpd.host = self.host_new
            mpd.port = self.port_new
            mpd.music_directory = self.dir_new

class ScreenSystemInfo(ScreenModal):
    """ Screen for settings playback options

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "System info")
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        label = "Back"
        self.add_component(ButtonText('btn_back', self.surface, button_left, 198, button_width, 32, label))
        info = mpd.mpd_client.stats()
        self.add_component(LabelText('lbl_database', self.surface, button_left, 30, 100, 18, "Music database"))
        self.components['lbl_database'].font_color = FIFTIES_TEAL
        artist_count = "Artists: " + "{:,}".format(int(info['artists']))
        self.add_component(LabelText('lbl_artist_count', self.surface, button_left, 48, 100, 18, artist_count))
        album_count = "Albums: " + "{:,}".format(int(info['albums']))
        self.add_component(LabelText('lbl_album_count', self.surface, button_left + 100, 48, 100, 18, album_count))
        song_count = "Songs: " + "{:,}".format(int(info['songs']))
        self.add_component(LabelText('lbl_song_count', self.surface, button_left + 210, 48, 100, 18, song_count))
        play_time = "Total time: " + self.make_time_string(int(info['db_playtime']))
        self.add_component(LabelText('lbl_play_time', self.surface, button_left, 66, 300, 18, play_time))

        self.add_component(LabelText('lbl_system', self.surface, button_left, 90, 100, 18, "Server"))
        self.components['lbl_system'].font_color = FIFTIES_TEAL
        self.add_component(
            LabelText('lbl_host_name', self.surface, button_left, 108, 1500, 18, "Host name: " + socket.gethostname()))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('google.com', 0))
            ip_address = s.getsockname()[0]
            self.add_component(
                LabelText('lbl_ip_address', self.surface, button_left, 126, 1500, 18, "IP address: " + ip_address))
        except Exception:
            pass

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_back':
            self.close()
            return

    def make_time_string(self, seconds):
        days = int(seconds / 86400)
        hours = int((seconds - (days * 86400)) / 3600)
        minutes = int((seconds - (days * 86400) - (hours * 3600)) / 60)
        seconds_left = int(round(seconds - (days * 86400) - (hours * 3600) - (minutes * 60), 0))
        time_string = ""
        if days > 0:
            time_string += str(days) + " days "
        if hours > 0:
            time_string += str(hours) + " hrs "
        if minutes > 0:
            time_string += str(minutes) + " mins "
        if seconds_left > 0:
            time_string += str(seconds_left) + " secs "

        return time_string
