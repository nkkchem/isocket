"""This file allows the user to configure their ISAMBARD install."""

import glob
import json
import os
import pathlib
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

isocket_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))

settings = {}


def main(args):
    # setup the line parser for user input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

    settings_path = isocket_path / 'settings.json'
    if args.circleci:
        install_for_circleci(settings_path)
        return
    if settings_path.exists() and (not args.overwrite):
        raise FileExistsError(
            '{FAIL}Configuration files found, these can be overwritten using the "-o" flag.{END_C}'.format(
                **text_colours))
    install(settings_path, basic=args.basic)
    print('{BOLD}{HEADER}Configuration completed successfully.{END_C}'.format(**text_colours))
    return


def complete(text, state):
    return (glob.glob(text+'*')+[None])[state]


def install(settings_path, basic=False):
    base_install()
    if not basic:
        optional_install()
    with open(str(settings_path), 'w') as outf:
        outf.write(json.dumps(settings, sort_keys=True, indent=4, separators=(',', ':')))
    return


def base_install():
    """Generates configuration setting for required functionality of ISAMBARD."""
    # scwrl
    scwrl = {}
    print('{BOLD}{HEADER}Generating configuration files for ISAMBARD.{END_C}\n'
          'All required input can use tab completion for paths.\n'
          '{BOLD}Setting up SCWRL 4.0 (Required){END_C}'.format(**text_colours))
    scwrl_path = get_user_path('Please provide a path to your SCWRL executable')
    scwrl['path'] = str(scwrl_path)
    pack_mode = get_user_option(
        'Please choose your packing mode (flexible is significantly slower but is more accurate).',
        ['flexible', 'rigid'])
    if pack_mode == 'rigid':
        scwrl['rigid_rotamer_model'] = True
    else:
        scwrl['rigid_rotamer_model'] = False
    settings['scwrl'] = scwrl

    # dssp
    print('{BOLD}Setting up DSSP (Recommended){END_C}'.format(**text_colours))
    dssp = {}
    dssp_path = get_user_path('Please provide a path to your DSSP executable.', required=False)
    dssp['path'] = str(dssp_path)
    settings['dssp'] = dssp

    # buff
    print('{BOLD}Setting up BUFF (Required){END_C}'.format(**text_colours))
    buff = {}
    ffs = []
    ff_dir = isocket_path / 'buff' / 'force_fields'
    for ff_file in os.listdir(str(ff_dir)):
        ff = pathlib.Path(ff_file)
        ffs.append(ff.stem)
    force_field_choice = get_user_option(
        'Please choose the default BUFF force field, this can be modified during runtime.',
        ffs)
    buff['default_force_field'] = force_field_choice
    settings['buff'] = buff
    return


def optional_install():
    """Generates configuration settings for optional functionality of ISAMBARD."""
    # bude
    print('{BOLD}Setting up BUDE (optional legacy, replaced with BUFF){END_C}'.format(**text_colours))
    bude = {}
    bude_cmd_files = isocket_path / 'external_programs' / 'bude_cmd_files'
    bude['cmd_files'] = str(bude_cmd_files)
    bude_internal_path = get_user_path('Please provide a path to your BUDE internal executable.', required=False)
    bude['internal_energy_binary'] = str(bude_internal_path)
    settings['bude'] = bude

    # reduce
    print('{BOLD}Setting up Reduce (used to find non-covalent interactions){END_C}'.format(**text_colours))
    reduce = {}
    reduce_path = get_user_path('Please provide a path to your reduce executable.', required=False)
    reduce['path'] = str(reduce_path)
    reduce['folder'] = str(reduce_path.parent) if reduce_path else ''
    settings['reduce'] = reduce

    # interactions database
    print('{BOLD}Setting up interaction database (optional){END_C}'.format(**text_colours))
    interactions_database = {}
    id_path = get_user_path('Please provide a path to the folder that hold the databases.', required=False)
    interactions_database['folder'] = str(id_path)
    settings['interactions_database'] = interactions_database

    # naccess
    print('{BOLD}Setting up naccess (optional){END_C}'.format(**text_colours))
    naccess = {}
    naccess_path = get_user_path('Please provide a path to your naccess executable.', required=False)
    naccess['path'] = str(naccess_path)
    settings['naccess'] = naccess

    # profit
    print('{BOLD}Setting up ProFit (optional){END_C}'.format(**text_colours))
    profit = {}
    profit_path = get_user_path('Please provide a path to your ProFit executable.', required=False)
    profit['path'] = str(profit_path)
    settings['profit'] = profit

    # structural database
    print('{BOLD}Setting up structural database (optional){END_C}'.format(**text_colours))
    sd = {}
    sd_path = get_user_path('Please provide a path to where you structural database is stored.', required=False)
    sd['path'] = str(sd_path)
    settings['structural_database'] = sd
    return


def install_for_circleci(settings_path):
    cci_settings = {
        "unknown_graphs": {
            "production": "/Users/jackheal/Projects/isocket/isocket_app/unknown_graphs",
            "testing": "/Users/jackheal/Projects/isocket/unit_tests/unknown_graphs_test_shelf"
        },
        "structural_database": {"path": ""}
        }
    with open(str(settings_path), 'w') as outf:
        outf.write(json.dumps(cci_settings, sort_keys=True, indent=4, separators=(',', ':')))
    return


def get_user_path(input_messege, required=True):
    good_path = False
    path = None
    f_input_mess = ''.join(['{OK_BLUE}', input_messege, ' Tab completion enabled:{END_C}']).format(**text_colours)
    print(f_input_mess)
    while not good_path:
        ui_path = input()
        if not len(ui_path):
            if required:
                print('{WARNING}Path required for core ISAMBARD functionality.{END_C}'.format(**text_colours))
                continue
            else:
                return ''
        try:
            path = pathlib.Path(ui_path).expanduser().resolve()  # Convert relative paths to absolute
            good_path = True
        except FileNotFoundError:
            print('{WARNING}Path does not exist.{END_C}'.format(**text_colours))
    print('Path set to "{}"'.format(str(path)))
    return path


def get_user_option(input_message, options):
    good_option = False
    option_strings = []
    for i, option in enumerate(options):
        option_str = '[{}] {}'.format(i + 1, option.capitalize())  # Adjust indices to make more convenient
        option_strings.append(option_str)
    f_input_mess = ''.join([
        '{OK_BLUE}', input_message, ' Use a number to select an option:\n{END_C}',
        '\n'.join(option_strings)]).format(**text_colours)
    print(f_input_mess)
    while not good_option:
        try:
            option_choice = int(input())
            if option_choice - 1 in range(len(options)):
                good_option = True
        except ValueError:
            pass
        if not good_option:
            print('{WARNING}Option not recognised, please use the number for the listed option.{END_C}'.format(
                **text_colours))
    return options[option_choice-1]


if __name__ == "__main__":
    import argparse

    description = "Generates configuration files required to you certain features of ISAMBARD."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-b', '--basic', help="Adds only the core functionality.", action="store_true")
    parser.add_argument('-o', '--overwrite', help="Overwrites existing configuration files.", action="store_true")
    parser.add_argument('-C', '--circleci', help="Generates settings for circleci.", action="store_true")
    arguments = parser.parse_args()

    main(arguments)
