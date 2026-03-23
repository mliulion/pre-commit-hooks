#!/usr/bin/env python3

import argparse
import re
import subprocess
import sys
import logging

_logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect patterns to be blocked within staged files"
    )
    parser.add_argument(
        "--target-name",
        metavar="A_NAME",
        help='A name for the target (ej: --target-name "Address")',
    )
    parser.add_argument(
        "--target-regex-list",
        nargs="*",
        default=[],
        metavar="REGEX",
        help="Regular Expresions of the target to be blocked",
    )
    parser.add_argument(
        "--whitelist",
        nargs="*",
        default=[],
        metavar="STRING",
        help=f"Strings that should not be blocked (ej: --whitelist a_string01 a_string02)",
    )
    parser.add_argument(
        "--whitelist-file",
        metavar="FILE",
        help=f"File with one string per line that should not be blocked (# are comments)",
    )
    parser.add_argument(
        "--ignore_file_list",
        nargs="*",
        default=[],
        metavar="PATH",
        help=f"Files to be ignored",
    )
    return parser.parse_args()


def normalize_string(my_string: str) -> str:
    """Normalize strings for comparison."""
    return my_string.replace(".", "").upper()

def load_whitelist(args) -> set:
    whitelist = {normalize_string(r) for r in args.whitelist}
    if args.whitelist_file:
        with open(args.whitelist_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    whitelist.add(normalize_string(line))
    return whitelist

def load_target_list(args):
    target_regex_list = []
    for pattern in args.target_regex_list:
        try:
            target_regex_list.append(re.compile(pattern))
        except re.error as e:
            print(f"Invalid Regex '{pattern}': {e}", file=sys.stderr)
            sys.exit(2)
    return target_regex_list

def main():

    args = parse_args()

    _logger.debug("args")
    _logger.debug(args)

    TARGET_NAME = args.target_name if args.target_name else "Target"
    IGNORE_FILE_LIST = args.ignore_file_list

    target_list = load_target_list(args)

    _logger.debug("target_list")
    _logger.debug(target_list)

    whitelist = load_whitelist(args)

    # Only staging files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    files = result.stdout.strip().splitlines()

    _logger.debug("files")
    _logger.debug(files)

    found = False
    for filepath in files:
        if filepath in IGNORE_FILE_LIST:
            _logger.debug(f"File '{filepath}' ignored")
            continue
        try:
            content = open(filepath).read()
            for i, line in enumerate(content.splitlines(), 1):
                for target_regex in target_list:

                    _logger.debug("target_regex")
                    _logger.debug(target_regex)

                    for match in target_regex.findall(line):
                        target_string = match if isinstance(match, str) else match[0]

                        _logger.debug("target_string")
                        _logger.debug(target_string)

                        if normalize_string(target_string) not in whitelist:
                            print(f"{TARGET_NAME} '{target_string}' found using [{target_regex}] in '{filepath}:{i}' :\n\t{line.strip()}")
                            found = True
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            pass

    _logger.debug("found")
    _logger.debug(found)

    sys.exit(1 if found else 0)

if __name__ == "__main__":
    main()
