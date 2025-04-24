import asyncio
import threading
from typing import Optional
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from nautilus_trader.model.data import DataType
from nautilus_trader.core.correctness import PyCondition
from nautilus_channels.channel import ChannelConfig, Channel

class TelegramChannelConfig(ChannelConfig):    
    """
    Configuration for the Notifications actor.

    Attributes:
    -----------
    telegram_bot_token : str
        The token for the Telegram bot used to send notifications.
    telegram_chat_id : str
        The chat ID of the Telegram group or user to send notifications to.
    message_prefix : str, optional
        A prefix to prepend to all messages sent via Telegram (default is an empty string).
    """
    token: str
    chat_id: str
    message_prefix: str = ""
    kwargs: dict = {}
    
class TelegramChannel(Channel):
    """
    A class to manage communication with a Telegram bot using aiogram.
    """
    def __init__(self, config: TelegramChannelConfig):
        """
        Initializes the Telegram bot.
        
        Parameters:
            token (str): Telegram bot API token.
        """
        PyCondition.type(config.token, str)
        PyCondition.type(config.chat_id, str)
        PyCondition.type(config.message_prefix, str)
        PyCondition.type(config.kwargs, dict)
        
        super().__init__(config)
        
        self.bot = Bot(token=self.config.token, **self.config.kwargs)
        self.dp = Dispatcher()
        
        # Register command handlers
        self.dp.message.register(self.start_command, Command("start"))
        self.dp.message.register(self.echo_message)

    async def start_command(self, message: Message):
        """Handles the /start command."""
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}! I am your trading bot.")

    async def echo_message(self, message: Message):
        """Echoes any received message."""
        await message.answer(message.text)

    async def send_message(self, chat_id: int, text: str, **kwargs):
        """
        Sends a message to a specific chat.
        
        Args:
            chat_id (int): The chat ID to send the message to.
            text (str): The message content.
        """
        await self.bot.send_message(chat_id, text, **kwargs)

    def run(self):
        """
        Starts the bot and runs event loop.
        """
        asyncio.run(self.dp.start_polling(self.bot))
        
    def run_background(self):
        """
        Starts the bot in a non-blocking background task.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.dp.start_polling(self.bot))
        except RuntimeError:
            threading.Thread(target=lambda: asyncio.run(self.dp.start_polling(self.bot)), daemon=True).start()


# 
# DUMP
# 




class TelegramNotifications(Actor):
    """Handles notifications related to trading scores and market activity.
    
    Notes:
    ------
        - Don't use Notifications in backtesting.
    """
    def __init__(self, config: NotificationsConfig):
        PyCondition.non_empty(config.telegram_bot_token, "telegram_bot_token")
        PyCondition.non_empty(config.telegram_chat_id, "telegram_chat_id")

        super().__init__(config=config)
        self.dataframe = dataframe
        
        self.telegram = TelegramNotifier(self.config.telegram_bot_token, parse_mode="markdown")
    
    def on_start(self):
        """
        Actions to be performed on notifications start.
        """
        self.telegram.run_background()
        
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument for {self.config.instrument_id}")
            self.stop()
            return
        
        self.tick_size = self.instrument.price_increment
        
        # Subscribe to model and predictions
        self.subscribe_data(data_type=DataType(TradeSignal, metadata={}))

    async def _send_telegram_message(self, message: str, chat_id: Optional[int] = None):
        """Helper function to send a Telegram message."""
        chat_id = chat_id or self.config["telegram_chat_id"]
        await self.telegram.send_message(chat_id=int(chat_id), text=message)

    @handle_exceptions
    async def send_score(self, model: Dict[str, Any]) -> None:
        """Sends a Telegram notification when a trade score crosses a threshold."""
        row = self.dataframe.iloc[-1]
        close_price = row["close"]
        trade_scores = [row[col] for col in model.get("score_column_names", [])]
        trade_score_primary = trade_scores[0] if trade_scores else None
        if trade_score_primary is None:
            return

        band_no, band = self._get_trade_band(trade_score_primary, model)
        if not band:
            return

        if not self._is_notification_needed(model, band_no, band):
            return

        message = self._format_score_message(close_price, trade_score_primary, band, model)
        await self._send_telegram_message(message)

    def _get_trade_band(self, trade_score: float, model: Dict[str, Any]):
        """Determines which band the score falls into."""
        bands = model.get("positive_bands" if trade_score > 0 else "negative_bands", [])
        return next(((i, x) for i, x in enumerate(bands) if trade_score <= x.get("edge")), (len(bands), None))

    def _is_notification_needed(self, model: Dict[str, Any], band_no: int, band: Dict[str, Any]) -> bool:
        """Checks if a notification should be sent based on band movement."""
        prev_band_no = model.get("prev_band_no")
        model["prev_band_no"] = band_no
        return prev_band_no is None or prev_band_no != band_no

    def _format_score_message(self, close_price: float, trade_score: float, band: Dict[str, Any], model: Dict[str, Any]) -> str:
        """Formats the trade score message."""
        symbol_char = {"BTCUSDT": "₿", "ETHUSDT": "Ξ"}.get(self.config["symbol"], self.config["symbol"])
        message = f"{band.get('sign', '')} {symbol_char} {int(close_price):,} Score: {trade_score:+.2f} {band.get('text', '')}"
        return f"*{message}*" if band.get("bold") else message

    @handle_exceptions
    async def send_diagram(self, model: Dict[str, Any]) -> None:
        """Generates and sends a chart to Telegram."""
        df = self._prepare_chart_data(model)
        fig = generate_chart(df, f"${self.config['symbol']}$", score_column=model.get("score_column_names"))
        with io.BytesIO() as buf:
            fig.savefig(buf, format='png')
            buf.seek(0)  # Move the cursor to the start of the file
            await self.telegram.bot.send_photo(chat_id=int(self.config["telegram_chat_id"]), photo=buf)

    def _prepare_chart_data(self, model: Dict[str, Any]) -> pd.DataFrame:
        """Prepares chart data for visualization."""
        required_columns = ["open", "high", "low", "close"] + model.get("score_column_names", [])
        existing_columns = [col for col in required_columns if col in self.dataframe.columns]
        df = self.dataframe[existing_columns]
        return resample_ohlc_data(df.reset_index(), model.get("resampling_freq"), model.get("nrows"))

    @handle_exceptions
    async def send_transaction_message(self, transaction: dict) -> None:
        """Sends a notification for trade transactions."""
        profit, profit_percent, *_ = await generate_transaction_stats() # generate_transaction_stats(self.state_machine.transaction)
        status = transaction.get("status")
        message = f"⚡💰 *{status}: Profit: {profit_percent:.2f}% {profit:.2f}₮*"
        await self._send_telegram_message(message)
