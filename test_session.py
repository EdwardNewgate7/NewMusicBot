import asyncio
import os
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_id = int(os.getenv("ASSISTANT_API_ID"))
    api_hash = os.getenv("ASSISTANT_API_HASH")
    session_string = os.getenv("ASSISTANT_STRING_SESSION")
    
    print(f"Testing session string: {session_string[:10]}...")
    
    app = Client(
        name="test_session",
        api_id=api_id,
        api_hash=api_hash,
        session_string=session_string,
        in_memory=True # Use memory so we don't lock database
    )
    
    try:
        await app.start()
        me = await app.get_me()
        print(f"Success! Logged in as: {me.first_name} (@{me.username})")
        await app.stop()
    except Exception as e:
        print(f"Failed to start assistant: {e}")

if __name__ == "__main__":
    asyncio.run(main())
