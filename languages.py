#!/usr/bin/env python3
"""
Language support module for Telegram Account Manager Bot
Developed by VX (@KOXVX)
"""

class Language:
    """Base language class with language switching functionality"""
    
    _current_language = "en"
    _cache = {}
    
    @classmethod
    def set_language(cls, lang_code):
        """Set the current language"""
        
        if lang_code in ["en", "fa"]:
            cls._current_language = lang_code
            cls._cache = {}
            return True
        return False
        
    @classmethod
    def get_language(cls):
        """Get the current language code"""
        
        return cls._current_language
    
    @classmethod
    def get_text(cls, key):
        """Get text for the current language with caching"""
        
        cache_key = f"{cls._current_language}:{key}"
        
        
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        
        if cls._current_language == "en":
            text = EnglishText.get(key)
        else:
            text = PersianText.get(key)
        
        
        cls._cache[cache_key] = text
        
        return text


class EnglishText:
    """English text for the bot"""
    
    
    TEXTS = {
        
        "welcome": "๑۞๑ Welcome to the Telegram Account Manager Bot! ๑۞๑\n\n╠═══ Please select an option below ═══╣",
        "show_accounts": "╔═══『 All Accounts 』═══╗\n\n╠═ Select an account to view or edit ═╣",
        "add_account": "♠♣♥♦ Let's add a new Telegram account ♠♣♥♦\n\n╔════ Please follow the steps below ════╗",
        
        
        "api_hash_prompt": "▓▒░ Please enter your API hash ░▒▓",
        "api_id_prompt": "▓▒░ Please enter your API ID ░▒▓",
        "phone_prompt": "▓▒░ Please enter your phone number (with country code) ░▒▓",
        "code_prompt": "▓▒░ Please enter the verification code sent to your Telegram app ░▒▓",
        "password_prompt": "▓▒░ Please enter your Two-Factor Authentication password ░▒▓",
        "account_added": "★彡 Account added successfully! 彡★",
        
        
        "account_details": "📱 **Account Details**\n\n**ID:** {id}\n**First Name:** {first_name}\n**Last Name:** {last_name}\n**Username:** {username}\n**Phone:** {phone}\n**Bio:** {bio}\n**Profile Photo:** {has_photo}\n**Premium:** {premium}\n**Verified:** {verified}\n**Restricted:** {restricted}\n**Active Sessions:** {sessions_count}\n**2FA Enabled:** {has_2fa}",
        
        
        "edit_first_name_prompt": "▓▒░ Please enter the new first name for your account ░▒▓",
        "edit_last_name_prompt": "▓▒░ Please enter the new last name for your account (or 'none' to remove it) ░▒▓",
        "edit_username_prompt": "▓▒░ Please enter the new username for your account ░▒▓",
        "edit_bio_prompt": "▓▒░ Please enter the new bio for your account (or 'none' to remove it) ░▒▓",
        
        
        "current_2fa_prompt": "▓▒░ Please enter your current 2FA password ░▒▓",
        "new_2fa_prompt": "▓▒░ Please enter your new 2FA password ░▒▓",
        
        
        "message_username_prompt": "▓▒░ Please enter the username of the user you want to message ░▒▓",
        "message_content_prompt": "▓▒░ Please enter the message content ░▒▓",
        "join_channel_prompt": "▓▒░ Please enter the username of the channel you want to join ░▒▓",
        "reaction_prompt": "▓▒░ Please enter the link to the message you want to react to ░▒▓",
        
        
        "session_management": "☸ Session Management ☸",
        "fetching_sessions": "⌛ Fetching active sessions, please wait... ⌛",
        "terminating_sessions": "⏳ Terminating sessions, please wait... ⏳",
        "all_sessions_terminated": "✓ All other sessions terminated successfully! ✓",
        "failed_terminate_sessions": "✗ Failed to terminate sessions ✗",
        "session_terminated": "✓ Session terminated successfully! ✓",
        "active_sessions_header": "<b>⚙ Active Sessions</b>\n\n",
        "no_sessions": "⚠ No active sessions found.",
        "session_number": "<b>⚡ Session #{number}</b> {current_marker}",
        "current_session": "⚜ <b>CURRENT</b> ",
        "device": "⌨ <b>Device:</b> {device_model}",
        "platform": "⚒ <b>Platform:</b> {platform} {system_version}",
        "app": "⚓ <b>App:</b> {app_name} {app_version}",
        "created": "⏰ <b>Created:</b> {date_created}",
        "last_active": "⏱ <b>Last Active:</b> {date_active}",
        "ip": "⚔ <b>IP:</b> {ip}",
        "location": "⚑ <b>Location:</b> {country}, {region}",
        "official_app": "⚕ <b>Official App</b>",
        "password_pending": "⚠ <b>Password Pending</b>",
        "session_id": "<code>⚛ Session ID: {hash}</code>",
        "terminate_session": "⚡ Terminate Session #{number}",
        "terminate_all_sessions": "☢ Terminate All Other Sessions ☢",
        "view_active_sessions": "☣ View Active Sessions ☣",
        "back": "╠═══ BACK ← ═══╣",
        
        
        "manager_title": "♔ Manager ♔",
        "add_account": "♚ Add Account ♚",
        "show_accounts": "♛ Show Accounts ♛",
        "account_tools": "♜ Account Tools ♜",
        "send_message": "♝ Send Message ♝",
        "join_channel": "♞ Join Channel ♞",
        "send_reaction": "♟ Send Reaction ♟",
        "edit_profile": "♕ Edit Profile ♕",
        "change_2fa": "♖ Change 2FA ♖",
        "edit_first_name": "♗ First Name ♗",
        "edit_last_name": "♘ Last Name ♘",
        "edit_username": "♙ Username ♙",
        "edit_bio": "♙ Bio ♙",
        "manage_sessions": "☠ Manage Sessions ☠",
        "set_change_password": "☯ Set/Change Password ☯",
        "id_header": "☢ ID ☢",
        "name_header": "☣ NAME ☣",
        "view_header": "☤ VIEW ☤",
        "delete_header": "☥ DELETE ☥",
        "view_button": "☛",
        "delete_button": "☒",
        "no_accounts": "ⓃⓉ Ⓐ⒲⒲ⓉⓊⓃⓄⓈ",
        "back_button": "☜ BACK ☜",
        
        
        "language_changed": "Language changed to English!",
        
        
        "help_title": "📚 Telegram Account Manager Bot - Help Guide 📚",
        "help_intro": "Welcome to the Telegram Account Manager Bot! This bot allows you to manage multiple Telegram accounts through a clean, single-message interface.\n\nHere's how to use all the features:",
        "help_commands": "📋 <b>Bot Commands</b>\n\n/start - Start the bot and show the main menu\n/help - Show this help message\n/eng - Switch to English language\n/fa - Switch to Persian language",
        "help_account_management": "👤 <b>Account Management</b>\n\n• <b>Add Account</b>: Add a new Telegram account by providing API credentials and phone verification\n• <b>Show Accounts</b>: View and manage all your added accounts\n• <b>Delete Account</b>: Remove an account you no longer need",
        "help_profile_editing": "✏️ <b>Profile Customization</b>\n\n• <b>Edit First Name</b>: Change your account's first name\n• <b>Edit Last Name</b>: Modify or remove your account's last name\n• <b>Edit Username</b>: Update your Telegram username\n• <b>Edit Bio</b>: Customize your profile bio",
        "help_security": "🔐 <b>Security Features</b>\n\n• <b>Change 2FA Password</b>: Update your Two-Factor Authentication password\n• <b>Manage Sessions</b>: View and terminate active sessions\n• <b>View Active Sessions</b>: See detailed information about all active sessions\n• <b>Terminate Sessions</b>: End specific or all other sessions",
        "help_mass_actions": "🔄 <b>Mass Actions</b>\n\n• <b>Send Message</b>: Send messages to users with all accounts simultaneously\n• <b>Join Channel</b>: Join Telegram channels with all accounts at once\n• <b>Send Reaction</b>: Send reactions to messages with all accounts",
        "help_interface": "🖥️ <b>User Interface</b>\n\n• <b>Single-Message Interface</b>: All interactions happen by editing a single message\n• <b>Navigation</b>: Use the provided buttons to navigate through different menus\n• <b>Back Button</b>: Return to the previous menu at any time",
        "help_footer": "For any issues or questions, please contact the bot administrator.",
    }
    
    @classmethod
    def get(cls, key):
        """Get English text by key"""
        return cls.TEXTS.get(key, f"Missing text: {key}")


class PersianText:
    """Persian text for the bot"""
    
    
    TEXTS = {
        
        "welcome": "๑۞๑ به ربات مدیریت حساب تلگرام خوش آمدید! ๑۞๑\n\n╠═══ لطفاً یک گزینه را انتخاب کنید ═══╣",
        "show_accounts": "╔═══『 همه حساب‌ها 』═══╗\n\n╠═ یک حساب را برای مشاهده یا ویرایش انتخاب کنید ═╣",
        "add_account": "♠♣♥♦ بیایید یک حساب تلگرام جدید اضافه کنیم ♠♣♥♦\n\n╔════ لطفاً مراحل زیر را دنبال کنید ════╗",
        
        
        "api_hash_prompt": "▓▒░ لطفاً API hash خود را وارد کنید ░▒▓",
        "api_id_prompt": "▓▒░ لطفاً API ID خود را وارد کنید ░▒▓",
        "phone_prompt": "▓▒░ لطفاً شماره تلفن خود را (با کد کشور) وارد کنید ░▒▓",
        "code_prompt": "▓▒░ لطفاً کد تأیید ارسال شده به برنامه تلگرام خود را وارد کنید ░▒▓",
        "password_prompt": "▓▒░ لطفاً رمز عبور احراز هویت دو مرحله‌ای خود را وارد کنید ░▒▓",
        "account_added": "★彡 حساب با موفقیت اضافه شد! 彡★",
        
        
        "account_details": "📱 **جزئیات حساب**\n\n**شناسه:** {id}\n**نام:** {first_name}\n**نام خانوادگی:** {last_name}\n**نام کاربری:** {username}\n**تلفن:** {phone}\n**بیو:** {bio}\n**عکس پروفایل:** {has_photo}\n**پریمیوم:** {premium}\n**تأیید شده:** {verified}\n**محدود شده:** {restricted}\n**جلسات فعال:** {sessions_count}\n**احراز هویت دو مرحله‌ای فعال:** {has_2fa}",
        
        
        "edit_first_name_prompt": "▓▒░ لطفاً نام جدید برای حساب خود را وارد کنید ░▒▓",
        "edit_last_name_prompt": "▓▒░ لطفاً نام خانوادگی جدید برای حساب خود را وارد کنید (یا 'none' برای حذف آن) ░▒▓",
        "edit_username_prompt": "▓▒░ لطفاً نام کاربری جدید برای حساب خود را وارد کنید ░▒▓",
        "edit_bio_prompt": "▓▒░ لطفاً بیوگرافی جدید برای حساب خود را وارد کنید (یا 'none' برای حذف آن) ░▒▓",
        
        
        "current_2fa_prompt": "▓▒░ لطفاً رمز عبور احراز هویت دو مرحله‌ای فعلی خود را وارد کنید ░▒▓",
        "new_2fa_prompt": "▓▒░ لطفاً رمز عبور احراز هویت دو مرحله‌ای جدید خود را وارد کنید ░▒▓",
        
        
        "message_username_prompt": "▓▒░ لطفاً نام کاربری شخصی که می‌خواهید به او پیام دهید را وارد کنید ░▒▓",
        "message_content_prompt": "▓▒░ لطفاً محتوای پیام را وارد کنید ░▒▓",
        "join_channel_prompt": "▓▒░ لطفاً نام کاربری کانالی که می‌خواهید به آن بپیوندید را وارد کنید ░▒▓",
        "reaction_prompt": "▓▒░ لطفاً لینک پیامی که می‌خواهید به آن واکنش دهید را وارد کنید ░▒▓",
        
        # Session management
        "session_management": "☸ مدیریت جلسات ☸",
        "fetching_sessions": "⌛ در حال دریافت جلسات فعال، لطفاً صبر کنید... ⌛",
        "terminating_sessions": "⏳ در حال خاتمه دادن به جلسات، لطفاً صبر کنید... ⏳",
        "all_sessions_terminated": "✓ تمام جلسات دیگر با موفقیت خاتمه یافتند! ✓",
        "failed_terminate_sessions": "✗ خاتمه دادن به جلسات ناموفق بود ✗",
        "session_terminated": "✓ جلسه با موفقیت خاتمه یافت! ✓",
        "active_sessions_header": "<b>⚙ جلسات فعال</b>\n\n",
        "no_sessions": "⚠ هیچ جلسه فعالی یافت نشد.",
        "session_number": "<b>⚡ جلسه #{number}</b> {current_marker}",
        "current_session": "⚜ <b>جلسه فعلی</b> ",
        "device": "⌨ <b>دستگاه:</b> {device_model}",
        "platform": "⚒ <b>پلتفرم:</b> {platform} {system_version}",
        "app": "⚓ <b>برنامه:</b> {app_name} {app_version}",
        "created": "⏰ <b>ایجاد شده:</b> {date_created}",
        "last_active": "⏱ <b>آخرین فعالیت:</b> {date_active}",
        "ip": "⚔ <b>آی‌پی:</b> {ip}",
        "location": "⚑ <b>موقعیت:</b> {country}, {region}",
        "official_app": "⚕ <b>برنامه رسمی</b>",
        "password_pending": "⚠ <b>رمز عبور در انتظار</b>",
        "session_id": "<code>⚛ شناسه جلسه: {hash}</code>",
        "terminate_session": "⚡ خاتمه دادن به جلسه #{number}",
        "terminate_all_sessions": "☢ خاتمه دادن به تمام جلسات دیگر ☢",
        "view_active_sessions": "☣ مشاهده جلسات فعال ☣",
        "back": "╠═══ بازگشت ← ═══╣",
        
        
        "manager_title": "♔ مدیریت ♔",
        "add_account": "♚ افزودن حساب ♚",
        "show_accounts": "♛ نمایش حساب‌ها ♛",
        "account_tools": "♜ ابزارهای حساب ♜",
        "send_message": "♝ ارسال پیام ♝",
        "join_channel": "♞ عضویت در کانال ♞",
        "send_reaction": "♟ ارسال واکنش ♟",
        "edit_profile": "♕ ویرایش پروفایل ♕",
        "change_2fa": "♖ تغییر احراز هویت دو مرحله‌ای ♖",
        "edit_first_name": "♗ نام ♗",
        "edit_last_name": "♘ نام خانوادگی ♘",
        "edit_username": "♙ نام کاربری ♙",
        "edit_bio": "♙ بیو ♙",
        "manage_sessions": "☠ مدیریت جلسات ☠",
        "set_change_password": "☯ تنظیم/تغییر رمز عبور ☯",
        "id_header": "☢ شناسه ☢",
        "name_header": "☣ نام ☣",
        "view_header": "☤ مشاهده ☤",
        "delete_header": "☥ حذف ☥",
        "view_button": "☛",
        "delete_button": "☒",
        "no_accounts": "هیچ حسابی وجود ندارد",
        "back_button": "☜ بازگشت ☜",
        
        
        "language_changed": "زبان به فارسی تغییر کرد!",
        
        
        "help_title": "📚 راهنمای ربات مدیریت حساب تلگرام 📚",
        "help_intro": "به ربات مدیریت حساب تلگرام خوش آمدید! این ربات به شما امکان می‌دهد چندین حساب تلگرام را از طریق یک رابط تک پیامی تمیز مدیریت کنید.\n\nنحوه استفاده از تمام ویژگی‌ها:",
        "help_commands": "📋 <b>دستورات ربات</b>\n\n/start - شروع ربات و نمایش منوی اصلی\n/help - نمایش این پیام راهنما\n/eng - تغییر زبان به انگلیسی\n/fa - تغییر زبان به فارسی",
        "help_account_management": "👤 <b>مدیریت حساب</b>\n\n• <b>افزودن حساب</b>: افزودن یک حساب تلگرام جدید با ارائه اعتبارنامه‌های API و تأیید تلفن\n• <b>نمایش حساب‌ها</b>: مشاهده و مدیریت تمام حساب‌های اضافه شده\n• <b>حذف حساب</b>: حذف حسابی که دیگر به آن نیاز ندارید",
        "help_profile_editing": "✏️ <b>سفارشی‌سازی پروفایل</b>\n\n• <b>ویرایش نام</b>: تغییر نام حساب خود\n• <b>ویرایش نام خانوادگی</b>: تغییر یا حذف نام خانوادگی حساب خود\n• <b>ویرایش نام کاربری</b>: به‌روزرسانی نام کاربری تلگرام خود\n• <b>ویرایش بیو</b>: سفارشی‌سازی بیوگرافی پروفایل خود",
        "help_security": "🔐 <b>ویژگی‌های امنیتی</b>\n\n• <b>تغییر رمز عبور احراز هویت دو مرحله‌ای</b>: به‌روزرسانی رمز عبور احراز هویت دو مرحله‌ای خود\n• <b>مدیریت جلسات</b>: مشاهده و خاتمه دادن به جلسات فعال\n• <b>مشاهده جلسات فعال</b>: مشاهده اطلاعات دقیق درباره تمام جلسات فعال\n• <b>خاتمه دادن به جلسات</b>: پایان دادن به جلسات خاص یا تمام جلسات دیگر",
        "help_mass_actions": "🔄 <b>اقدامات گروهی</b>\n\n• <b>ارسال پیام</b>: ارسال پیام به کاربران با تمام حساب‌ها به طور همزمان\n• <b>پیوستن به کانال</b>: پیوستن به کانال‌های تلگرام با تمام حساب‌ها به طور همزمان\n• <b>ارسال واکنش</b>: ارسال واکنش به پیام‌ها با تمام حساب‌ها",
        "help_interface": "🖥️ <b>رابط کاربری</b>\n\n• <b>رابط تک پیامی</b>: تمام تعاملات با ویرایش یک پیام واحد انجام می‌شود\n• <b>ناوبری</b>: از دکمه‌های ارائه شده برای حرکت بین منوهای مختلف استفاده کنید\n• <b>دکمه بازگشت</b>: در هر زمان به منوی قبلی بازگردید",
        "help_footer": "برای هرگونه مشکل یا سؤال، لطفاً با مدیر ربات تماس بگیرید.",
    }
    
    @classmethod
    def get(cls, key):
        """Get Persian text by key"""
        return cls.TEXTS.get(key, f"متن یافت نشد: {key}")
