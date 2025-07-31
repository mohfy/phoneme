pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

desktop_file = i18n.merge_file(
        input: 'io.github.mohfy.word2ipa.desktop.in',
       output: 'io.github.mohfy.word2ipa.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

gnome.compile_resources('word2ipa',
  'word2ipa.gresource.xml.in',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

appstream_file = i18n.merge_file(
        input: 'io.github.mohfy.word2ipa.metainfo.xml.in',
       output: 'io.github.mohfy.word2ipa.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data('io.github.mohfy.word2ipa.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])


service_conf = configuration_data()
service_conf.set('bindir', get_option('prefix') / get_option('bindir'))
configure_file(
  input: 'io.github.mohfy.word2ipa.service.in',
  output: 'io.github.mohfy.word2ipa.service',
  configuration: service_conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)

subdir('icons')
