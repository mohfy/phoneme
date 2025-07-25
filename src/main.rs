use gtk::prelude::*;
use relm4::prelude::*;
use serde::Deserialize;
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io::{self, BufReader};

#[derive(Debug, Deserialize)]
struct Dictionary {
    #[serde(rename = "en_US")]
    entries: Vec<HashMap<String, String>>,
}

struct App {
    buffer: gtk::EntryBuffer,
    ipa_result: String,
}

#[derive(Debug)]
enum Msg {
    TextChanged,
}

#[relm4::component]
impl SimpleComponent for App {
    type Init = ();
    type Input = Msg;
    type Output = ();

    view! {
        gtk::Window {
            set_title: Some("Word to IPA"),
            set_default_size: (300, 100),

            gtk::Box {
                set_orientation: gtk::Orientation::Vertical,
                set_spacing: 5,
                set_margin_all: 5,

                gtk::Entry {
                    set_buffer: &model.buffer,
                    connect_activate => Msg::TextChanged,
                },

                gtk::Label {
                    #[watch]
                    set_label: &format!("IPA: {}", model.ipa_result),
                    set_margin_all: 5,
                },
            }
        }
    }

    fn init(
        _init: Self::Init,
        _root: Self::Root,
        _sender: ComponentSender<Self>,
    ) -> ComponentParts<Self> {
        let buffer = gtk::EntryBuffer::new(None::<String>);
        let model = App {
            ipa_result: String::new(),
            buffer,
        };

        let widgets = view_output!();
        ComponentParts { model, widgets }
    }

    fn update(&mut self, msg: Self::Input, _sender: ComponentSender<Self>) {
        if let Msg::TextChanged = msg {
            let word = self.buffer.text().to_string();
            match word_to_ipa(&word) {
                Ok(ipa) => self.ipa_result = ipa,
                Err(err) => {
                    self.ipa_result = format!("Error: {}", err);
                    eprintln!("error: {}", err);
                }
            }
        }
    }
}

fn main() {
    let app = RelmApp::new("com.mohfy.word2ipa");
    app.run::<App>(());
}

fn word_to_ipa(word: &str) -> Result<String, Box<dyn Error>> {
    let file_path = "en_US.json";
    let file = File::open(file_path)?;
    let reader = BufReader::new(file);
    let dictionary: Dictionary = serde_json::from_reader(reader)?;

    if let Some(first_map) = dictionary.entries.get(0) {
        if let Some(ipa) = first_map.get(word) {
            Ok(ipa.clone())
        } else {
            Err(io::Error::new(
                io::ErrorKind::NotFound,
                format!("Word '{}' not found.", word),
            )
            .into())
        }
    } else {
        Err(io::Error::new(io::ErrorKind::NotFound, "No entries found.".to_string()).into())
    }
}
