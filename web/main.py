"""Web interface for monitoring and configuring the Pumpkin."""
import subprocess
import threading
import time

from flask import (
    Flask,
    jsonify,
    render_template_string,
    request,
)

from flame import COLOUR_SCHEMES, Flame
from web.environment import read_env, update_env
from web.config_html import CONFIG_PAGE
from web.restart_html import RESTART_PAGE
from web.ups_html import UPS_PAGE
from environment import ENVIRONMENT
from wifi import WiFi
from ups import UPS

app = Flask(__name__)
_flame: Flame | None = None

if ENVIRONMENT.UPS_PRESENT:
    ups = UPS()
else:
    ups = None


def reboot_after_delay(delay=2):
    """Wait briefly before rebooting."""
    time.sleep(delay)
    subprocess.run(
        [
            'sudo',
            '/usr/sbin/reboot'
        ],
        check=False
    )


@app.route('/')
def configuration():
    """Display the Pumpkin configuration page."""
    values = read_env()

    try:
        networks = WiFi.networks()
    except Exception as error:
        print(
            f'Unable to scan Wi-Fi networks: {error}'
        )
        networks = []

    return render_template_string(
        CONFIG_PAGE,
        values=values,
        networks=networks,
        ups_present=ENVIRONMENT.UPS_PRESENT,
        colour_schemes=COLOUR_SCHEMES,
        active_colour_scheme=(
            _flame.active_colour_scheme
            if _flame is not None
            else COLOUR_SCHEMES[0]
        ),
    )


@app.route(
    '/mode',
    methods=['POST']
)
def set_mode():
    """Change the running flame mode without updating the environment file."""
    if _flame is None:
        return jsonify({
            'ok': False,
            'error': 'Flame is not available.'
        }), 503

    mode = request.form.get(
        'mode',
        ''
    )

    if mode not in COLOUR_SCHEMES:
        return jsonify({
            'ok': False,
            'error': 'Invalid colour scheme.'
        }), 400

    _flame.set_colour_scheme(mode)

    return jsonify({
        'ok': True,
        'mode': _flame.active_colour_scheme,
    })


@app.route(
    '/save',
    methods=['POST']
)
def save():
    """Save Pumpkin configuration and restart."""
    current_values = read_env()
    new_values = {}

    for key in current_values:
        new_values[key] = request.form.get(
            key,
            ''
        )

    update_env(new_values)

    ssid = request.form.get(
        'wifi_ssid',
        ''
    ).strip()
    password = request.form.get(
        'wifi_password',
        ''
    )

    if ssid:
        try:
            WiFi.connect(
                ssid,
                password
            )
        except Exception as error:
            print(
                f'Unable to change Wi-Fi: {error}'
            )

    reboot_thread = threading.Thread(
        target=reboot_after_delay,
        daemon=True
    )
    reboot_thread.start()

    return RESTART_PAGE


@app.route('/ups')
def ups_page():
    """Display the UPS monitoring page."""
    return render_template_string(
        UPS_PAGE
    )


@app.route('/api/ups')
def ups_state():
    """Return the current UPS state as JSON."""
    return jsonify(
        ups.get_state()
    ) if ups is not None else jsonify({})


def run_web_server(flame: Flame):
    """Run the Flask web server using the active Flame instance."""
    global _flame
    _flame = flame

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )


if __name__ == '__main__':
    raise RuntimeError(
        'Run the web server through app.py so it receives the active Flame instance.'
    )
