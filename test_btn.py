from aiogram.types import InlineKeyboardButton
try:
    btn = InlineKeyboardButton(text="test", callback_data="test", style="primary", icon_custom_emoji_id="123")
    print("SUCCESS: InlineKeyboardButton accepts style and icon_custom_emoji_id")
except TypeError as e:
    print(f"FAILED: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
