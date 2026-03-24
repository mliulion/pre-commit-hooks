# My pre-commit-hooks

My [pre-commit](https://pre-commit.com/) Hooks. Check [Releases](https://github.com/mliulion/pre-commit-hooks/releases).

>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
>
>> It's not tested... yet
>


[[_TOC_]]


## Usage

### CLI

```sh
# Help
./check_pattern.py --help

```

```help
usage: check_pattern.py [-h] [--target-name A_NAME] [--target-regex-list [REGEX ...]] [--whitelist [STRING ...]] [--whitelist-file FILE] [--ignore_file_list [PATH ...]] [FILE ...]

Detect patterns to be blocked within files

positional arguments:
  FILE                  File(s) to check

options:
  -h, --help            show this help message and exit
  --target-name A_NAME  A name for the target (ej: --target-name "Address")
  --target-regex-list [REGEX ...]
                        Regular Expresions of the target to be blocked
  --whitelist [STRING ...]
                        Strings that should not be blocked (ej: --whitelist a_string01 a_string02)
  --whitelist-file FILE
                        File with one string per line that should not be blocked (# are comments)
  --ignore_file_list [PATH ...]
                        Files to be ignored

```


```sh
# Basic usage
./check_pattern.py --target-regex-list '\d{1,2}(?:\.\d{3}){2}-[\dkK]|\d{7,8}-[\dkK]' -- _A_FILE_PATH_

# Debug mode
CHECK_PATTERN_LOG_LEVEL=DEBUG ./check_pattern.py --target-regex-list '\d{1,2}(?:\.\d{3}){2}-[\dkK]|\d{7,8}-[\dkK]' -- _A_FILE_PATH_

```


### Config in a `.pre-commit-config.yaml`

```yaml
repos:
    # ...
  - repo: https://github.com/mliulion/pre-commit-hooks
    rev: v0.2.0                                        # check https://github.com/mliulion/pre-commit-hooks/releases
    hooks:
      - id: check_pattern
        name: Detecta RUTs chilenos
        args:
          - "--target-name"
          - 'Rut'

          - "--target-regex-list"
          - '\d{1,2}(?:\.\d{3}){2}-[\dkK]|\d{7,8}-[\dkK]'

          - "--whitelist"
          - "11.111.111-1"
          - "12345678-9"
          - "--"

      - id: check_pattern
        name: Detecta Local path
        args:
          - "--target-name"
          - 'Local path'

          - "--target-regex-list"
          - '(?:file://)?/home/.*'

          - "--ignore_file_list"
          - ".pre-commit-config.yaml"
          - "--"

```

---

# See Also
* [CONTRIBUTING.md](CONTRIBUTING.md)
* [https://pre-commit.com/](https://pre-commit.com/)
* [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit)
* [https://github.com/pre-commit/pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
