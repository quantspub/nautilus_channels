# -*- coding: utf-8 -*-
"""
Nautilus Trader - Communication Channel Module
"""
from __future__ import annotations
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod
from nautilus_trader.core.data import Data
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.common.actor import Actor, ActorConfig

class ChannelType:
    """
    Enum for different types of communication channels.
    """
    TELEGRAM = "telegram"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    PUSH_NOTIFICATIONS = "push_notifications"

class ChannelData(Data):
    """
    Data class for communication channels.

    Attributes:
    -----------
    channel_type : ChannelType
        The type of the channel (e.g., Telegram, Discord).
    channel_id : str
        The unique identifier for the channel.
    """
    channel_type: ChannelType
    channel_id: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
class ChannelConfig(ActorConfig):
    """
    Configuration for a communication channel.

    Attributes:
    -----------
    channel_name : str
        The name of the channel (e.g., Telegram, Discord).
    """
    channel_name: str


class Channel(Actor, ABC):
    """
    Abstract base class for communication channels.

    This class provides a structure for sending notifications and receiving commands.
    """

    def __init__(self, config: ChannelConfig):
        super().__init__(config=config)
        self.channel_name = config.channel_name

    @abstractmethod
    async def send_notification(self, message: str, **kwargs: Dict[str, Any]) -> None:
        """
        Sends a notification through the channel.

        Parameters:
        -----------
        message : str
            The message to send.
        kwargs : Dict[str, Any]
            Additional parameters for the notification.
        """
        pass

    @abstractmethod
    async def handle_command(self, command: str, **kwargs: Dict[str, Any]) -> None:
        """
        Handles a command received through the channel.

        Parameters:
        -----------
        command : str
            The command to process.
        kwargs : Dict[str, Any]
            Additional parameters for the command.
        """
        pass

    def on_start(self) -> None:
        """
        Actions to perform when the channel starts.
        """
        self.log.info(f"{self.channel_name} channel started.")

    def on_stop(self) -> None:
        """
        Actions to perform when the channel stops.
        """
        self.log.info(f"{self.channel_name} channel stopped.")