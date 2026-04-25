project(
  'hugo-python-distributions',
  version : '0.160.1',
  meson_version : '>=1.3.0',
  default_options : ['warning_level=0'],
)

# Setting `pure: true` routes the Python package (including the bundled Hugo
# executable) to purelib, so platlib stays empty. Combined with the marker file
# installed into libdir below, this keeps the wheel tag at py3-none-<platform>
# instead of a Python-version-specific ABI tag.
# See _has_extension_modules and _pure in mesonpy/__init__.py
py = import('python').find_installation(pure: true)

go  = find_program('go',  required: true)
git = find_program('git', required: true)

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

host_sys = host_machine.system()
host_cpu = host_machine.cpu_family()
exe_suffix = host_sys == 'windows' ? '.exe' : ''

# Map meson's host_machine values to Golang's GOOS/GOARCH values
# for cross-compilation
GOOS_MAP = {
  'linux'   : 'linux',
  'darwin'  : 'darwin',
  'windows' : 'windows',
}
GOARCH_MAP = {
  'x86_64'  : 'amd64',
  'aarch64' : 'arm64',
  'arm'     : 'arm',
  'x86'     : '386',
  'ppc64'   : 'ppc64le',
  's390x'   : 's390x',
  'riscv64' : 'riscv64',
}
if not GOOS_MAP.has_key(host_sys)
  error('Unsupported host_machine.system: ' + host_sys)
endif
if not GOARCH_MAP.has_key(host_cpu)
  error('Unsupported host_machine.cpu_family: ' + host_cpu)
endif
goos = GOOS_MAP[host_sys]
goarch = GOARCH_MAP[host_cpu]

# Use Zig when cross-compiling, except for the "macOS arm64 to macOS x86_64"
# case where Zig lacks the macOS SDK and cannot find libresolv.dylib. For that
# we rely on the system linker as it is where AppleClang has native support
# for cross-compilation. This can still be overridden by setting the use_zig
# option to true or false explicitly.
auto_use_zig = meson.is_cross_build() and host_sys != 'darwin'
use_zig_opt = get_option('use_zig')
use_zig = use_zig_opt.auto() ? auto_use_zig : use_zig_opt.enabled()


custom_target(
  'hugo-binary',
  output : 'hugo' + exe_suffix, # must match src/hugo/cli.py
  command : [
    py.full_path(),
    files('scripts/build_hugo.py'),
    '--hugo-src', meson.project_source_root() / 'hugo-src',
    '--cache',   meson.project_build_root()  / 'hugo_cache',
    '--version', meson.project_version(),
    '--output',  '@OUTPUT@',
    '--use-zig', use_zig.to_string(),
    '--goos',    goos,
    '--goarch',  goarch,
  ],
  install : true,
  install_dir : py.get_install_dir() / 'hugo' / 'binaries',
  install_tag : 'python-runtime',
  build_by_default : true,
  console : true,
)

# This is a hack to make meson-python mark the wheel as non-pure regardless
# of whether the host platform's magic-number check in mesonpy._is_native
# matches the target binary. _pure becomes False whenever mesonpy-libs
# ({libdir}) is non-empty, without running _is_native on its contents. See
#_WheelBuilder._pure in mesonpy/__init__.py.
configure_file(
  output : '.platform_marker',
  configuration : configuration_data(),
  install : true,
  install_dir : get_option('libdir'),
  install_tag : 'runtime',
)

meson.add_dist_script(py.full_path(), files('scripts/prune_sdist.py'))
