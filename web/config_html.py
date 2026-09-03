"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Pumpkin Configuration</title>

    <style>

        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 700px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow:
                0 2px 10px
                rgba(0, 0, 0, 0.15);
        }

        h1 {
            margin-top: 0;
        }

        h2 {
            margin-top: 30px;
        }

        .field {
            margin-bottom: 20px;
        }

        label {
            display: block;
            font-weight: bold;
            margin-bottom: 6px;
        }

        input,
        select {
            width: 100%;
            padding: 10px;
            box-sizing: border-box;
            font-size: 16px;
            border: 1px solid #cccccc;
            border-radius: 5px;
        }

        .buttons {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .save {
            background: #007bff;
            color: white;
        }

        .reset {
            background: #cccccc;
            color: black;
        }

        .navigation {
            margin-top: 30px;
            text-align: center;
        }

        .navigation a {
            color: #007bff;
            text-decoration: none;
        }

        hr {
            border: 0;
            border-top: 1px solid #dddddd;
            margin: 30px 0;
        }

        .note {
            color: #666666;
            font-size: 0.9em;
            margin-top: -10px;
            margin-bottom: 20px;
        }

    </style>

</head>

<body>

    <div class="container">

        <h1>Pumpkin Configuration</h1>

        <form
            method="POST"
            action="{{ url_for('save') }}"
        >

            <h2>Wi-Fi</h2>

            <div class="field">

                <label for="wifi_ssid">
                    Wi-Fi Network
                </label>

                <select
                    id="wifi_ssid"
                    name="wifi_ssid"
                >

                    <option value="">
                        Don't change Wi-Fi
                    </option>

                    {% for network in networks %}

                        <option value="{{ network }}">
                            {{ network }}
                        </option>

                    {% endfor %}

                </select>

            </div>

            <div class="field">

                <label for="wifi_password">
                    Wi-Fi Password
                </label>

                <input
                    type="password"
                    id="wifi_password"
                    name="wifi_password"
                    autocomplete="new-password"
                >

            </div>

            <div class="note">

                Leave the Wi-Fi network unchanged if you
                only want to modify Pumpkin settings.

            </div>

            <hr>

            <h2>Environment Variables</h2>

            {% for key, value in values.items() %}

                <div class="field">

                    <label for="{{ key }}">
                        {{ key }}
                    </label>

                    <input
                        type="text"
                        id="{{ key }}"
                        name="{{ key }}"
                        value="{{ value }}"
                    >

                </div>

            {% endfor %}

            <div class="buttons">

                <button
                    class="reset"
                    type="button"
                    onclick="window.location.reload()"
                >
                    Reset
                </button>

                <button
                    class="save"
                    type="submit"
                >
                    Save
                </button>

            </div>

        </form>

        <div class="navigation">

            <a href="/ups">
                View UPS Status
            </a>

        </div>

    </div>

</body>

</html>
"""
