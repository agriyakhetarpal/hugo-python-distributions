project(
  'hugo-python-distributions',
  version : '0.160.1',
  meson_version : '>=1.3.0',
  default_options : ['warning_level=0'],
)

py = import('python').find_installation(pure : true)

go  = find_program('go',  required : true)
git = find_program('git', required : true)

configure_file(
  input : 'src/hugo/_version.py.in',
  output : '_version.py',
  configuration : { 'HUGO_VERSION' : meson.project_version() },
  install : true,
  install_dir : py.get_install_dir() / 'hugo',
  install_tag : 'python-runtime',
)

py.install_sources(
  ['src/hugo/__main__.py', 'src/hugo/cli.py'],
  subdir : 'hugo',
)

