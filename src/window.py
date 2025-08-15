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

from gi.repository import Adw, Gtk, Gio, GObject, GLib
import json
import os

@Gtk.Template(resource_path='/io/github/mohfy/phoneme/window.ui')
class PhonemeWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PhonemeWindow'
    selected_lang = "en_US"
    ipa_dict_list = Gtk.Template.Child()
    word_text = Gtk.Template.Child()
    ipa_text = Gtk.Template.Child()
    language_changer = Gtk.Template.Child()
    history_ui = Gtk.Template.Child()
    clr_history = Gtk.Template.Child()
    history = []
    config_file_path = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        # Load history from file
        app_config_dir = os.path.join(GLib.get_user_config_dir(), "phoneme")
        self.config_file_path = os.path.join(app_config_dir, "history.json")
        os.makedirs(app_config_dir, exist_ok=True)

        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, "r") as f:
                self.history = json.load(f)
        else:
            self.history = []

        # Populate history list
        for history_item in self.history:
            self.add_history_row(history_item)

        # Set up language search
        expr = Gtk.ClosureExpression.new(
            GObject.TYPE_STRING,
            lambda obj, *args: obj.get_string() if obj else "",
            None
        )
        self.language_changer.set_expression(expr)

        # Init IPA Dictionary
        ipa_dict_json = Gio.resources_lookup_data(
            "/io/github/mohfy/phoneme/dicts/ipa_lookup_table.json",
            Gio.ResourceLookupFlags.NONE
        ).get_data().decode("utf-8")
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

    def add_history_row(self, history_item):
        """Add a single history entry row with remove button."""
        row = Adw.ActionRow()
        row.set_title(history_item["ipa"])
        row.set_subtitle(history_item["word"])

        lang_label = Gtk.Label(label=history_item["lang"])
        lang_label.add_css_class("dim-label")
        row.add_suffix(lang_label)

        # Trash button
        remove_btn = Gtk.Button(icon_name="user-trash-symbolic")
        remove_btn.add_css_class("flat")
        remove_btn.set_tooltip_text("Remove from history")
        remove_btn.connect("clicked", self.on_remove_history_row, row, history_item)
        row.add_suffix(remove_btn)

        # Add to the PreferencesGroup (history_ui)
        # PreferencesGroup supports add()/remove() for its children.
        self.history_ui.add(row)

    def on_remove_history_row(self, button, row, history_item):
        """Remove a specific history row."""
        # Remove from internal list
        self.history = [
            h for h in self.history
            if not (
                h["word"] == history_item["word"] and
                h["ipa"] == history_item["ipa"] and
                h["lang"] == history_item["lang"]
            )
        ]

        # Save updated history
        with open(self.config_file_path, "w") as f:
            json.dump(self.history, f, indent=2)

        # Remove row from UI instantly
        try:
            self.history_ui.remove(row)
        except Exception:
            # Fallback: if remove fails, attempt to recreate the group
            parent = self.history_ui.get_parent()
            new_group = Adw.PreferencesGroup(title="History")
            parent.remove(self.history_ui)
            parent.append(new_group)
            self.history_ui = new_group
            for h in self.history:
                self.add_history_row(h)

    @Gtk.Template.Callback()
    def on_entryrow_apply(self, word_text):
        lang = self.selected_lang
        history = self.history

        if "(" in lang and ")" in lang:
            code = lang[lang.find("(")+1 : lang.find(")")]
        else:
            code = lang.split()[-1]

        resource_data = Gio.resources_lookup_data(
            f"/io/github/mohfy/phoneme/dicts/{code}.json",
            Gio.ResourceLookupFlags.NONE
        )
        current = word_text.get_text()
        json_str = resource_data.get_data().decode("utf-8")
        data = json.loads(json_str)
        if ipa := data["entries"][0].get(current):
            self.ipa_text.show()
            self.ipa_text.set_text(ipa)

            # Add history entry
            new_entry = {"word": current, "ipa": ipa, "lang": self.selected_lang}
            self.history.append(new_entry)
            with open(self.config_file_path, "w") as f:
                json.dump(self.history, f, indent=2)

            self.add_history_row(new_entry)

    @Gtk.Template.Callback()
    def on_language_change(self, language_changer, pspec):
        self.selected_lang = language_changer.get_selected_item().get_string()
        print(f"lang changed: {self.selected_lang}")

    @Gtk.Template.Callback()
    def on_button_clicked(self, clr_history):
        """Clear all history entries by replacing the PreferencesGroup with a fresh one."""
        self.history.clear()

        # Replace the PreferencesGroup with a new (empty) group.
        parent = self.history_ui.get_parent()
        # create a fresh group with the same title (use a simple "History" title)
        empty_group = Adw.PreferencesGroup(title="History")

        # replace in the parent container
        parent.remove(self.history_ui)
        parent.append(empty_group)
        self.history_ui = empty_group

        # persist empty history
        with open(self.config_file_path, "w") as f:
            json.dump([], f, indent=2)

        print("History cleared.")

