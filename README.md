# account-manager-telegram
# Telegram Account Manager Bot

<div align="center">
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9">
  <img src="https://img.shields.io/badge/Telethon-1.24.0-red?style=for-the-badge" alt="Telethon">
</div>

## 📑 Overview

A sophisticated Telegram bot designed for managing multiple Telegram accounts through an elegant, streamlined interface. This tool stands out with its innovative single-message UI that updates in real-time, eliminating message clutter and providing a seamless user experience.

## ⚡ Key Features

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

### Mass Actions
- **Bulk Messaging**: Send messages to users with all your accounts simultaneously
- **Channel Joining**: Join Telegram channels with all accounts at once
- **Message Reactions**: Send reactions to messages with all accounts

### User Experience
- **Single-Message Interface**: All interactions happen by editing a single message
- **Clean Navigation**: Intuitive keyboard-based navigation system
- **Real-time Updates**: See changes immediately without message clutter

## 🔧 Technical Specifications

### Dependencies
- **Python 3.9+**
- **Telethon**: For Telegram client functionality
- **AsyncTeleBot**: For the bot interface
- **JSON**: For session storage and management

### Architecture
- **State-Based Design**: Maintains conversation state for fluid interactions
- **Asynchronous Operations**: Handles multiple accounts efficiently
- **Modular Structure**: Organized into logical components:
  - `SessionManager`: Handles account sessions
  - `AccountManager`: Manages account operations
  - `Keyboards`: Generates interactive keyboards
  - `Messages`: Stores message templates

## 💻 Installation

1. Ensure you have Python 3.9 or higher installed

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-account-manager.git
   cd telegram-account-manager
   ```

3. Install required packages:
   ```bash
   pip install telethon==1.24.0 pytelegrambotapi==4.7.0
   ```

4. Create a `data` directory for storing sessions:
   ```bash
   mkdir data
   ```

5. Configure the bot by editing the `Config` class in `acc_new.py`:
   - Add your Telegram bot token
   - Set appropriate paths for session storage

6. Run the bot:
   ```bash
   python acc_new.py
   ```

## 🚀 Usage Guide

1. Start a conversation with your bot by sending `/start`

2. **Adding an Account**:
   - Click "Add Account"
   - Enter your API hash, API ID, and phone number
   - Complete the verification process

3. **Managing Accounts**:
   - Click "Show Accounts" to see all added accounts
   - Select an account to view details and management options

4. **Editing Profiles**:
   - Select an account and click "Edit Profile"
   - Choose what you want to edit (first name, last name, username, bio)

5. **Using Mass Actions**:
   - From the main menu, select the desired tool:
     - "Send Message" to message users with all accounts
     - "Join Channel" to join a channel with all accounts
     - "Send Reaction" to react to messages with all accounts

## 🔐 Security Considerations

- **Session Protection**: Session strings are stored locally and encrypted
- **API Credentials**: Your API ID and hash are stored securely
- **Privacy**: The bot doesn't share any data with third parties
- **Session Management**: Regularly check and terminate unknown sessions

## ⚠️ Disclaimer

This tool is for personal use only. Always comply with Telegram's Terms of Service when using this bot. The developers are not responsible for any misuse or violations.

---

<div align="center">
  <p>Developed with ❤️ for the Telegram community</p>
</div>
