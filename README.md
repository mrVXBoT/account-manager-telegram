<div align="center">

# 🌟 Telegram Account Manager Bot 🌟

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/KOXVX)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telethon](https://img.shields.io/badge/Telethon-1.24.0-red?style=for-the-badge)](https://github.com/LonamiWebs/Telethon)
[![PyTelegramBotAPI](https://img.shields.io/badge/PyTelegramBotAPI-4.7.0-green?style=for-the-badge)](https://github.com/eternnoir/pyTelegramBotAPI)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Channel](https://img.shields.io/badge/Channel-@L27__0-purple?style=for-the-badge&logo=telegram)](https://t.me/L27_0)


</div>

## 📑 Overview

A sophisticated Telegram bot designed for managing multiple Telegram accounts through an elegant, streamlined interface. This tool stands out with its innovative single-message UI that updates in real-time, eliminating message clutter and providing a seamless user experience.

<div align="center">
<img src="https://raw.githubusercontent.com/mrVXBoT/account-manager-telegram/main/assets/demo.gif" alt="Demo" width="400">
</div>

## ⚡ Key Features

<div align="center">
<img src="https://raw.githubusercontent.com/mrVXBoT/account-manager-telegram/main/assets/features.png" alt="Features" width="500">
</div>

### Account Management
- **Add Multiple Accounts**: Easily add and manage multiple Telegram accounts
- **View Account Details**: See account information including username, first name, and ID
- **Delete Accounts**: Remove accounts you no longer need

### Profile Customization
- **Edit First Name**: Change your account's first name
- **Edit Last Name**: Modify or remove your account's last name
- **Edit Username**: Update your Telegram username
- **Edit Bio**: Customize your profile bio

### Security Features
- **2FA Password Management**: Change or update your Two-Factor Authentication password
- **Session Management**: View and terminate active sessions
- **Secure Storage**: All sensitive data is stored locally with proper encryption

### Mass Actions
- **Bulk Messaging**: Send messages to users with all your accounts simultaneously
- **Channel Joining**: Join Telegram channels with all accounts at once
- **Message Reactions**: Send reactions to messages with all accounts

### User Experience
- **Single-Message Interface**: All interactions happen by editing a single message
- **Clean Navigation**: Intuitive keyboard-based navigation system
- **Real-time Updates**: See changes immediately without message clutter
- **Multi-language Support**: Full support for English and Persian languages
- **Beautiful Symbols**: Enhanced UI with elegant chess and special symbols
- **Performance Optimized**: Efficient caching and asynchronous operations

## 🔧 Technical Specifications


### Dependencies
- **Python 3.9+**: Modern Python features for clean, efficient code
- **Telethon 1.24.0+**: Powerful, pure Python 3 MTProto API Telegram client library
- **PyTelegramBotAPI 4.7.0+**: Simple but extensible Python implementation for the Telegram Bot API
- **Colorama & Termcolor**: For beautiful terminal output and animations
- **Python-dotenv**: For secure environment variable management
- **Asyncio**: For asynchronous programming and concurrent operations

### Architecture
- **State-Based Design**: Maintains conversation state for fluid interactions
- **Asynchronous Operations**: Handles multiple accounts efficiently with non-blocking operations
- **Single-Message Interface**: All interactions happen by editing a single message rather than sending multiple messages
- **Modular Structure**: Organized into logical components:
  - `SessionManager`: Handles secure account sessions storage and retrieval
  - `AccountManager`: Manages account operations and API interactions
  - `Keyboards`: Generates dynamic, context-aware interactive keyboards
  - `Messages`: Stores and retrieves message templates with language support
  - `Language`: Manages multi-language support with efficient caching
- **Performance Optimizations**:
  - Efficient caching system with time-based expiration
  - Rate limiting for API calls to prevent flooding
  - Safe execution wrappers for error resilience
  - Parallel processing for multi-account operations
- **Internationalization**: Complete language switching capability with all UI elements

## 💻 Installation


### Prerequisites

- Python 3.9 or higher
- A Telegram account
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (API ID and API Hash from [my.telegram.org](https://my.telegram.org))

### Step-by-Step Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mrVXBoT/account-manager-telegram.git
   cd account-manager-telegram
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install dependencies manually:
   ```bash
   pip install telethon==1.24.0 pytelegrambotapi==4.7.0 python-dotenv colorama termcolor pyfiglet
   ```

4. **Create configuration files**:
   - Create a `.env` file in the project root with the following content:
     ```
     BOT_TOKEN=your_bot_token_here
     DATA_DIR=data
     ```
   - Create a `data` directory for storing sessions:
     ```bash
     mkdir data
     ```

5. **Run the bot**:
   ```bash
   python VX-acc.py
   ```

### Docker Installation (Alternative)

```bash
# Build the Docker image
docker build -t account-manager-telegram .

# Run the container
docker run -d --name telegram-account-manager \
  -v $(pwd)/data:/app/data \
  -e BOT_TOKEN=your_bot_token_here \
  account-manager-telegram
```

## 🚀 Usage Guide



### Basic Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and display the main menu |
| `/help` | Display comprehensive help information |
| `/eng` | Switch the interface to English |
| `/fa` | Switch the interface to Persian (فارسی) |

### Detailed Usage Instructions

1. **Getting Started**:
   - Start a conversation with your bot by sending `/start`
   - The bot will respond with a welcome message and the main menu
   - **Important**: All interactions happen by editing a single message, creating a clean interface without message clutter

2. **Language Selection**:
   - Use `/eng` command to switch to English
   - Use `/fa` command to switch to Persian (فارسی)
   - All UI elements will update instantly to the selected language

3. **Adding an Account**:
   - Click "Add Account" (or "افزودن حساب" in Persian)
   - Enter your API hash when prompted
   - Enter your API ID when prompted
   - Enter your phone number with country code (e.g., +12345678901)
   - Enter the verification code sent to your Telegram app
   - If 2FA is enabled, enter your password when prompted

4. **Managing Accounts**:
   - Click "Show Accounts" to see all added accounts
   - Each account will display its ID, name, and action buttons
   - Select an account to view details and management options
   - Use the delete button to remove an account

5. **Editing Profiles**:
   - Select an account and click "Edit Profile"
   - Choose what you want to edit:
     - First name: Enter a new first name
     - Last name: Enter a new last name or leave empty to remove
     - Username: Enter a new username without the @ symbol
     - Bio: Enter a new biography text

6. **Using Mass Actions**:
   - From the main menu, select the desired tool:
     - "Send Message": Enter the username/ID and message to send with all accounts
     - "Join Channel": Enter the channel username or invite link to join with all accounts
     - "Send Reaction": Enter the message link and select a reaction to send with all accounts

7. **Session Management**:
   - Click "Manage Sessions" to view and control active sessions
   - View detailed information about each session (device, platform, IP, location)
   - Terminate individual sessions or all other sessions at once
   - Monitor for suspicious sessions and terminate them for security

8. **2FA Password Management**:
   - Select an account and click "Change 2FA"
   - Follow the prompts to set or change your Two-Factor Authentication password

### Tips for Optimal Use

- **Single-Message Interface**: The bot uses a single-message interface that updates in real-time. No need to scroll through multiple messages.
- **Back Button**: Always use the back button to navigate to previous menus rather than sending new commands.
- **Session Security**: Regularly check active sessions and terminate any suspicious ones.
- **Language Switching**: You can switch languages at any time using the `/eng` or `/fa` commands.

## 🔐 Security Considerations


- **Local Storage**: All data is stored locally on your device, not on external servers
- **Session Protection**: Session strings are stored with proper encryption
- **API Credentials**: Your API ID and hash are stored securely using environment variables
- **Privacy**: The bot doesn't share any data with third parties or collect analytics
- **Session Management**: Advanced tools to monitor and terminate suspicious sessions
- **2FA Support**: Full support for Two-Factor Authentication
- **Error Handling**: Robust error handling to prevent unexpected behavior

## 💬 Support & Contribution

- **Issues**: Report bugs or request features through [GitHub Issues](https://github.com/mrVXBoT/account-manager-telegram/issues)
- **Contributions**: Pull requests are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md)
- **Contact**: Reach out to [@KOXVX](https://t.me/KOXVX) on Telegram for direct support
- **Updates**: Follow [@L27_0](https://t.me/L27_0) for updates and announcements

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal use only. Always comply with [Telegram's Terms of Service](https://telegram.org/tos) when using this bot. The developers are not responsible for any misuse or violations. Using automation tools like this may violate Telegram's terms in some cases, especially if used for spam or abuse. Use responsibly and at your own risk.

---

<div align="center">
  <p>Developed with ❤️ by <a href="https://t.me/KOXVX">VX</a> for the Telegram community</p>
  <p>© 2025 | <a href="https://t.me/L27_0">@L27_0</a></p>
</div>
