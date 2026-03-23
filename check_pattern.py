#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys
import logging

log_level = os.getenv("CHECK_PATTERN_LOG_LEVEL")

log_level = log_level if (log_level in logging._nameToLevel) else logging.WARNING

logging.basicConfig(
    format="{asctime} {levelname:.1} {pathname}:{lineno} - {message}",
    style="{",
    level=log_level,
    datefmt="%Y-%m-%d %H:%M:%S"
)

_logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect patterns to be blocked within files"
    )
    parser.add_argument(
        "filenames",
        nargs="*",                  # pre-commit files
        metavar="FILE",
        help='File(s) to check',
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

    _logger.info("check_pattern!")

    args = parse_args()

    _logger.debug("args")
    _logger.debug(args)

    TARGET_NAME = args.target_name if args.target_name else "Target"
    IGNORE_FILE_LIST = args.ignore_file_list

    target_list = load_target_list(args)

    _logger.debug("target_list")
    _logger.debug(target_list)

    whitelist = load_whitelist(args)

    files = args.filenames

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
                    for match in target_regex.findall(line):

                        _logger.debug("match")
                        _logger.debug(match)

                        target_string = match if isinstance(match, str) else match[0]

                        if normalize_string(target_string) not in whitelist:
                            print(f"{TARGET_NAME} '{target_string}' matched [{target_regex}] in '{filepath}:{i}' :\n\t{line.strip()}")
                            found = True
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            pass

    _logger.debug("found")
    _logger.debug(found)

    sys.exit(1 if found else 0)

if __name__ == "__main__":
    main()
