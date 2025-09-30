[![](https://img.shields.io/badge/GitHub-HBehrens/puncover-8da0cb?style=flat-square&logo=github)](https://github.com/HBehrens/puncover)
[![](https://img.shields.io/github/actions/workflow/status/HBehrens/puncover/ci.yml?style=flat-square&branch=master)](https://github.com/HBehrens/puncover/actions?query=branch%3Amaster+)
[![](https://img.shields.io/codecov/c/github/HBehrens/puncover/master?style=flat-square)](https://codecov.io/gh/HBehrens/puncover)
[![](https://img.shields.io/pypi/v/puncover?style=flat-square)](https://pypi.org/project/puncover)
[![](https://img.shields.io/pypi/pyversions/puncover?style=flat-square)](https://pypi.org/project/puncover)
[![](https://img.shields.io/github/license/HBehrens/puncover?color=blue&style=flat-square)](https://github.com/HBehrens/puncover)

# puncover

![](https://raw.githubusercontent.com/HBehrens/puncover/master/images/overview.png)

Analyzes C/C++ binaries for code size, static variables and stack usages. It
creates a report with disassembler and call-stack analysis per directory, file,
or function.

## Installation and Usage

Install with pip:

```bash
pip install --user git+https://github.com/paulwuertz/puncover/
```

Run it by passing the binary to analyze:

```bash
puncover --elf_file project.elf
...
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Open the link in your browser to view the analysis.

### Stack usage

To get worst-case stack usage puncover relies on the `-fstack-usage` compilation option and the build directory has to be passed additionally like `puncover --elf_file project.elf --build_dir $PWD/build`.

Compiling with `-fstack-usage` generates stack usage files in the build directory as [introduced to GCC by adacore](https://www.adacore.com/uploads/techPapers/Stack_Analysis.pdf). For each compiled *.c a coresponding *.su is created, containing a line for each function with it's determined stack usage and a qualifier label, that can hint that a function has a non-statically determined - dynamic stack-usage.

### Non-intereactive usage

For montitor firmware changes in CI it can be useful to run puncover and get out some numbers. For getting stack usage of some RTOS threads i.e.

```bash
puncover --elf_file ~/zephyrproject/zephyr/samples/modules/lvgl/demos/build/zephyr/zephyr.elf --build_dir ~/zephyrproject/zephyr/samples/modules/lvgl/demos/build/ --generate-report --report-max-static-stack-usage ready_thread --report-max-static-stack-usage shell_thread --report-max-static-stack-usage main --report-max-static-stack-usage unready_thread --report-max-static-stack-usage bg_thread_main --no-interactive
```

### Configuration file

For larger configuration a file based configuration might be more comfortable to use.

The only necessary option then is `puncover -c config.yaml`

An example configuration file might look like this:

```yaml
elf_file: ~/cannectivity/build/zephyr/zephyr.elf
build_dir: ~/cannectivity/build/
src_root: ~/cannectivity/
port: 5001
feature_version: "cannectivity-1.2"
generate-report: true
report-type: json
report-filename: report
report-max-static-stack-usage: [
  bg_thread_main:::1024,
  led_thread:::1024,
  gs_usb_tx_thread:::1024,
  gs_usb_rx_thread:::1024,
  log_process_thread_func:::768,
]
add-dynamic-calls: [
    z_impl_can_send->can_mcan_send,
    can_mcan_send->gs_usb_can_tx_callback,
]
error_on_exceeded_stack_usage: true
warn_threshold_size_for_max_static_stack_usage: 100
```

### Report export

If the `generate-report` option is selected as true, then a .json report is generated or appended.

A new entry in the object contained in the file configured at `report-filename` is created under the key of the configured `feature_version`. If the file does not exist it is created containing only one report of this run. If the `feature_version` is already defined in the report file it will be overwritten.

## Running Tests Locally

### Setup

To run the tests locally, you need to install the development dependencies:

1. install pyenv: https://github.com/pyenv/pyenv

   ```bash
   curl https://pyenv.run | bash
   ```

2. install all the python environments, using this bashism (this can take a few
   minutes):

   ```bash
   for _py in $(<.python-version ); do pyenv install ${_py}; done
   ```

3. install the development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

### Running Tests

Then you can run the tests with:

```bash
tox
```

or, to target only the current `python` on `$PATH`:

```bash
tox -e py
```

## Publishing Release

### Release Script

See `release.sh` for a script that automates the above steps. This example will
work with the PyPi tokens (now required):

```bash
PUNCOVER_VERSION=0.3.5 TWINE_PASSWORD="<pypi token>" TWINE_USERNAME=__token__ ./release.sh
```

### Manual Steps

Only for reference, the release script should take care of all of this.

<details><summary>Click to expand</summary>

1. Update the version in `puncover/__version__.py`.
2. Commit the version update:

   ```bash
   git add . && git commit -m "Bump version to x.y.z"
   ```

3. Create an annotated tag:

   ```bash
   git tag -a {-m=,}x.y.z
   ```

4. Push the commit and tag:

   ```bash
   git push && git push --tags
   ```

5. Either wait for the GitHub Action to complete and download the release
   artifact for uploading: https://github.com/HBehrens/puncover/actions OR Build
   the package locally: `python setup.py sdist bdist_wheel`

6. Upload the package to PyPI:

   ```bash
   twine upload dist/*
   ```

7. Create GitHub releases:

   - `gh release create --generate-notes x.y.z`
   - attach the artifacts to the release too: `gh release upload x.y.z dist/*`

</details>

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.
