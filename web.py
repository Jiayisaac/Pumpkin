"""Web interface for monitoring the Pumpkin UPS."""
from flask import Flask, jsonify, render_template_string

from ups import UPS

app = Flask(__name__)
ups = UPS()


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>Pumpkin UPS</title>

    <style>
        body {
            margin: 0;
            background: #202020;
            color: #eeeeee;
            font-family: Arial, sans-serif;
        }

        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 20px;
        }

        h1 {
            text-align: center;
        }

        .battery {
            border: 3px solid #eeeeee;
            border-radius: 8px;
            height: 50px;
            margin: 30px 0;
            overflow: hidden;
        }

        .battery-level {
            height: 100%;
            width: 0%;
            background: #eeeeee;
            transition: width 0.5s;
        }

        .percentage {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
        }

        .reading {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #444444;
        }

        .status {
            text-align: center;
            margin-top: 30px;
            font-size: 1.2em;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>Pumpkin UPS</h1>

        <div class="battery">
            <div
                id="battery-level"
                class="battery-level"
            ></div>
        </div>

        <div
            id="percentage"
            class="percentage"
        >
            --%
        </div>

        <div class="reading">
            <span>Voltage</span>
            <span id="voltage">-- V</span>
        </div>

        <div class="reading">
            <span>Current</span>
            <span id="current">-- mA</span>
        </div>

        <div class="reading">
            <span>Power</span>
            <span id="power">-- mW</span>
        </div>

        <div
            id="status"
            class="status"
        >
            Loading...
        </div>
    </div>

    <script>
        async function updateUPS() {
            try {
                const response = await fetch('/api/ups');
                const data = await response.json();

                document.getElementById(
                    'percentage'
                ).textContent =
                    data.percentage.toFixed(0) + '%';

                document.getElementById(
                    'battery-level'
                ).style.width =
                    data.percentage + '%';

                document.getElementById(
                    'voltage'
                ).textContent =
                    data.voltage.toFixed(2) + ' V';

                document.getElementById(
                    'current'
                ).textContent =
                    data.current.toFixed(0) + ' mA';

                document.getElementById(
                    'power'
                ).textContent =
                    data.power.toFixed(0) + ' mW';

                let status = 'Battery';

                if (data.charging) {
                    status = 'Charging';
                } else if (data.discharging) {
                    status = 'Running on battery';
                }

                if (data.low) {
                    status += ' — LOW BATTERY';
                }

                document.getElementById(
                    'status'
                ).textContent = status;

            } catch (error) {
                document.getElementById(
                    'status'
                ).textContent = 'Unable to read UPS';
            }
        }

        updateUPS();

        setInterval(
            updateUPS,
            30000
        );
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Display the UPS monitoring page."""
    return render_template_string(PAGE)


@app.route("/api/ups")
def ups_state():
    """Return the current UPS state as JSON."""
    return jsonify(ups.get_state())


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
