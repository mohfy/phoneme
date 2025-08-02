# window.py
#
# Copyright 2025 mohfy
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gio
import json

@Gtk.Template(resource_path='/io/github/mohfy/word2ipa/window.ui')
class Word2ipaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'Word2ipaWindow'

    word_text = Gtk.Template.Child()
    ipa_text = Gtk.Template.Child()
    history = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

    @Gtk.Template.Callback()
    def on_entry_activate(self, word_text):
        resource_data = Gio.resources_lookup_data("/io/github/mohfy/word2ipa/dicts/en_US.json", Gio.ResourceLookupFlags.NONE)
        current = word_text.get_text()
        json_str = resource_data.get_data().decode("utf-8")
        data = json.loads(json_str)
        if ipa := data["entries"][0][current]:
            self.ipa_text.set_text(ipa)
            history_row = Adw.ActionRow()
            history_row.set_title(ipa)
            history_row.set_subtitle(current)
            self.history.add(history_row)

        else:
            self.ipa_text.set_text("IPA translation will appear here.")
