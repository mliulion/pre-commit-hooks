"""
Hook de pre-commit que detecta si algún secreto definido en un archivo
aparece en los archivos staged.

Uso:
    check_secrets.py --secrets-file .secrets/ archivo1.py archivo2.py
    check_secrets.py --secrets-file .secrets/api_keys.txt archivo1.py

Formato del archivo de secretos (un secreto por línea, # son comentarios):
    # esto es un comentario
    mi_api_key_super_secreta
    otra_clave_secreta
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import sys

log_level_name = os.getenv('CHECK_SECRETS_LOG_LEVEL')
log_level: int = (
    logging._nameToLevel[log_level_name]
    if log_level_name in logging._nameToLevel
    else logging.WARNING
)
logging.basicConfig(
    format='{asctime} {levelname:.1} {pathname}:{lineno} - {message}',
    style='{',
    level=log_level,
    datefmt='%Y-%m-%d %H:%M:%S',
)
_logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Detecta secretos dentro del código.',
    )
    parser.add_argument(
        '--secrets-file',
        required=True,
        metavar='FILE_OR_DIR',
        help='Archivo o directorio con secretos (# son comentarios)',
    )
    parser.add_argument(
        '--secret-name',
        default='Secret',
        metavar='NAME',
        help='Nombre descriptivo para mensajes (ej: --secret-name "API Key")',
    )
    parser.add_argument(
        'filenames',
        nargs='*',
        metavar='FILE',
        help='Archivos a escanear (pre-commit los pasa automáticamente)',
    )

    args, unknown = parser.parse_known_args()

    if unknown:
        print(f"Warning: unknown args: {unknown}")

    return args


def load_secrets_from_file(filepath: str) -> list[str]:
    """Lee secretos de un archivo, ignorando comentarios y líneas vacías."""
    secrets = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                secrets.append(line)
    _logger.debug(f"  {filepath}: {len(secrets)} secretos")
    return secrets


def load_secrets(secrets_path: str) -> list[str]:
    """Lee secretos desde un archivo o directorio."""
    if not os.path.exists(secrets_path):
        _logger.error(f"No encontrado: '{secrets_path}'")
        sys.exit(2)

    secrets = []

    if os.path.isdir(secrets_path):
        _logger.debug(f"Cargando secretos desde directorio: '{secrets_path}'")
        for filename in sorted(os.listdir(secrets_path)):
            filepath = os.path.join(secrets_path, filename)
            if os.path.isfile(filepath):
                try:
                    secrets.extend(load_secrets_from_file(filepath))
                except (UnicodeDecodeError, PermissionError) as e:
                    _logger.warning(f"Saltando '{filepath}': {e}")
    else:
        _logger.debug(f"Cargando secretos desde archivo: '{secrets_path}'")
        secrets = load_secrets_from_file(secrets_path)

    _logger.debug(f"Total secretos cargados: {len(secrets)}")
    return secrets


def main() -> None:
    args = parse_args()

    # print('check_secrets args')
    # print(args)
    _logger.debug('args')
    _logger.debug(args)

    secrets = load_secrets(args.secrets_file)

    if not secrets:
        _logger.warning(
            f"No hay secretos en '{args.secrets_file}', nada que chequear.",
        )
        sys.exit(0)

    found = False
    for filepath in args.filenames:
        _logger.debug(f"Escaneando: {filepath}")
        try:
            with open(filepath) as f:
                for i, line in enumerate(f, 1):
                    masked_line = line
                    for secret in secrets:

                        mask_match = '*' * len(secret)

                        masked_line = re.sub(
                            pattern=secret,
                            repl=mask_match,
                            string=masked_line,
                            flags=re.IGNORECASE,
                        )

                    if masked_line != line:
                        print(
                            f"{args.secret_name} encontrado en"
                            f" '{filepath}:{i}':\n\t{masked_line.strip()}",
                        )
                        found = True
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            pass

    sys.exit(1 if found else 0)


if __name__ == '__main__':
    main()
