"""
╔══════════════════════════════════════════════════════════════╗
║        🎵 HARMONY MUSIC - ASİSTAN OTURUM OLUŞTURUCU        ║
║   (Voice Chat / Sesli Sohbet yayını için String Session al)  ║
╚══════════════════════════════════════════════════════════════╝

Açıklama:
Bu betik, botunuzun sesli sohbetlere katılıp müzik yayını yapabilmesi için
gereken Asistan Hesabı'nın (Pyrogram) "String Session" anahtarını üretir.

Kullanım:
1) my.telegram.org adresinden API_ID ve API_HASH bilgilerinizi alın.
2) config.py veya .env.example (ya da .env) dosyanıza bu bilgileri girin.
3) Bu dosyayı çalıştırın: `python generate_session.py`
4) Çıkan uzun string kodunu (String Session) .env dosyanızdaki
   ASSISTANT_STRING_SESSION= karşısına kopyalayın.

Not: Pyrogram paketine ihtiyaç duyar! Yüklü değilse:
`pip install pyrogram tgcrypto` komutunu çalıştırın.
"""

import asyncio
import os
import sys

try:
    from pyrogram import Client
except ImportError:
    print("\n❌ Pyrogram kütüphanesi bulunamadı!")
    print("👉 Lütfen yükleyin: pip install pyrogram tgcrypto\n")
    sys.exit(1)

# .env'den okuma
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def main() -> None:
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("    🌟 HARMONY MUSIC - PYROGRAM SESSION OLUŞTURUCU  ")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # API Bilgilerini Al
    env_api_id = os.getenv("ASSISTANT_API_ID", "")
    env_api_hash = os.getenv("ASSISTANT_API_HASH", "")

    print("ℹ️ Çıkış yapmak için CTRL+C yapabilirsiniz.\n")

    if env_api_id and env_api_id != "0":
        user_api_id = env_api_id
        print(f"📦 .env dosyasından API_ID algılandı: {user_api_id}")
    else:
        user_api_id = input("1) my.telegram.org API_ID değerini girin: ").strip()

    if env_api_hash:
        user_api_hash = env_api_hash
        print(f"📦 .env dosyasından API_HASH algılandı: {user_api_hash}")
    else:
        user_api_hash = input("2) my.telegram.org API_HASH değerini girin: ").strip()

    if not user_api_id.isdigit():
        print("❌ HATA: API ID sadece rakamlardan oluşmalıdır.")
        return

    print("\n⏳ Telfon numarası, kod ve şifre(varsa) için hazırlanıyor...\n")

    client = Client(
        name=":memory:",
        api_id=int(user_api_id),
        api_hash=user_api_hash,
        in_memory=True
    )

    await client.start()
    
    session_string = await client.export_session_string()
    
    print("\n" + "═" * 50)
    print("✅ BAŞARIYLA GİRİŞ YAPILDI! ✅")
    print("Aşağıdaki sizin ASSISTANT_STRING_SESSION anahtarınızdır.\nÇOK ÖNEMLİ: Bu metni kimseyle paylaşmayın!\n")
    print(session_string)
    print("═" * 50 + "\n")
    print("👉 Kopyaladığınız string'i .env dosyanızdaki ASSISTANT_STRING_SESSION= kısmına yapıştırın.")
    print("👉 Daha sonra ASSISTANT_ENABLED=true yaparak botu başlatın.\n")

    await client.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 İşlem kullanıcı tarafından iptal edildi.")
    except Exception as e:
        print(f"\n❌ Bir hata oluştu: {e}")
