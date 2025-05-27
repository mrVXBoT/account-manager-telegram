#!/usr/bin/env python3
"""
Telegram Account Manager Bot
Developed by VX (@KOXVX)
"""

import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import random
import traceback
import time
import sys
from datetime import datetime
from dotenv import load_dotenv
from functools import lru_cache, wraps

load_dotenv()
from telebot.async_telebot import AsyncTeleBot, types as telebot_types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import (
    FloodWaitError, 
    BadRequestError, 
    PhoneCodeInvalidError, 
    SessionPasswordNeededError, 
    PasswordHashInvalidError
)

import pyfiglet
from termcolor import colored
import colorama
colorama.init()

from languages import Language

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler("telegram_bot.log", maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration settings for the bot."""
    BOT_TOKEN = os.getenv("BOT_TOKEN", "<your-bot-token>")
    DATA_DIR = os.getenv("DATA_DIR", "data")
    SESSIONS_FILE = os.path.join(DATA_DIR, "Sessions.json")
    REACTION_LIST = ['🔥', '👍', '❤️']
    



def timed_lru_cache(seconds=300, maxsize=128):
    """Cache decorator with time expiration"""

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds
        func.expiration = time.time() + seconds
        
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.time() > func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime
            return func(*args, **kwargs)
        
        return wrapped_func
    
    return wrapper_cache

def rate_limit(calls_per_second=1):
    """Rate limiter decorator for API calls"""
    
    min_interval = 1.0 / calls_per_second
    last_call_time = 0
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_call_time
            elapsed = time.time() - last_call_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            result = await func(*args, **kwargs)
            last_call_time = time.time()
            return result
        return wrapper
    return decorator

async def safe_execute(coroutine, default_value=None):
    """Safely execute a coroutine with error handling"""

    try:
        return await coroutine
    except Exception as e:
        logger.error(f"Error executing coroutine: {e}")
        return default_value

async def process_multiple_accounts(accounts, action_func, *args, **kwargs):
    """Execute a function on multiple accounts simultaneously"""

    tasks = []
    for account in accounts:
        tasks.append(safe_execute(action_func(account, *args, **kwargs)))
    
    return await asyncio.gather(*tasks)

def initialize_data():
    """Initialize the data directory and sessions file if they don't exist."""

    if not os.path.exists(Config.DATA_DIR):
        os.makedirs(Config.DATA_DIR)
    
    if not os.path.exists(Config.SESSIONS_FILE):
        with open(Config.SESSIONS_FILE, 'w', encoding='utf-8') as file:
            json.dump({'sessions': {}}, file, indent=4)


class SessionManager:
    """
    Manage Telegram sessions using Telethon.
    """

    
    @staticmethod
    def read_sessions():
        """Read sessions from the sessions file."""

        with open(Config.SESSIONS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def get_session_count():
        """Get the count of sessions."""

        sessions = SessionManager.read_sessions()
        return len(sessions['sessions'])
    
    @staticmethod
    def add_session(api_id, api_hash, phone, session_string, first_name, account_id, username):
        """Add a new session to the sessions file."""

        
        with open(Config.SESSIONS_FILE, 'r', encoding='utf-8') as file:
            sessions = json.load(file)
        
        
        session_id = f"session_{len(sessions['sessions']) + 1}"
        
        
        sessions['sessions'][session_id] = {
            "id": len(sessions['sessions']) + 1,
            "api_hash": api_hash,
            "api_id": api_id,
            "phone": phone,
            "session": session_string,
            "first_name": first_name,
            "username": username,
            "account_id": account_id
        }
        
        
        with open(Config.SESSIONS_FILE, 'w', encoding='utf-8') as file:
            json.dump(sessions, file, indent=4)
            
        return session_id
    
    @staticmethod
    def delete_session(session_id):
        """Delete a session from the sessions file."""

        with open(Config.SESSIONS_FILE, 'r', encoding='utf-8') as file:
            sessions = json.load(file)
        

        if session_id in sessions['sessions']:
            del sessions['sessions'][session_id]
            

            with open(Config.SESSIONS_FILE, 'w', encoding='utf-8') as file:
                json.dump(sessions, file, indent=4)
            return True
        
        return False
    
    @staticmethod
    async def create_session(api_id, api_hash, phone, bot, chat_id, message_id):
        """Create a new Telethon session."""
        
        try:
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            
            
            await bot.send_message(
                chat_id,
                "Sending code request..."
            )
            
            sent = await client.send_code_request(phone)
            
            return True, client
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def sign_in_with_code(client, phone, code, password=None):
        """
        Sign in with the received code.
        
        Args:
            client (TelegramClient): Telethon client instance
            phone (str): Phone number
            code (str): Verification code
            password (str, optional): Two-step verification password
        
        Returns:
            tuple: (success, session_string or error message, user_info)
        """
        try:
            try:

                user = await client.sign_in(phone, code)
            except SessionPasswordNeededError:

                if password:
                    user = await client.sign_in(password=password)
                else:
                    return False, "Two-step verification is enabled. Please provide your password.", None
            

            session_string = client.session.save()
            

            user_info = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "phone": user.phone
            }
            
            return True, session_string, user_info
        except PhoneCodeInvalidError:
            return False, "Invalid code. Please try again.", None
        except PasswordHashInvalidError:
            return False, "Invalid password. Please try again.", None
        except Exception as e:
            return False, str(e), None



class AccountManager:
    """
    Manage Telegram accounts and perform actions with them.
    """
    
    @staticmethod
    async def get_client_for_session(session_id):
        """
        Create and connect a Telethon client for a specific session.
        
        Args:
            session_id (str): Session ID to create client for
            
        Returns:
            tuple: (success, client or error message)
        """
        sessions = SessionManager.read_sessions()['sessions']
        
        if session_id not in sessions:
            return False, "Session not found"
        
        session_data = sessions[session_id]
        
        try:
            client = TelegramClient(
                StringSession(session_data['session']),
                int(session_data['api_id']),
                session_data['api_hash']
            )
            

            await client.connect()
            
            if not await client.is_user_authorized():
                await client.disconnect()
                return False, "Session is no longer valid"
            
            return True, client
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def get_account_details(session_id):
        """
        Get detailed information about an account.
        
        Args:
            session_id (str): Session ID to get details for
            
        Returns:
            tuple: (success, account_details or error message)
        """
        success, client_or_error = await AccountManager.get_client_for_session(session_id)
        
        if not success:
            return False, client_or_error
        
        client = client_or_error
        
        try:
            
            me = await client.get_me()
            
            
            full = await client(functions.users.GetFullUserRequest(me.id))
            bio = full.full_user.about if hasattr(full.full_user, 'about') else None
            
            
            profile_photos = await client.get_profile_photos(me.id)
            has_photo = len(profile_photos) > 0
            
            
            active_sessions = await client(functions.account.GetAuthorizationsRequest())
            
            
            password_settings = None
            has_2fa = False
            try:
                password_settings = await client(functions.account.GetPasswordRequest())
                has_2fa = password_settings.has_password
            except Exception:
                pass
            
            
            account_details = {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone": me.phone,
                "bio": bio,
                "has_photo": has_photo,
                "premium": me.premium if hasattr(me, 'premium') else False,
                "verified": me.verified if hasattr(me, 'verified') else False,
                "restricted": me.restricted if hasattr(me, 'restricted') else False,
                "sessions_count": len(active_sessions.authorizations),
                "has_2fa": has_2fa
            }
            
            await client.disconnect()
            return True, account_details
        except Exception as e:
            await client.disconnect()
            return False, str(e)
    
    @staticmethod
    async def update_profile(session_id, first_name=None, last_name=None, bio=None, username=None):
        """
        Update account profile information.
        
        Args:
            session_id (str): Session ID to update profile for
            first_name (str, optional): New first name
            last_name (str, optional): New last name
            bio (str, optional): New bio
            username (str, optional): New username
            
        Returns:
            tuple: (success, message)
        """
        success, client_or_error = await AccountManager.get_client_for_session(session_id)
        
        if not success:
            return False, client_or_error
        
        client = client_or_error
        
        try:

            me = await client.get_me()
            current_first_name = me.first_name or ""
            current_last_name = me.last_name or ""
            full = await client(functions.users.GetFullUserRequest(me.id))
            current_bio = full.full_user.about or ""
            
            update_first_name = first_name if first_name is not None else current_first_name
            update_last_name = last_name if last_name is not None else current_last_name
            update_bio = bio if bio is not None else current_bio
            
            await client(functions.account.UpdateProfileRequest(
                first_name=update_first_name,
                last_name=update_last_name,
                about=update_bio
            ))
            
            if username is not None:
                await client(functions.account.UpdateUsernameRequest(
                    username=username
                ))
            
            sessions = SessionManager.read_sessions()
            if session_id in sessions['sessions']:
                if first_name is not None:
                    sessions['sessions'][session_id]['first_name'] = first_name
                if username is not None:
                    sessions['sessions'][session_id]['username'] = username
                
                with open(Config.SESSIONS_FILE, 'w', encoding='utf-8') as file:
                    json.dump(sessions, file, indent=4)
            
            await client.disconnect()
            return True, "Profile updated successfully"
        except Exception as e:
            await client.disconnect()
            return False, str(e)
    
    @staticmethod
    async def update_2fa(session_id, current_password=None, new_password=None):
        """
        Update or set up 2FA password.
        
        Args:
            session_id (str): Session ID to update 2FA for
            current_password (str, optional): Current 2FA password
            new_password (str): New 2FA password
            
        Returns:
            tuple: (success, message)
        """
        success, client_or_error = await AccountManager.get_client_for_session(session_id)
        
        if not success:
            return False, client_or_error
        
        client = client_or_error
        
        try:
            
            password_settings = await client(functions.account.GetPasswordRequest())
            has_2fa = password_settings.has_password
            
            
            if has_2fa:
                await client.edit_2fa(current_password, new_password)
            else:
                await client.edit_2fa(None, new_password)
            
            await client.disconnect()
            return True, "2FA updated successfully"
        except Exception as e:
            await client.disconnect()
            return False, str(e)
    
    
    
    @staticmethod
    async def get_active_sessions(session_id):
        """
        Get detailed information about all active sessions for this account.
        
        Args:
            session_id (str): Session ID to get sessions for
            
        Returns:
            tuple: (success, sessions_list or error message)
        """
        success, client_or_error = await AccountManager.get_client_for_session(session_id)
        
        if not success:
            return False, client_or_error
        
        client = client_or_error
        
        try:
            result = await client(functions.account.GetAuthorizationsRequest())
            sessions = []
            
            for auth in result.authorizations:
                try:
                    date_created = datetime.fromtimestamp(auth.date_created).strftime('%Y-%m-%d %H:%M:%S')
                except (TypeError, ValueError):
                    date_created = str(auth.date_created)
                    
                try:
                    date_active = datetime.fromtimestamp(auth.date_active).strftime('%Y-%m-%d %H:%M:%S')
                except (TypeError, ValueError):
                    date_active = str(auth.date_active)
                
                session_info = {
                    "hash": auth.hash,
                    "device_model": auth.device_model,
                    "platform": auth.platform,
                    "system_version": auth.system_version,
                    "api_id": auth.api_id,
                    "app_name": auth.app_name,
                    "app_version": auth.app_version,
                    "date_created": date_created,
                    "date_active": date_active,
                    "ip": auth.ip,
                    "country": auth.country,
                    "region": auth.region,
                    "is_current": auth.current,
                    "is_official_app": auth.official_app,
                    "is_password_pending": auth.password_pending
                }
                sessions.append(session_info)
            
            await client.disconnect()
            return True, sessions
        except Exception as e:
            logger.error(f"Error in get_active_sessions: {str(e)}\n{traceback.format_exc()}")
            await client.disconnect()
            return False, str(e)
            
    @staticmethod
    async def terminate_sessions(session_id, all_sessions=False, session_ids=None):
        """
        Terminate other sessions for this account.
        
        Args:
            session_id (str): Session ID to terminate sessions for
            all_sessions (bool): Whether to terminate all other sessions
            session_ids (list, optional): List of specific session IDs to terminate
            
        Returns:
            tuple: (success, message)
        """
        success, client_or_error = await AccountManager.get_client_for_session(session_id)
        
        if not success:
            return False, client_or_error
        
        client = client_or_error
        
        try:
            if all_sessions:
                # Terminate all other sessions
                await client(functions.auth.ResetAuthorizationsRequest())
                message = "All other sessions terminated successfully"
            elif session_ids:
                # Terminate specific sessions
                for session_id in session_ids:
                    await client(functions.account.ResetAuthorizationRequest(hash=int(session_id)))
                message = f"{len(session_ids)} sessions terminated successfully"
            else:
                await client.disconnect()
                return False, "No sessions specified to terminate"
            
            await client.disconnect()
            return True, message
        except Exception as e:
            await client.disconnect()
            return False, str(e)
    
    @staticmethod
    async def send_message_with_all_accounts(username, message):
        """
        Send a message to a user with all accounts.
        
        Args:
            username (str): Username to send the message to
            message (str): Message to send
        
        Returns:
            int: Number of successful message sends
        """
        sessions = SessionManager.read_sessions()['sessions']
        success_count = 0
        
        for session_id, session_data in sessions.items():
            try:
                # Create client with session string
                client = TelegramClient(
                    StringSession(session_data['session']),
                    int(session_data['api_id']),
                    session_data['api_hash']
                )
                
                # Connect and send message
                await client.connect()
                await client.send_message(username, message)
                await client.disconnect()
                
                success_count += 1
            except Exception:
                continue
        
        return success_count
    
    @staticmethod
    async def join_channel_with_all_accounts(username):
        """
        Join a channel with all accounts.
        
        Args:
            username (str): Username of the channel to join
        
        Returns:
            int: Number of successful joins
        """
        try:
            sessions = SessionManager.read_sessions()['sessions']
            logger.info(f"Found {len(sessions)} sessions to join channel {username}")
        except Exception as e:
            logger.error(f"Error reading sessions: {str(e)}")
            return 0
        
        if not sessions:
            logger.warning("No sessions found to join channel")
            return 0
        
        success_count = 0
        
        for session_id, session_data in sessions.items():
            try:
                logger.info(f"Attempting to join channel with session {session_id}")
                
                # Validate session data
                if 'session' not in session_data or not session_data['session']:
                    logger.error(f"Session string missing for session {session_id}")
                    continue
                    
                if 'api_id' not in session_data or not session_data['api_id']:
                    logger.error(f"API ID missing for session {session_id}")
                    continue
                    
                if 'api_hash' not in session_data or not session_data['api_hash']:
                    logger.error(f"API hash missing for session {session_id}")
                    continue
                
                # Create client with session string
                client = TelegramClient(
                    StringSession(session_data['session']),
                    int(session_data['api_id']),
                    session_data['api_hash']
                )
                
                # Connect and join channel
                await client.connect()
                if not await client.is_user_authorized():
                    logger.error(f"Session {session_id} is not authorized")
                    await client.disconnect()
                    continue
                
                # Use the correct method for joining channels
                try:
                    # Ensure username is properly formatted
                    if username.startswith('@'):
                        username = username[1:]
                    
                    logger.info(f"Attempting to join channel: {username}")
                    
                    # Get the channel entity first
                    channel_entity = await client.get_entity(username)
                    logger.info(f"Found channel entity: {channel_entity.title if hasattr(channel_entity, 'title') else channel_entity}")
                    
                    # Join the channel using JoinChannelRequest
                    result = await client(JoinChannelRequest(channel_entity))
                    logger.info(f"Successfully joined channel: {channel_entity.title if hasattr(channel_entity, 'title') else username}")
                except Exception as e:
                    logger.error(f"Error joining channel {username}: {str(e)}")
                    logger.error(traceback.format_exc())
                    raise
                        
                await client.disconnect()
                
                logger.info(f"Successfully joined channel with session {session_id}")
                success_count += 1
            except ValueError as ve:
                logger.error(f"Value error with session {session_id}: {str(ve)}")
                continue
            except Exception as e:
                logger.error(f"Error joining channel with session {session_id}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Joined channel with {success_count} out of {len(sessions)} accounts")
        return success_count
    
    @staticmethod
    async def send_reaction_with_all_accounts(message_link):
        """
        Send a reaction to a message with all accounts.
        
        Args:
            message_link (str): Link to the message to react to
        
        Returns:
            int: Number of successful reactions
        """
        try:
            sessions = SessionManager.read_sessions()['sessions']
            logger.info(f"Found {len(sessions)} sessions to send reaction to {message_link}")
        except Exception as e:
            logger.error(f"Error reading sessions: {str(e)}")
            return 0
        
        if not sessions:
            logger.warning("No sessions found to send reaction")
            return 0
        
        success_count = 0
        
        
        try:
            
            if '?single' in message_link:
                message_link = message_link.split('?')[0]
                
            parts = message_link.split('/')
            chat_username = parts[-2]
            message_id = int(parts[-1])
            logger.info(f"Parsed message link: chat={chat_username}, message_id={message_id}")
        except Exception as e:
            logger.error(f"Error parsing message link: {str(e)}")
            return 0
        
        for session_id, session_data in sessions.items():
            try:
                logger.info(f"Attempting to send reaction with session {session_id}")
                
                # Validate session data
                if 'session' not in session_data or not session_data['session']:
                    logger.error(f"Session string missing for session {session_id}")
                    continue
                    
                if 'api_id' not in session_data or not session_data['api_id']:
                    logger.error(f"API ID missing for session {session_id}")
                    continue
                    
                if 'api_hash' not in session_data or not session_data['api_hash']:
                    logger.error(f"API hash missing for session {session_id}")
                    continue
                
                # Create client with session string
                client = TelegramClient(
                    StringSession(session_data['session']),
                    int(session_data['api_id']),
                    session_data['api_hash']
                )
                
                # Connect and send reaction
                await client.connect()
                if not await client.is_user_authorized():
                    logger.error(f"Session {session_id} is not authorized")
                    await client.disconnect()
                    continue
                
                # Get the chat entity
                chat_entity = await client.get_entity(chat_username)
                logger.info(f"Found chat entity: {chat_entity.title if hasattr(chat_entity, 'title') else chat_entity}")
                
                # Use SendReactionRequest from the appropriate module
                try:
                    from telethon.tl.functions.messages import SendReactionRequest
                    
                    # Choose a random reaction from the config
                    reaction = random.choice(Config.REACTION_LIST)
                    logger.info(f"Sending reaction {reaction} to message {message_id}")
                    
                    # Send the reaction
                    result = await client(SendReactionRequest(
                        peer=chat_entity,
                        msg_id=message_id,
                        reaction=[types.ReactionEmoji(emoticon=reaction)]
                    ))
                    
                    logger.info(f"Successfully sent reaction with session {session_id}")
                    success_count += 1
                except ImportError:
                    # Try alternative method if SendReactionRequest is not available
                    logger.warning("SendReactionRequest not available, trying alternative method")
                    try:
                        # Get the message first
                        message = await client.get_messages(chat_entity, ids=message_id)
                        if not message:
                            logger.error(f"Could not find message with ID {message_id}")
                            continue
                            
                        # Try to use the react method if available
                        reaction = random.choice(Config.REACTION_LIST)
                        await message.react(reaction)
                        logger.info(f"Successfully sent reaction with alternative method")
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to send reaction with alternative method: {str(e)}")
                        continue
                
                await client.disconnect()
                
            except Exception as e:
                logger.error(f"Error sending reaction with session {session_id}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"Sent reactions with {success_count} out of {len(sessions)} accounts")
        return success_count



class Keyboards:
    """Generate keyboards for the bot."""
    
    @staticmethod
    def home_keyboard():
        """Generate the home keyboard."""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(Language.get_text("manager_title"), callback_data='not'))
        keyboard.add(
            InlineKeyboardButton(Language.get_text("add_account"), callback_data='add_account'), 
            InlineKeyboardButton(Language.get_text("show_accounts"), callback_data="show_accounts")
        )
        keyboard.add(InlineKeyboardButton(Language.get_text("account_tools"), callback_data='not'))
        keyboard.add(
            InlineKeyboardButton(Language.get_text("send_message"), callback_data='tool_send_message'),
            InlineKeyboardButton(Language.get_text("join_channel"), callback_data='tool_join_channel')
        )
        keyboard.add(InlineKeyboardButton(Language.get_text("send_reaction"), callback_data='tool_reaction'))
        return keyboard
    
    @staticmethod
    def back_home_keyboard():
        """Generate the back home keyboard."""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(Language.get_text("back"), callback_data='back_home'))
        return keyboard
    
    @staticmethod
    def accounts_keyboard():
        """Generate the accounts keyboard."""
        sessions = SessionManager.read_sessions()
        keyboard = InlineKeyboardMarkup(row_width=4)
        keyboard.add(
            InlineKeyboardButton(Language.get_text("id_header"), callback_data="not"),
            InlineKeyboardButton(Language.get_text("name_header"), callback_data="not"),
            InlineKeyboardButton(Language.get_text("view_header"), callback_data="not"),
            InlineKeyboardButton(Language.get_text("delete_header"), callback_data="not")
        )
        
        if len(sessions['sessions']) > 0:
            for session_id, session_data in sessions['sessions'].items():
                # Show the actual account ID instead of session number
                account_id = session_data.get('account_id', session_id.split('_')[1])
                
                # Create name button (full name if available)
                full_name = session_data.get('first_name', '')
                if session_data.get('last_name'):
                    full_name += f" {session_data.get('last_name')}"
                
                # Create view details button
                view_button = InlineKeyboardButton(
                    Language.get_text("view_button"), 
                    callback_data=f"view_account:{session_id}"
                )
                
                # Create delete button
                keyboard.add(
                    InlineKeyboardButton(account_id, callback_data="not"),
                    InlineKeyboardButton(full_name, callback_data=f"edit_account:{session_id}"),
                    view_button,
                    InlineKeyboardButton(Language.get_text("delete_button"), callback_data=f"delete_session:{session_id}")
                )
        else:
            keyboard.add(InlineKeyboardButton(Language.get_text("no_accounts"), callback_data="not"))
        
        keyboard.add(InlineKeyboardButton(Language.get_text("back_button"), callback_data="back_home"))
        return keyboard
    
    @staticmethod
    def account_details_keyboard(session_id):
        """Generate the account details keyboard."""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(Language.get_text("edit_profile"), callback_data=f"edit_account:{session_id}"),
            InlineKeyboardButton(Language.get_text("change_2fa"), callback_data=f"change_2fa:{session_id}")
        )
        keyboard.add(
            InlineKeyboardButton(Language.get_text("manage_sessions"), callback_data=f"manage_sessions:{session_id}")
        )
        keyboard.add(InlineKeyboardButton(Language.get_text("back"), callback_data="show_accounts"))
        return keyboard
    
    @staticmethod
    def edit_profile_keyboard(session_id):
        """Generate the edit profile keyboard."""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(Language.get_text("edit_first_name"), callback_data=f"edit_first_name:{session_id}"),
            InlineKeyboardButton(Language.get_text("edit_last_name"), callback_data=f"edit_last_name:{session_id}")
        )
        keyboard.add(
            InlineKeyboardButton(Language.get_text("edit_username"), callback_data=f"edit_username:{session_id}"),
            InlineKeyboardButton(Language.get_text("edit_bio"), callback_data=f"edit_bio:{session_id}")
        )
        keyboard.add(InlineKeyboardButton(Language.get_text("back"), callback_data=f"view_account:{session_id}"))
        return keyboard
    
    @staticmethod
    def manage_sessions_keyboard(session_id):
        """Generate the manage sessions keyboard."""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(Language.get_text("view_active_sessions"), callback_data=f"view_active_sessions:{session_id}"))
        keyboard.add(InlineKeyboardButton(Language.get_text("terminate_all_sessions"), callback_data=f"terminate_all:{session_id}"))
        keyboard.add(InlineKeyboardButton(Language.get_text("back"), callback_data=f"view_account:{session_id}"))
        return keyboard
    
    @staticmethod
    def change_2fa_keyboard(session_id):
        """Generate the change 2FA keyboard."""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(Language.get_text("set_change_password"), callback_data=f"set_2fa:{session_id}"))
        keyboard.add(InlineKeyboardButton(Language.get_text("back"), callback_data=f"view_account:{session_id}"))
        return keyboard



class Messages:
    """Store message templates for the bot with language support."""
    
    @classmethod
    def get(cls, key, **kwargs):
        """Get message text in the current language with optional formatting."""
        text = Language.get_text(key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError as e:
                logging.error(f"Missing format key in message: {e}")
                return text
        return text
    
    
    WELCOME = Language.get_text("welcome")
    SHOW_ACCOUNTS = Language.get_text("show_accounts")
    ADD_ACCOUNT = Language.get_text("add_account")
    API_HASH_PROMPT = Language.get_text("api_hash_prompt")
    API_ID_PROMPT = Language.get_text("api_id_prompt")
    PHONE_PROMPT = Language.get_text("phone_prompt")
    CODE_PROMPT = Language.get_text("code_prompt")
    PASSWORD_PROMPT = Language.get_text("password_prompt")
    ACCOUNT_ADDED = Language.get_text("account_added")
    EDIT_FIRST_NAME_PROMPT = Language.get_text("edit_first_name_prompt")
    EDIT_LAST_NAME_PROMPT = Language.get_text("edit_last_name_prompt")
    EDIT_USERNAME_PROMPT = Language.get_text("edit_username_prompt")
    EDIT_BIO_PROMPT = Language.get_text("edit_bio_prompt")
    CURRENT_2FA_PROMPT = Language.get_text("current_2fa_prompt")
    NEW_2FA_PROMPT = Language.get_text("new_2fa_prompt")
    MESSAGE_USERNAME_PROMPT = Language.get_text("message_username_prompt")
    MESSAGE_CONTENT_PROMPT = Language.get_text("message_content_prompt")
    JOIN_CHANNEL_PROMPT = Language.get_text("join_channel_prompt")
    REACTION_PROMPT = Language.get_text("reaction_prompt")
    
    @classmethod
    def update_messages(cls):
        """Update all messages with current language"""
        cls.WELCOME = Language.get_text("welcome")
        cls.SHOW_ACCOUNTS = Language.get_text("show_accounts")
        cls.ADD_ACCOUNT = Language.get_text("add_account")
        cls.API_HASH_PROMPT = Language.get_text("api_hash_prompt")
        cls.API_ID_PROMPT = Language.get_text("api_id_prompt")
        cls.PHONE_PROMPT = Language.get_text("phone_prompt")
        cls.CODE_PROMPT = Language.get_text("code_prompt")
        cls.PASSWORD_PROMPT = Language.get_text("password_prompt")
        cls.ACCOUNT_ADDED = Language.get_text("account_added")
        cls.EDIT_FIRST_NAME_PROMPT = Language.get_text("edit_first_name_prompt")
        cls.EDIT_LAST_NAME_PROMPT = Language.get_text("edit_last_name_prompt")
        cls.EDIT_USERNAME_PROMPT = Language.get_text("edit_username_prompt")
        cls.EDIT_BIO_PROMPT = Language.get_text("edit_bio_prompt")
        cls.CURRENT_2FA_PROMPT = Language.get_text("current_2fa_prompt")
        cls.NEW_2FA_PROMPT = Language.get_text("new_2fa_prompt")
        cls.MESSAGE_USERNAME_PROMPT = Language.get_text("message_username_prompt")
        cls.MESSAGE_CONTENT_PROMPT = Language.get_text("message_content_prompt")
        cls.JOIN_CHANNEL_PROMPT = Language.get_text("join_channel_prompt")
        cls.REACTION_PROMPT = Language.get_text("reaction_prompt")
    
    @staticmethod
    def account_details(details):
        """Format account details message."""
        has_photo = "Yes" if details['has_photo'] else "No"
        premium = "Yes" if details['premium'] else "No"
        verified = "Yes" if details['verified'] else "No"
        restricted = "Yes" if details['restricted'] else "No"
        has_2fa = "Yes" if details['has_2fa'] else "No"
        username = '@' + details['username'] if details['username'] else '-'
        
        # Format the details based on the current language
        return Language.get_text("account_details").format(
            id=details['id'],
            first_name=details['first_name'] or '-',
            last_name=details['last_name'] or '-',
            username=username,
            phone=details['phone'],
            bio=details['bio'] or '-',
            has_photo=has_photo,
            premium=premium,
            verified=verified,
            restricted=restricted,
            sessions_count=details['sessions_count'],
            has_2fa=has_2fa
        )


# Initialize the bot
initialize_data()
bot = AsyncTeleBot(Config.BOT_TOKEN)

# Create Messages instance
messages = Messages()

# Set up bot commands
bot_commands = [
    telebot_types.BotCommand("start", "Start the bot"),
    telebot_types.BotCommand("help", "Show help information"),
    telebot_types.BotCommand("eng", "Switch to English language"),
    telebot_types.BotCommand("fa", "Switch to Persian language")
]

# State variables
state = {
    'waiting_for_input': False,
    'current_action': None,
    'temp_data': {},
    'main_message_id': None,  # Store the main message ID for editing
    'chat_id': None,  # Store the chat ID for editing
    'add_account': {
        'api_hash': None,
        'api_id': None,
        'phone': None,
        'code': None,
        'password': None,
        'client': None,
        'chat_id': None,
        'message_id': None
    }
}


# Command handlers
@bot.message_handler(commands=['start'])
async def start_command(message):
    """Handle the /start command."""
    # Make sure messages are updated with current language
    Messages.update_messages()
    
    # Reset waiting state
    state['waiting_for_input'] = False
    
    # Send the main message and store its ID for future editing using safe_execute
    sent_message = await safe_execute(
        bot.send_message(
            message.chat.id,
            Messages.WELCOME,
            reply_markup=Keyboards.home_keyboard()
        )
    )
    
    # If message sending failed, return early
    if sent_message is None:
        return
    
    # Store the message ID and chat ID in state for future editing
    state['main_message_id'] = sent_message.message_id
    state['chat_id'] = message.chat.id


# Callback query handlers
@bot.callback_query_handler(func=lambda call: call.data == 'back_home')
async def back_home_callback(call):
    """Handle the back home callback."""
    # Reset state
    state['waiting_for_input'] = False
    state['current_action'] = None
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    try:
        await bot.edit_message_text(
            Messages.WELCOME,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=Keyboards.home_keyboard()
        )
    except Exception as e:
        # Ignore 'message is not modified' errors as they're not critical
        if "message is not modified" not in str(e):
            logger.error(f"Error in back_home_callback: {e}")
            # For other errors, try to send a new message
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=Messages.WELCOME,
                    reply_markup=Keyboards.home_keyboard()
                )
            except Exception as send_error:
                logger.error(f"Failed to send new message: {send_error}")
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'add_account')
async def add_account_callback(call):
    """Handle the add account callback."""
    # Reset add account state
    state['add_account'] = {
        'api_hash': None,
        'api_id': None,
        'phone': None,
        'code': None,
        'password': None,
        'client': None,
        'chat_id': call.message.chat.id,
        'message_id': call.message.message_id
    }
    
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = 'api_hash'
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    await bot.edit_message_text(
        Messages.API_HASH_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'show_accounts')
async def show_accounts_callback(call):
    """Handle the show accounts callback."""
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        Messages.SHOW_ACCOUNTS,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.accounts_keyboard()
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_session:'))
async def delete_session_callback(call):
    """Handle the delete session callback."""
    session_id = call.data.split(':')[1]
    
    # Delete session
    success = SessionManager.delete_session(session_id)
    
    if success:
        await bot.answer_callback_query(call.id, "Account deleted successfully!")
    else:
        await bot.answer_callback_query(call.id, "Failed to delete account!")
    
    # Update accounts list (using send_message instead of edit_message_text)
    await bot.send_message(
        call.message.chat.id,
        Messages.SHOW_ACCOUNTS,
        reply_markup=Keyboards.accounts_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data == 'tool_send_message')
async def tool_send_message_callback(call):
    """Handle the tool send message callback."""
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = 'send_message_username'
    state['temp_data'] = {}
    
    # Use the current message ID or store it for future edits
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    
    # Store these for future reference
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Edit the main message to show the prompt
    await bot.edit_message_text(
        Messages.MESSAGE_USERNAME_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'tool_join_channel')
async def tool_join_channel_callback(call):
    """Handle the tool join channel callback."""
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = 'join_channel'
    
    # Use the current message ID or store it for future edits
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    
    # Store these for future reference
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Edit the main message to show the prompt
    await bot.edit_message_text(
        Messages.JOIN_CHANNEL_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'tool_reaction')
async def tool_reaction_callback(call):
    """Handle the tool reaction callback."""
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = 'send_reaction'
    
    # Use the current message ID or store it for future edits
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    
    # Store these for future reference
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Edit the main message to show the prompt
    await bot.edit_message_text(
        Messages.REACTION_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


# Add callback handlers for account management
@bot.callback_query_handler(func=lambda call: call.data.startswith('view_account:'))
async def view_account_callback(call):
    """Handle the view account callback."""
    session_id = call.data.split(':')[1]
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Get account details
    success, result = await AccountManager.get_account_details(session_id)
    
    if success:
        # Format account details message
        account_details_message = Messages.account_details(result)
        
        # Edit the message instead of sending a new one
        await bot.edit_message_text(
            account_details_message,
            chat_id=chat_id,
            message_id=message_id,
            parse_mode='Markdown',
            reply_markup=Keyboards.account_details_keyboard(session_id)
        )
    else:
        # Edit the message with error
        await bot.edit_message_text(
            f"Failed to get account details: {result}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=Keyboards.back_home_keyboard()
        )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_account:'))
async def edit_account_callback(call):
    """Handle the edit account callback."""
    session_id = call.data.split(':')[1]
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        "Select what you want to edit:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.edit_profile_keyboard(session_id)
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_first_name:'))
async def edit_first_name_callback(call):
    """Handle the edit first name callback."""
    session_id = call.data.split(':')[1]
    
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = f'edit_first_name:{session_id}'
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        Messages.EDIT_FIRST_NAME_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_last_name:'))
async def edit_last_name_callback(call):
    """Handle the edit last name callback."""
    session_id = call.data.split(':')[1]
    
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = f'edit_last_name:{session_id}'
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        Messages.EDIT_LAST_NAME_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_username:'))
async def edit_username_callback(call):
    """Handle the edit username callback."""
    session_id = call.data.split(':')[1]
    
    # Set waiting state
    state['waiting_for_input'] = True
    state['current_action'] = f'edit_username:{session_id}'
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        Messages.EDIT_USERNAME_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_bio:'))
async def edit_bio_callback(call):
    """Handle the edit bio callback."""
    session_id = call.data.split(':')[1]
    
    
    state['waiting_for_input'] = True
    state['current_action'] = f'edit_bio:{session_id}'
    
    
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    
    await bot.edit_message_text(
        Messages.EDIT_BIO_PROMPT,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.back_home_keyboard()
    )
    
    
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('change_2fa:'))
async def change_2fa_callback(call):
    """Handle the change 2FA callback."""
    session_id = call.data.split(':')[1]
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        "2FA Password Management:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.change_2fa_keyboard(session_id)
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_2fa:'))
async def set_2fa_callback(call):
    """Handle the set 2FA callback."""
    session_id = call.data.split(':')[1]
    
    # Get account details to check if 2FA is already enabled
    success, result = await AccountManager.get_account_details(session_id)
    
    if success:
        # Set waiting state
        state['waiting_for_input'] = True
        state['temp_data'] = {'session_id': session_id}
        
        if result['has_2fa']:
            # If 2FA is already enabled, ask for current password first
            state['current_action'] = 'current_2fa_password'
            await bot.send_message(
                call.message.chat.id,
                Messages.CURRENT_2FA_PROMPT,
                reply_markup=Keyboards.back_home_keyboard()
            )
        else:
            # If 2FA is not enabled, ask for new password directly
            state['current_action'] = 'new_2fa_password'
            await bot.send_message(
                call.message.chat.id,
                Messages.NEW_2FA_PROMPT,
                reply_markup=Keyboards.back_home_keyboard()
            )
    else:
        await bot.send_message(
            call.message.chat.id,
            f"Failed to get account details: {result}",
            reply_markup=Keyboards.back_home_keyboard()
        )
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_sessions:'))
async def manage_sessions_callback(call):
    """Handle the manage sessions callback."""
    session_id = call.data.split(':')[1]
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message instead of sending a new one
    await bot.edit_message_text(
        "Session Management:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.manage_sessions_keyboard(session_id)
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('terminate_all:'))
async def terminate_all_callback(call):
    """Handle the terminate all sessions callback."""
    session_id = call.data.split(':')[1]
    
    
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    
    await bot.edit_message_text(
        Language.get_text("terminating_sessions"),
        chat_id=chat_id,
        message_id=message_id
    )
    
    
    success, result_message = await AccountManager.terminate_sessions(session_id, all_sessions=True)
    
    if success:
        
        success, sessions_or_error = await AccountManager.get_active_sessions(session_id)
        
        if success:
            
            sessions_text = format_sessions_info(sessions_or_error)
            
            
            await bot.edit_message_text(
                f"✅ {Language.get_text('all_sessions_terminated')}\n\n{sessions_text}",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=generate_sessions_keyboard(session_id, sessions_or_error),
                parse_mode="HTML"
            )
        else:
            # Show success message but couldn't refresh sessions
            await bot.edit_message_text(
                f"✅ {Language.get_text('all_sessions_terminated')}",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=Keyboards.manage_sessions_keyboard(session_id)
            )
    else:
        # Show error message
        await bot.edit_message_text(
            f"❌ {Language.get_text('failed_terminate_sessions')}: {result_message}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=Keyboards.manage_sessions_keyboard(session_id)
        )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


# Change photo functionality has been removed as requested


@bot.callback_query_handler(func=lambda call: call.data.startswith('manage_sessions:'))
async def manage_sessions_back_callback(call):
    """Handle the manage sessions callback for returning from session list."""
    session_id = call.data.split(':')[1]
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Edit the message to show the session management menu
    await bot.edit_message_text(
        Language.get_text("session_management"),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=Keyboards.manage_sessions_keyboard(session_id)
    )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('view_active_sessions:'))
async def view_active_sessions_callback(call):
    """Handle the view active sessions callback."""
    session_id = call.data.split(':')[1]
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Show loading message
    await bot.edit_message_text(
        Language.get_text("fetching_sessions"),
        chat_id=chat_id,
        message_id=message_id
    )
    
    # Get active sessions
    success, sessions_or_error = await AccountManager.get_active_sessions(session_id)
    
    if success:
        # Format sessions information
        sessions_text = format_sessions_info(sessions_or_error)
        
        # Generate keyboard with session-specific actions
        keyboard = generate_sessions_keyboard(session_id, sessions_or_error)
        
        # Edit the message to show sessions
        await bot.edit_message_text(
            sessions_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Show error message
        await bot.edit_message_text(
            f"❌ {Language.get_text('failed_terminate_sessions')}: {sessions_or_error}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=Keyboards.manage_sessions_keyboard(session_id)
        )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('terminate_session:'))
async def terminate_session_callback(call):
    """Handle the terminate specific session callback."""
    parts = call.data.split(':')
    session_id = parts[1]
    auth_hash = int(parts[2])
    
    # Use the stored message ID or the current message ID
    message_id = state.get('main_message_id') or call.message.message_id
    chat_id = state.get('chat_id') or call.message.chat.id
    
    # Show loading message
    await bot.edit_message_text(
        Language.get_text("terminating_sessions"),
        chat_id=chat_id,
        message_id=message_id
    )
    
    # Terminate the specific session
    success, result_message = await AccountManager.terminate_sessions(session_id, session_ids=[auth_hash])
    
    if success:
        # Get updated sessions after termination
        success, sessions_or_error = await AccountManager.get_active_sessions(session_id)
        
        if success:
            sessions_text = format_sessions_info(sessions_or_error)
            
            keyboard = generate_sessions_keyboard(session_id, sessions_or_error)
            
            await bot.edit_message_text(
                f"✅ {Language.get_text('session_terminated')}\n\n{sessions_text}",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await bot.edit_message_text(
                f"{Language.get_text('session_terminated')}\n{Language.get_text('fetching_sessions')} {sessions_or_error}",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=Keyboards.manage_sessions_keyboard(session_id)
            )
    else:
        # Show error message
        await bot.edit_message_text(
            f"❌ {Language.get_text('failed_terminate_sessions')}: {result_message}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=Keyboards.manage_sessions_keyboard(session_id)
        )
    
    # Update the stored message ID and chat ID
    state['main_message_id'] = message_id
    state['chat_id'] = chat_id
    
    # Answer the callback query to remove the loading state
    await bot.answer_callback_query(call.id)


def format_sessions_info(sessions):
    """Format sessions information for display."""
    if not sessions:
        return Language.get_text("no_sessions")
    
    # Start with header
    text = Language.get_text("active_sessions_header")
    
    # Store session hashes for the state
    state['temp_data']['sessions'] = {}
    
    # Add each session
    for i, session in enumerate(sessions, 1):
        # Mark current session
        current_marker = Language.get_text("current_session") if session["is_current"] else ""
        
        # Store session hash with index
        session_hash = session["hash"]
        state['temp_data']['sessions'][i] = session_hash
        
        # Format session information using language keys
        text += Language.get_text("session_number").format(number=i, current_marker=current_marker) + "\n"
        text += Language.get_text("device").format(device_model=session['device_model']) + "\n"
        text += Language.get_text("platform").format(platform=session['platform'], system_version=session['system_version']) + "\n"
        text += Language.get_text("app").format(app_name=session['app_name'], app_version=session['app_version']) + "\n"
        text += Language.get_text("created").format(date_created=session['date_created']) + "\n"
        text += Language.get_text("last_active").format(date_active=session['date_active']) + "\n"
        text += Language.get_text("ip").format(ip=session['ip']) + "\n"
        text += Language.get_text("location").format(country=session['country'], region=session['region']) + "\n"
        
        # Add official app and password pending indicators if applicable
        if session["is_official_app"]:
            text += Language.get_text("official_app") + "\n"
        if session["is_password_pending"]:
            text += Language.get_text("password_pending") + "\n"
        
        # Add session hash for debugging/reference
        text += Language.get_text("session_id").format(hash=session_hash) + "\n"
        
        # Add separator between sessions
        if i < len(sessions):
            text += "\n" + "-" * 30 + "\n\n"
    
    return text


def generate_sessions_keyboard(session_id, sessions):
    """Generate keyboard with buttons for each session."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Add buttons for each session
    buttons = []
    for i in range(1, len(sessions) + 1):
        # Skip current session as it can't be terminated
        if sessions[i-1]["is_current"]:
            continue
            
        buttons.append(InlineKeyboardButton(
            Language.get_text("terminate_session").format(number=i),
            callback_data=f"terminate_session:{session_id}:{sessions[i-1]['hash']}"
        ))
    
    # Add buttons in pairs
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i+1])
        else:
            keyboard.add(buttons[i])
    
    # Add back button
    keyboard.add(InlineKeyboardButton(Language.get_text("terminate_all_sessions"), callback_data=f"terminate_all:{session_id}"))
    keyboard.add(InlineKeyboardButton("╠═══ BACK ← ═══╣", callback_data=f"manage_sessions:{session_id}"))
    
    return keyboard


# Message handlers
@bot.message_handler(func=lambda message: state['waiting_for_input'])
@rate_limit(calls_per_second=5)  # محدود کردن تعداد فراخوانی‌ها برای ورودی کاربر
async def handle_input(message):
    """Handle user input based on current state."""
    try:
        action = state['current_action']
    except KeyError:
        logger.error("Current action not found in state")
        # بازگشت به منوی اصلی در صورت بروز خطا
        state['waiting_for_input'] = False
        state['current_action'] = None
        await safe_execute(
            bot.send_message(
                message.chat.id,
                "An error occurred. Returning to main menu...",
                reply_markup=Keyboards.home_keyboard()
            )
        )
        return
    
    # Handle add account flow
    if action == 'api_hash':
        state['add_account']['api_hash'] = message.text
        state['current_action'] = 'api_id'
        
        # Use the stored message ID or create a new one
        if state.get('main_message_id'):
            await safe_execute(
                bot.edit_message_text(
                    Messages.API_ID_PROMPT,
                    chat_id=state['chat_id'],
                    message_id=state['main_message_id'],
                    reply_markup=Keyboards.back_home_keyboard()
                )
            )
        else:
            # If no main message exists, create one
            sent_message = await safe_execute(
                bot.send_message(
                    message.chat.id, 
                    Messages.API_ID_PROMPT,
                    reply_markup=Keyboards.back_home_keyboard()
                )
            )
            
            # If message sending failed, return early
            if sent_message is None:
                return
                
            state['main_message_id'] = sent_message.message_id
            state['chat_id'] = message.chat.id
    
    elif action == 'api_id':
        state['add_account']['api_id'] = message.text
        state['current_action'] = 'phone'
        
        # Edit the main message
        await bot.edit_message_text(
            Messages.PHONE_PROMPT,
            chat_id=state['chat_id'],
            message_id=state['main_message_id'],
            reply_markup=Keyboards.back_home_keyboard()
        )
    
    elif action == 'phone':
        state['add_account']['phone'] = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Processing your request, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Create session
        success, result = await SessionManager.create_session(
            state['add_account']['api_id'],
            state['add_account']['api_hash'],
            state['add_account']['phone'],
            bot,
            message.chat.id,
            message.message_id
        )
        
        if success:
            state['add_account']['client'] = result
            state['current_action'] = 'code'
            
            # Edit the main message to prompt for code
            await bot.edit_message_text(
                Messages.CODE_PROMPT,
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.back_home_keyboard()
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to create session: {result}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.back_home_keyboard()
            )
            state['waiting_for_input'] = False
    
    elif action == 'code':
        state['add_account']['code'] = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Verifying code, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Sign in with code
        success, result, user_info = await SessionManager.sign_in_with_code(
            state['add_account']['client'],
            state['add_account']['phone'],
            state['add_account']['code']
        )
        
        if success:
            # Add session
            session_id = SessionManager.add_session(
                state['add_account']['api_id'],
                state['add_account']['api_hash'],
                state['add_account']['phone'],
                result,
                user_info['first_name'],
                str(user_info['id']),
                user_info['username']
            )
            
            # Edit the main message to show success
            await bot.edit_message_text(
                Messages.ACCOUNT_ADDED,
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.home_keyboard()
            )
            state['waiting_for_input'] = False
        elif "Two-step verification" in result:
            state['current_action'] = 'password'
            
            # Edit the main message to prompt for password
            await bot.edit_message_text(
                Messages.PASSWORD_PROMPT,
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.back_home_keyboard()
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to sign in: {result}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.back_home_keyboard()
            )
            state['waiting_for_input'] = False
    
    elif action == 'password':
        state['add_account']['password'] = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Verifying password, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Sign in with password
        success, result, user_info = await SessionManager.sign_in_with_code(
            state['add_account']['client'],
            state['add_account']['phone'],
            state['add_account']['code'],
            state['add_account']['password']
        )
        
        if success:
            # Add session
            session_id = SessionManager.add_session(
                state['add_account']['api_id'],
                state['add_account']['api_hash'],
                state['add_account']['phone'],
                result,
                user_info['first_name'],
                str(user_info['id']),
                user_info['username']
            )
            
            # Edit the main message to show success
            await bot.edit_message_text(
                Messages.ACCOUNT_ADDED,
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.home_keyboard()
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to sign in: {result}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.back_home_keyboard()
            )
        
        state['waiting_for_input'] = False
    
    # Handle profile editing
    elif action.startswith('edit_first_name:'):
        session_id = action.split(':')[1]
        new_first_name = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Updating first name, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Update profile
        success, result_message = await AccountManager.update_profile(
            session_id,
            first_name=new_first_name
        )
        
        if success:
            # Edit the main message to show success
            await bot.edit_message_text(
                "First name updated successfully!",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to update first name: {result_message}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        
        state['waiting_for_input'] = False
    
    elif action.startswith('edit_last_name:'):
        session_id = action.split(':')[1]
        new_last_name = None if message.text.lower() == 'none' else message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Updating last name, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Update profile
        success, result_message = await AccountManager.update_profile(
            session_id,
            last_name=new_last_name
        )
        
        if success:
            # Edit the main message to show success
            await bot.edit_message_text(
                "Last name updated successfully!",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to update last name: {result_message}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        
        state['waiting_for_input'] = False
    
    elif action.startswith('edit_username:'):
        session_id = action.split(':')[1]
        new_username = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Updating username, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Update profile
        success, result_message = await AccountManager.update_profile(
            session_id,
            username=new_username
        )
        
        if success:
            # Edit the main message to show success
            await bot.edit_message_text(
                "Username updated successfully!",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to update username: {result_message}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        
        state['waiting_for_input'] = False
    
    elif action.startswith('edit_bio:'):
        session_id = action.split(':')[1]
        new_bio = None if message.text.lower() == 'none' else message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Updating bio, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Update profile
        success, result_message = await AccountManager.update_profile(
            session_id,
            bio=new_bio
        )
        
        if success:
            # Edit the main message to show success
            await bot.edit_message_text(
                "Bio updated successfully!",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to update bio: {result_message}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.edit_profile_keyboard(session_id)
            )
        
        state['waiting_for_input'] = False
    
    # Handle 2FA password flow
    elif action == 'current_2fa_password':
        current_password = message.text
        state['temp_data']['current_password'] = current_password
        state['current_action'] = 'new_2fa_password'
        
        # Edit the main message to prompt for new password
        await bot.edit_message_text(
            Messages.NEW_2FA_PROMPT,
            chat_id=state['chat_id'],
            message_id=state['main_message_id'],
            reply_markup=Keyboards.back_home_keyboard()
        )
    
    elif action == 'new_2fa_password':
        new_password = message.text
        session_id = state['temp_data']['session_id']
        current_password = state['temp_data'].get('current_password')
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Updating 2FA password, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Update 2FA
        success, result_message = await AccountManager.update_2fa(
            session_id,
            current_password=current_password,
            new_password=new_password
        )
        
        if success:
            # Edit the main message to show success
            await bot.edit_message_text(
                "2FA password updated successfully!",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.change_2fa_keyboard(session_id)
            )
        else:
            # Edit the main message to show error
            await bot.edit_message_text(
                f"Failed to update 2FA password: {result_message}",
                chat_id=state['chat_id'],
                message_id=state['main_message_id'],
                reply_markup=Keyboards.change_2fa_keyboard(session_id)
            )
        
        state['waiting_for_input'] = False
    
    # Handle change photo flow
    elif action.startswith('change_photo:'):
        if message.content_type != 'photo':
            await bot.send_message(
                message.chat.id,
                "Please send an image as the new profile photo."
            )
            return
        
        session_id = action.split(':')[1]
        logger.info(f"Starting profile photo update for session {session_id}")
        
        # Notify user that we're processing
        status_message = await bot.send_message(
            message.chat.id,
            "⏳ Processing your photo, please wait..."
        )
        
        try:
            # Get the photo file - use the largest available photo
            logger.debug(f"Getting photo file info for file_id: {message.photo[-1].file_id}")
            file_info = await bot.get_file(message.photo[-1].file_id)
            logger.debug(f"Downloading file from path: {file_info.file_path}")
            downloaded_file = await bot.download_file(file_info.file_path)
            logger.debug(f"Downloaded file size: {len(downloaded_file)} bytes")
            
            # Save photo to a temporary file with a unique name
            import uuid
            temp_photo_path = f"temp_photo_{uuid.uuid4()}.jpg"
            logger.debug(f"Saving to temporary file: {temp_photo_path}")
            with open(temp_photo_path, 'wb') as f:
                f.write(downloaded_file)
            
            logger.debug(f"Temporary file created, size: {os.path.getsize(temp_photo_path)} bytes")
            
            # Use our dedicated function to change the profile photo
            success, message_text = await AccountManager.change_profile_photo(session_id, temp_photo_path)
            
            # Clean up the temporary file regardless of success
            if os.path.exists(temp_photo_path):
                os.remove(temp_photo_path)
                logger.debug(f"Temporary file {temp_photo_path} removed")
            
            if success:
                await bot.edit_message_text(
                    "✅ Profile photo updated successfully!",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id
                )
                
                await bot.send_message(
                    message.chat.id,
                    "You can now view your updated profile.",
                    reply_markup=Keyboards.account_details_keyboard(session_id)
                )
            else:
                await bot.edit_message_text(
                    f"❌ Failed to update profile photo: {message_text}",
                    chat_id=message.chat.id,
                    message_id=status_message.message_id
                )
                
                await bot.send_message(
                    message.chat.id,
                    "Please try again with a different photo.",
                    reply_markup=Keyboards.account_details_keyboard(session_id)
                )
        except Exception as e:
            logger.error(f"Unexpected error in photo processing: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Clean up the temporary file if it exists
            if 'temp_photo_path' in locals() and os.path.exists(temp_photo_path):
                os.remove(temp_photo_path)
                logger.debug(f"Temporary file {temp_photo_path} removed after error")
            
            await bot.edit_message_text(
                f"❌ Failed to process photo: {str(e)}",
                chat_id=message.chat.id,
                message_id=status_message.message_id
            )
            
            await bot.send_message(
                message.chat.id,
                "Please try again with a different photo.",
                reply_markup=Keyboards.account_details_keyboard(session_id)
            )
        
        state['waiting_for_input'] = False
    
    # Handle send message flow
    elif action == 'send_message_username':
        state['temp_data']['username'] = message.text
        state['current_action'] = 'send_message_content'
        
        # Edit the main message to prompt for message content
        await bot.edit_message_text(
            Messages.MESSAGE_CONTENT_PROMPT,
            chat_id=state['chat_id'],
            message_id=state['main_message_id'],
            reply_markup=Keyboards.back_home_keyboard()
        )
    
    elif action == 'send_message_content':
        username = state['temp_data']['username']
        content = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Sending message with all accounts, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Send message with all accounts
        success_count = await AccountManager.send_message_with_all_accounts(username, content)
        
        # Edit the main message to show success
        await bot.edit_message_text(
            f"Message sent successfully with {success_count} accounts!",
            chat_id=state['chat_id'],
            message_id=state['main_message_id'],
            reply_markup=Keyboards.home_keyboard()
        )
        
        state['waiting_for_input'] = False
    
    # Handle join channel flow
    elif action == 'join_channel':
        username = message.text
        
        # Edit the main message to show processing
        await bot.edit_message_text(
            "Joining channel with all accounts, please wait...",
            chat_id=state['chat_id'],
            message_id=state['main_message_id']
        )
        
        # Join channel with all accounts
        success_count = await AccountManager.join_channel_with_all_accounts(username)
        
        # Edit the main message to show success
        await bot.edit_message_text(
            f"Joined channel successfully with {success_count} accounts!",
            chat_id=state['chat_id'],
            message_id=state['main_message_id'],
            reply_markup=Keyboards.home_keyboard()
        )
        
        state['waiting_for_input'] = False
    
    # Handle send reaction flow
    elif action == 'send_reaction':
        message_link = message.text
        
        # Edit the main message to show processing with safe execution
        await safe_execute(
            bot.edit_message_text(
                "Sending reaction with all accounts, please wait...",
                chat_id=state['chat_id'],
                message_id=state['main_message_id']
            )
        )
        
        try:
            # Send reaction with all accounts using process_multiple_accounts for better performance
            # Get all accounts first
            sessions = SessionManager.read_sessions()
            accounts = sessions.get('sessions', {})
            
            # Define a helper function for sending reaction with a single account
            async def send_reaction_with_account(account_id, link):
                # Implementation depends on your AccountManager structure
                # This is a placeholder for the actual implementation
                return await AccountManager.send_reaction(account_id, link)
            
            # Process all accounts in parallel
            results = await process_multiple_accounts(
                accounts.keys(),
                send_reaction_with_account,
                message_link
            )
            
            # Count successful operations
            success_count = sum(1 for result in results if result)
            
            # Edit the main message to show success with safe execution
            await safe_execute(
                bot.edit_message_text(
                    f"Reaction sent successfully with {success_count} accounts!",
                    chat_id=state['chat_id'],
                    message_id=state['main_message_id'],
                    reply_markup=Keyboards.home_keyboard()
                )
            )
        except Exception as e:
            logger.error(f"Error sending reactions: {e}")
            # Show error message to user
            await safe_execute(
                bot.edit_message_text(
                    f"Error sending reactions: {str(e)}",
                    chat_id=state['chat_id'],
                    message_id=state['main_message_id'],
                    reply_markup=Keyboards.home_keyboard()
                )
            )
        finally:
            # Reset waiting state regardless of success or failure
            state['waiting_for_input'] = False


# Command handlers for language switching
@bot.message_handler(commands=['eng'])
@rate_limit(calls_per_second=2)  # محدود کردن تعداد فراخوانی‌ها
async def eng_command(message):
    """Switch the bot language to English."""
    Language.set_language("en")
    Messages.update_messages()
    
    
    state['main_message_id'] = message.message_id + 1  # +1 because we're about to send a message
    state['chat_id'] = message.chat.id
    state['waiting_for_input'] = False
    
    
    sent_message = await safe_execute(
        bot.send_message(
            message.chat.id,
            Language.get_text("language_changed")
        )
    )
    
    
    if sent_message is None:
        return
    
    
    state['main_message_id'] = sent_message.message_id
    
    
    await safe_execute(
        bot.edit_message_text(
            Messages.WELCOME,
            chat_id=message.chat.id,
            message_id=sent_message.message_id,
            reply_markup=Keyboards.home_keyboard()
        )
    )

@bot.message_handler(commands=['fa'])
@rate_limit(calls_per_second=2)  # محدود کردن تعداد فراخوانی‌ها
async def fa_command(message):
    """Switch the bot language to Persian."""
    Language.set_language("fa")
    Messages.update_messages()
    
    # Store the message ID for updating
    state['main_message_id'] = message.message_id + 1  # +1 because we're about to send a message
    state['chat_id'] = message.chat.id
    state['waiting_for_input'] = False
    
    # Send confirmation message with safe execution
    sent_message = await safe_execute(
        bot.send_message(
            message.chat.id,
            Language.get_text("language_changed")
        )
    )
    
    # If message sending failed, return early
    if sent_message is None:
        return
    
    # Update the main message ID
    state['main_message_id'] = sent_message.message_id
    
    # Show the main menu with updated language using safe execution
    await safe_execute(
        bot.edit_message_text(
            Messages.WELCOME,
            chat_id=message.chat.id,
            message_id=sent_message.message_id,
            reply_markup=Keyboards.home_keyboard()
        )
    )

@bot.message_handler(commands=['help'])
@rate_limit(calls_per_second=2)  # محدود کردن تعداد فراخوانی‌ها
@timed_lru_cache(seconds=300)  # کش کردن متن راهنما برای 5 دقیقه
async def help_command(message):
    """Display comprehensive help information."""
    # Make sure messages are updated with current language
    Messages.update_messages()
    
    #
    help_text = (
        f"{Language.get_text('help_title')}\n\n"
        f"{Language.get_text('help_intro')}\n\n"
        f"{Language.get_text('help_commands')}\n\n"
        f"{Language.get_text('help_account_management')}\n\n"
        f"{Language.get_text('help_profile_editing')}\n\n"
        f"{Language.get_text('help_security')}\n\n"
        f"{Language.get_text('help_mass_actions')}\n\n"
        f"{Language.get_text('help_interface')}\n\n"
        f"{Language.get_text('help_footer')}"
    )
    
    
    if state.get('main_message_id') and state.get('chat_id') == message.chat.id:

        await safe_execute(
            bot.edit_message_text(
                help_text,
                chat_id=message.chat.id,
                message_id=state['main_message_id'],
                parse_mode="HTML",
                reply_markup=Keyboards.back_home_keyboard()
            )
        )
    else:
        
        sent_message = await safe_execute(
            bot.send_message(
                message.chat.id,
                help_text,
                parse_mode="HTML",
                reply_markup=Keyboards.back_home_keyboard()
            )
        )
        
        if sent_message is None:
            return
        
        state['main_message_id'] = sent_message.message_id
        state['chat_id'] = message.chat.id
        
    # Reset waiting state
    state['waiting_for_input'] = False

def display_startup_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner_text = pyfiglet.figlet_format("VX BOT", font="slant")
    
    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']
    
    for i in range(10):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        for line in banner_text.split('\n'):
            print(colored(line, colors[i % len(colors)]))
        
        # Print the info line
        border = colored('╔' + '═' * 58 + '╗', 'cyan')
        print(border)
        
        info = "BOT STARTED | DEV : VX | TG : @KOXVX | CHANNEL : @L27_0"
        padding = (58 - len(info)) // 2
        info_line = colored('║' + ' ' * padding + info + ' ' * (58 - len(info) - padding) + '║', 'cyan')
        print(info_line)
        
        border_bottom = colored('╚' + '═' * 58 + '╝', 'cyan')
        print(border_bottom)
        
        
        time.sleep(0.1)
    
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    
    lines = banner_text.split('\n')
    for i, line in enumerate(lines):
        print(colored(line, colors[i % len(colors)]))
    
    
    border = colored('┏' + '━' * 58 + '┓', 'cyan')
    print(border)
    
    info = "BOT STARTED | DEV : VX | TG : @KOXVX | CHANNEL : @L27_0"
    padding = (58 - len(info)) // 2
    info_line = colored('┃' + ' ' * padding + colored(info, 'yellow', attrs=['bold']) + ' ' * (58 - len(info) - padding) + '┃', 'cyan')
    print(info_line)
    
    border_bottom = colored('┗' + '━' * 58 + '┛', 'cyan')
    print(border_bottom)
    print("\n")

# Start the bot
async def main():
    try:
        display_startup_banner()
        initialize_data()
        logger.info("Data directory and sessions file initialized")
        
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Operating system: {os.name}")
        logger.info(f"Bot token: {Config.BOT_TOKEN[:8]}...")
        logger.info(f"Data directory: {Config.DATA_DIR}")
        
        try:
            sessions = SessionManager.read_sessions()
            session_count = len(sessions.get('sessions', {}))
            logger.info(f"Found {session_count} existing sessions")
        except Exception as e:
            logger.warning(f"Could not read sessions: {e}")
            session_count = 0
        
        
        await bot.set_my_commands(bot_commands)
        logger.info("Bot commands registered successfully")
        
        
        print(colored("\nBot Information:", 'cyan'))
        print(colored(f"Session count: {session_count}", 'yellow'))
        print(colored(f"Current language: {Language.get_language()}", 'yellow'))
        print(colored("\nBot is now running! Press Ctrl+C to stop.", 'green', attrs=['bold']))
        
        
        await bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error(traceback.format_exc())
        print(colored(f"\nError: {e}", 'red', attrs=['bold']))
        print(colored("Bot stopped due to an error. Check logs for details.", 'red'))
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(colored("\nBot stopped by user.", 'yellow'))
    except Exception as e:
        print(colored(f"\nFatal error: {e}", 'red', attrs=['bold']))
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
