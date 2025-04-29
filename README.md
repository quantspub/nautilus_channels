# Nautilus Channels

This is a module for [Nautilus Trader](https://nautilustrader.io/) that provides a flexible and unified way to interact with various external communication channels, such as social platforms (Telegram, Discord), SMS gateways, and potentially other notification endpoints (like push notification services).

This module allows your Nautilus Trader strategies and components to:

* Send real-time notifications and alerts based on trading events, strategy signals, or system status.
* Receive commands and instructions from external channels, enabling interactive control of your trading system.


## Features

* **Multi-Channel Support:** Built to support integration with a variety of communication platforms (Telegram, Discord, SMS, etc.) with a consistent interface.
* **Bidirectional Communication:** Facilitates both sending alerts/notifications *from* Nautilus Trader and receiving commands/messages *to* Nautilus Trader.
* **Pluggable Architecture:** Designed to easily add support for new communication channels by implementing a defined interface.
* **Seamless Nautilus Integration:** Connects with the Nautilus Trader core, likely interacting with the MessageBus or other relevant components to send and receive information.
* **Configurable Endpoints:** Allows granular configuration of which alerts go to which channels and how commands are processed from each source.

## Installation

You can install it using pip:

```bash
pip install nautilus-channels
```

You may need to install additional dependencies depending on the specific channels you wish to use (e.g., `python-telegram-bot` for Telegram, `discord.py` for Discord, a library for your chosen SMS gateway). These will be detailed in the specific channel integration documentation.

## Usage

To use `nautilus-channels`, you will typically:

1.  Install the `nautilus-channels` module and the necessary libraries for your desired channels.
2.  Configure the `nautilus-channels` module within your Nautilus Trader configuration, providing API keys, channel IDs, and other channel-specific settings.
3.  Integrate `nautilus-channels` into your Nautilus Trader strategy or custom components to send alerts and handle incoming commands.

**Example: Sending an Alert (Conceptual)**

Within a Nautilus Trader strategy or component, you might interact with `nautilus-channels` like this:

```python
# Assuming 'channels_module' is an instance of the nautilus-channels interface
from nautilus_channels.api import ChannelsAPI

class MyTradingStrategy:
    def __init__(self, channels_api: ChannelsAPI):
        self.channels = channels_api
        # ... other strategy setup

    def on_trade_executed(self, trade):
        alert_message = f"Trade executed: {trade.instrument.symbol} @ {trade.price}"
        self.channels.send_alert("telegram_alerts_channel", alert_message)
        self.channels.send_alert("sms_alerts_group", alert_message)

    # ... other strategy methods
```

**Example: Handling an Incoming Command (Conceptual)**

You would likely define handlers for commands received through the channels module:

```python
# Assuming your channels module is configured to route commands
class CommandHandler:
    def __init__(self, trading_system):
        self.trading_system = trading_system

    def handle_command(self, command):
        if command.name == "close_position":
            instrument_symbol = command.payload.get("symbol")
            if instrument_symbol:
                self.trading_system.close_position(instrument_symbol)
                command.reply("Position closed successfully.")
            else:
                command.reply("Error: Please specify a symbol.")
        elif command.name == "get_status":
            status = self.trading_system.get_status()
            command.reply(f"System Status: {status}")
        # ... handle other commands
```

Detailed examples and API documentation will be provided as the module is developed.

## Configuration

Configuration for `nautilus-channels` will involve specifying which channels are enabled and providing the necessary credentials and settings for each. This will likely be done within your main Nautilus Trader configuration file (e.g., `config.yaml` or similar).

```yaml
channels:
  telegram:
    enabled: true
    bot_token: YOUR_TELEGRAM_BOT_TOKEN
    chat_ids:
      alerts: -123456789 # Example chat ID for alerts
      commands: -987654321 # Example chat ID for commands
  discord:
    enabled: false
    bot_token: YOUR_DISCORD_BOT_TOKEN
    channel_ids:
      alerts: 111111111111111111
      commands: 222222222222222222
  sms:
    enabled: true
    provider: YOUR_SMS_PROVIDER # e.g., twilio
    api_key: YOUR_SMS_API_KEY
    api_secret: YOUR_SMS_API_SECRET
    to_numbers:
      alerts_group: ["+15551234567", "+15557654321"]
      critical_alerts: ["+15559998888"]
```

The exact configuration structure will be finalized during development.

## Contributing

We welcome contributions to the `nautilus-channels` module\! If you have ideas for new features, channel integrations, or improvements, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or bugfix.
3.  Make your changes and ensure tests pass.
4.  Submit a pull request with a clear description of your changes.

Please adhere to the coding standards and guidelines of the Nautilus Trader project.

## License

This project is licensed under the [GNU Lesser General Public License v3.0 (LGPL-3.0)](https://www.google.com/search?q=LICENSE) or the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.google.com/search?q=LICENSE). Please see the https://www.google.com/search?q=LICENSE file for details. (Note: Confirm the exact license aligns with the main Nautilus Trader project).

## Acknowledgements

This module is built as an extension to the powerful open-source algorithmic trading platform, [Nautilus Trader](https://nautilustrader.io/).


