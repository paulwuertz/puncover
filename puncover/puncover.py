#!/usr/bin/env python

import configargparse
import datetime
import os
import json
import yaml
import webbrowser
from shutil import which
from os.path import dirname
from threading import Timer

from flask import Flask

from puncover import renderers
from puncover.builders import ElfBuilder
from puncover.collector import Collector, STACK_SIZE, TYPE, TYPE_FUNCTION
from puncover.gcc_tools import GCCTools
from puncover.middleware import BuilderMiddleware
from puncover.version import __version__

# Default listening port. Fallback to 8000 if the default port is already in use.
DEFAULT_PORT = 5000
DEFAULT_PORT_FALLBACK = 8000


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def get_default_port():
    return DEFAULT_PORT if not is_port_in_use(DEFAULT_PORT) else DEFAULT_PORT_FALLBACK


def create_builder(
        gcc_base_filename, elf_file=None, su_dir=None, src_root=None, dynamic_calls=None,
        feature_version=None, export_json=None
    ):
    c = Collector(GCCTools(gcc_base_filename))
    if elf_file:
        return ElfBuilder(c, src_root, elf_file, su_dir, dynamic_calls, feature_version, export_json)
    else:
        raise Exception("Unable to configure builder for collector")


app = Flask(__name__)


def get_arm_tools_prefix_path():
    """
    Try to find and return the arm tools triple prefix path, like this:
      /usr/local/gcc-arm-none-eabi-9-2019-q4-major/bin/arm-none-eabi-

    It's used to invoke the other tools, like objdump/nm.

    Note that we could instead use the '-print-prog-name=...' option to gcc,
    which returns the paths we need. For now stick with the hacky method here.
    """
    obj_dump = which("arm-none-eabi-objdump")
    if not obj_dump:
        return None

    gcc_tools_base_dir = dirname(dirname(obj_dump))
    assert gcc_tools_base_dir, "Unable to find gcc tools base dir from {}".format(obj_dump)

    return os.path.join(gcc_tools_base_dir, 'bin/arm-none-eabi-')


def open_browser(host, port):
    webbrowser.open("http://{}:{}/".format(host, port))

def main():
    gcc_tools_base = get_arm_tools_prefix_path()

    parser = configargparse.ArgumentParser(
        description="Analyses C/C++ build output for code size, static variables, and stack usage.",
        formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
        default_config_files=['./punconfig.yaml'],
        config_file_parser_class=configargparse.YAMLConfigFileParser
    )
    parser.add_argument('--add-dynamic-calls', '--add_dynamic_calls', action='append',
                        help="adds a dynamic callee to another function i.e. --add-dynamic-calls 'func_a->func_1' to add func_1 as a calee to func_a ")
    parser.add_argument('-c', '--config', required=False, is_config_file=True, help='config file path', type=yaml.safe_load)
    parser.add_argument('--gcc-tools-base', '--gcc_tools_base', default=gcc_tools_base,
                        help='filename prefix for your gcc tools, e.g. ~/arm-cs-tools/bin/arm-none-eabi-')
    parser.add_argument('--elf_file', '--elf-file', required=True,
                        help='location of an ELF file')
    parser.add_argument('--feature_version', '--feature-version', default="unknown",
                        help='version of the feature to save it in the database i.e. the commit of the branch or pipline ID')
    parser.add_argument('--src_root', '--src-root',
                        help='location of your sources')
    parser.add_argument('--build_dir', '--build-dir',
                        help='location of your build output')
    parser.add_argument('--debug', action='store_true',
                        help='enable Flask debugger')
    parser.add_argument('--generate-report', '--generate_report', action='store_true')
    parser.add_argument('--port', dest='port', default=get_default_port(), type=int,
                        help='port the HTTP server runs on')
    parser.add_argument('--host', default='127.0.0.1',
                        help='host IP the HTTP server runs on')
    parser.add_argument('--open_interactive_browser_session', type=bool,
                        help="don't automatically open a browser window")
    parser.add_argument('--no-interactive', '--no_interactive', action='store_true',
                        help="don't start the interactive website to browse the elf analysis")
    parser.add_argument('--report-type', '--report_type', default="json")
    parser.add_argument('--report-filename', '--report_filename', default="report")
    parser.add_argument('--report-max-static-stack-usage', '--report_max_static_stack_usage', action='append',
                        help="display_name[:max_stack_size] of functions to report the worst case static stack size with i.e. bg_thread_main or bg_thread_main:1024")
    parser.add_argument('--error_on_exceeded_stack_usage', type=bool, default=False,
                        help="If to exit with an os.EX_CONFIG (78) error on exceededing a functions stack usage")
    parser.add_argument('--warn_threshold_size_for_max_static_stack_usage', default=0, type=int,
                        help='Number of bytes before exiting with os.EX_TEMPFAIL (75) as a WARNING')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()

    if args.gcc_tools_base is None:
        print("Unable to find gcc tools base dir (tried searching for 'arm-none-eabi-objdump' on PATH), please specify --gcc-tools-base")
        exit(1)


    export_json = {}
    # append file with new version if already exists
    if args.generate_report and os.path.isfile(args.report_filename+".json"):
        export_json = json.load(open(args.report_filename+".json", "r"))
    export_json[args.feature_version] = {}

    builder = create_builder(args.gcc_tools_base, elf_file=args.elf_file, src_root=args.src_root,
                             su_dir=args.build_dir, dynamic_calls=args.add_dynamic_calls,
                             feature_version=args.feature_version, export_json=export_json)
    builder.build_if_needed()

    stack_report = None
    if args.generate_report:
        warning_threshold = args.warn_threshold_size_for_max_static_stack_usage
        report_max_map, report_status, error_msg = builder.collector.report_max_static_stack_usages_from_function_names(
            args.report_max_static_stack_usage, report_type=args.report_type, warning_threshold=warning_threshold
        )
        export_json[args.feature_version]["stack_reports"] = report_max_map
        export_json[args.feature_version]["timestamp"] = datetime.datetime.now().isoformat()
        json.dump(export_json, open(args.report_filename+".json", "w+"), ensure_ascii=False)
        if args.error_on_exceeded_stack_usage and report_status != os.EX_OK:
            print("ERR "+error_msg)
            exit(report_status)

    renderers.register_jinja_filters(app.jinja_env)
    renderers.register_urls(app, builder.collector, user_defined_stack_report=stack_report)
    app.wsgi_app = BuilderMiddleware(app.wsgi_app, builder)

    if args.debug:
        app.debug = True

    if not args.no_interactive:
        if is_port_in_use(args.port):
            print("Port {} is already in use, please choose a different port.".format(args.port))
            exit(1)

        # Open a browser window, only if this is the first instance of the server
        # from https://stackoverflow.com/a/63216793
        if not args.open_interactive_browser_session and not os.environ.get("WERKZEUG_RUN_MAIN"):
            # wait one second before starting, so the flask server is ready and we
            # don't see a 404 for a moment first
            Timer(1, open_browser, kwargs={"host":args.host, "port":args.port}).start()
            app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
