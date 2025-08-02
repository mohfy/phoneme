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

from gi.repository import Adw, Gtk, Gio, GObject
import json

@Gtk.Template(resource_path='/io/github/mohfy/word2ipa/window.ui')
class Word2ipaWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'Word2ipaWindow'
    selected_lang = "en_US"
    ipa_dict_list = Gtk.Template.Child()
    word_text = Gtk.Template.Child()
    ipa_text = Gtk.Template.Child()
    language_changer = Gtk.Template.Child()
    history = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        # for searching in lang selector
        expr = Gtk.ClosureExpression.new(
        GObject.TYPE_STRING,
        lambda obj, *args: obj.get_string() if obj else "",
        None
        )
        self.language_changer.set_expression(expr)

        # init IPA Dictionary
        ipa_dict_json = Gio.resources_lookup_data(f"/io/github/mohfy/word2ipa/dicts/ipa_lookup_table.json", Gio.ResourceLookupFlags.NONE).get_data().decode("utf-8")
        ipa_data = json.loads(ipa_dict_json)
        for ipa_info in ipa_data:
            ipa_info_row = Adw.ExpanderRow()
            ipa_info_row.set_title(ipa_info["symbol"])
            ipa_info_row.set_subtitle(ipa_info["sound"])

            for id, example in enumerate(ipa_info["examples"]):
                example_row = Adw.ActionRow()
                example_row.set_title(f'{example} => {ipa_info["ipa_examples"][id]}')
                ipa_info_row.add_row(example_row)

            self.ipa_dict_list.add(ipa_info_row)

    @Gtk.Template.Callback()
    def on_entryrow_activate(self, word_text):
        resource_data = Gio.resources_lookup_data(f"/io/github/mohfy/word2ipa/dicts/{self.selected_lang.partition(" ")[0]}.json", Gio.ResourceLookupFlags.NONE)
        current = word_text.get_text()
        json_str = resource_data.get_data().decode("utf-8")
        data = json.loads(json_str)
        if ipa := data["entries"][0][current]:
            self.ipa_text.show()
            self.ipa_text.set_text(ipa)


            history_row = Adw.ActionRow()
            lang = Gtk.Label(label=self.selected_lang)
            history_row.set_title(ipa)
            history_row.set_subtitle(current)

            history_row.add_suffix(lang)
            self.history.add(history_row)

        else:
            self.ipa_text.set_text("IPA translation will appear here.")

    @Gtk.Template.Callback()
    def on_language_change(self, language_changer, pspec):
        self.selected_lang = language_changer.get_selected_item().get_string()
        print(f"lang changed: {self.selected_lang}")
