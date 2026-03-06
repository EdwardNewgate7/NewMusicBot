
class Emoji:
    HEADPHONES = "123"

emoji = Emoji()
query = "test"
action_text = "action"
cookie_badge = "cookie"

text=(
    f'<tg-emoji emoji-id="{emoji.HEADPHONES}">🎶</tg-emoji>'
    f" <b>ARANIYOR:</b> <code>{query[:50]}</code>\n\n"
    f"<i>{action_text} {cookie_badge}</i>"
)
print(text)
