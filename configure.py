"""This file allows the user to configure their ISAMBARD install."""

import glob
import json
import os
import readline

text_colours = {
    'HEADER': '\033[95m',
    'OK_BLUE': '\033[94m',
    'OK_GREEN': '\033[92m',
    'WARNING': '\033[93mWARNING: ',
    'FAIL': '\033[91m',
    'END_C': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

isocket_path = os.path.dirname(os.path.realpath(__file__))

settings = {}


def main(args):
    # setup the line parser for user input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

    settings_path = os.path.join(isocket_path, 'web', 'settings.json')
    if args.circleci:
        install_for_circleci(settings_path)
        return
    return


def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]


def install_for_circleci(settings_path):
    cci_settings = {
        "unknown_graphs": {
            "production": "/home/ubuntu/isocket/web/isocket/data/unknown_graphs.p",
            "testing": "/home/ubuntu/isocket/web/unit_tests/unknown_graphs_tests.p"
        },
        "structural_database": {"path": "."}
        }
    with open(str(settings_path), 'w') as outf:
        outf.write(json.dumps(cci_settings, sort_keys=True, indent=4, separators=(',', ':')))
    return


if __name__ == "__main__":
    import argparse

    description = "Generates configuration files required to you certain features of ISAMBARD."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-C', '--circleci', help="Generates settings for circleci.", action="store_true")
    arguments = parser.parse_args()

    main(arguments)
