from pathlib import Path

ENV_FILE = Path(__file__).parent / '.env'

def read_env():
    """Read KEY=value entries from the .env file."""

    values = {}

    if not ENV_FILE.exists():
        return values

    with ENV_FILE.open(
        'r',
        encoding='utf-8'
    ) as file:

        for line in file:

            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith('#'):
                continue

            if '=' not in stripped:
                continue

            key, value = stripped.split(
                '=',
                1
            )

            values[key.strip()] = value.strip()

    return values


def update_env(new_values):
    """
    Update existing KEY=value entries while preserving
    comments, blank lines and ordering.
    """

    if not ENV_FILE.exists():

        raise FileNotFoundError(
            f'{ENV_FILE} does not exist.'
        )

    lines = ENV_FILE.read_text(
        encoding='utf-8'
    ).splitlines()

    output = []

    for line in lines:

        stripped = line.strip()

        if not stripped:
            output.append(line)
            continue

        if stripped.startswith('#'):
            output.append(line)
            continue

        if '=' not in line:
            output.append(line)
            continue

        key, _ = line.split(
            '=',
            1
        )

        key = key.strip()

        if key in new_values:

            output.append(
                f'{key}={new_values[key]}'
            )

        else:

            output.append(line)

    ENV_FILE.write_text(
        '\n'.join(output) + '\n',
        encoding='utf-8'
    )
