"""
╔══════════════════════════════════════════════════════════════╗
║       🎵 Harmony Music - Mesaj Metinleri v3.0             ║
║       Botun gönderdiği tüm mesajların HTML formatı          ║
╚══════════════════════════════════════════════════════════════╝
"""

from utils.emoji_ids import emoji


def start_text(user_first_name: str) -> str:
    """Kullanıcıya gönderilecek /start karşılama mesajı."""
    return (
        f'<tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji> <b>MERHABA {user_first_name}!</b> <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        f'<tg-emoji emoji-id="{emoji.ID_AUDIO_BARS}">📶</tg-emoji> <b>BEN HARMONY MÜZİK BOTU</b>, TELEGRAM\'IN EN GÜÇLÜ VE HIZLI MÜZİK ASİSTANIYIM! <tg-emoji emoji-id="{emoji.ID_NOTES}">🎶</tg-emoji>\n\n'
        f'<tg-emoji emoji-id="{emoji.ID_LIGHTNING}">⚡</tg-emoji> <b>BENİ GRUBUNA EKLE VE RİTMİ HİSSET!</b> <tg-emoji emoji-id="{emoji.ID_EXPLOSION}">💥</tg-emoji>\n\n'
        f'<tg-emoji emoji-id="{emoji.ID_RINGS}">🌀</tg-emoji> <i>Aşağıdaki butonlardan tüm komutları görebilirsin.</i> <tg-emoji emoji-id="{emoji.ID_DOTS}">🟢</tg-emoji>'
    )


def commands_main_text() -> str:
    """Komut kategorileri ana menüsü."""
    return (
        f'<tg-emoji emoji-id="{emoji.ID_RINGS}">🌀</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>KOMUT KATEGORİLERİ:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "<b>LÜTFEN BİLGİ ALMAK İSTEDİĞİNİZ KATEGORİYİ SEÇİN:</b>"
    )


def music_play_commands_text() -> str:
    """Müzik oynatma komutları açıklama metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.CMD_PLAY}">📶</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>MÜZİK OYNATMA KOMUTLARI:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "• <b>/oynat</b> [ŞARKIVİDEO/YANITLA]\n"
        "├ ŞARKIYI OYNATIR,\n"
        "├ YANITLADIĞINIZ VİDEONUN SESİNİ OYNATIR\n"
        "└ YANITLADIĞINIZ SESLİ MESAJI OYNATIR.\n\n"
        "• <b>/voynat</b> [VİDEO/YANITLA]\n"
        "├ YAZDIĞINIZ VİDEOYU OYNATIR.\n"
        "└ YANITLADIĞINIZ VİDEOYU OYNATIR.\n\n"
        "• <b>/poynat</b>\n"
        "├ KİŞİSEL ÇALMA LİSTENİ ÇALAR;\n"
        "├ SIRAYI SEN SEÇ,\n"
        "├ SIRAYLA ÇAL,\n"
        "└ KARIŞIK ÇAL.\n\n"
        "• <b>/dinle</b>\n"
        "├ GELİŞMİŞ MİNİ OYNATICIYI AÇAR;\n"
        "├ KESİNTİSİZ ŞARKI ÇALMA,\n"
        "├ ÇALMA LİSTESİNİ KONTROL ET,\n"
        "├ ÇALMA LİSTENİ OYNAT,\n"
        "├ ÇALMA LİSTENİ KARIŞIK ÇAL,\n"
        "├ ÇALAN ŞARKIYI TEKRARLA,\n"
        "├ ŞARKI DİNLEME ODALARI,\n"
        "├ AKTİF GRUPLARI GÖRÜNTÜLE,\n"
        "├ ŞARKI SÖZLERİ BUL,\n"
        "└ DİNLEDİĞİN ŞARKIYI PAYLAŞ,"
    )


def control_commands_text() -> str:
    """Kontrol komutları açıklama metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.CMD_CONTROL}">🌀</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>KONTROL KOMUTLARI (YÖNETİCİLER):</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "• <b>/ayarlar</b>\n"
        "├ SESLİ KORUMA, HOŞGELDİN MESAJI,\n"
        "├ SIRA BİLDİRİM, KAPAK FOTOĞRAFI,\n"
        "├ ETİKETLEME, OYNATMA YETKİSİ,\n"
        "└ VE TEMİZLİK MODU AYARLARI.\n\n"
        "• <b>/zamanla</b>\n"
        "├ SÜRE BİTİNCE SESLİ KAPATILSIN MI SEÇ,\n"
        "└ DURDURMA SÜRESİNİ BELİRLE.\n\n"
        "• <b>/durdur</b> - ÇALANI DURAKLATIR.\n"
        "• <b>/devam</b> - DEVAM ETTİRİR.\n"
        "• <b>/atla</b> - SIRADAKİ ŞARKIYA GEÇER.\n"
        "• <b>/sira</b> - KUYRUĞU GÖRÜNTÜLE VE ŞARKI SİL.\n"
        "• <b>/ileri</b> [SN] - ŞARKIYI İLERİ SARAR.\n"
        "• <b>/geri</b> [SN] - ŞARKIYI GERİ SARAR.\n\n"
        "• <b>/son</b> VEYA <b>/bitir</b>\n"
        "└ AKTİF MÜZİĞİ, ETİKETLEME İŞLEMİNİ VEYA YARIŞMAYI ANINDA SONLANDIRIR."
    )


def playlist_commands_text() -> str:
    """Çalma listesi komutları açıklama metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.CMD_PLAYLIST}">💿</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>PLAYLİST KOMUTLARI:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "• <b>/ekle</b> [ŞARKI ADI] - LİSTENE ŞARKI EKLER.\n"
        "• <b>/cikar</b> [ŞARKI/NO] - LİSTENDEN ŞARKI SİLER.\n"
        "• <b>/playlist</b> - LİSTENİZİ YÖNETİR.\n"
        "• <b>/listemisil</b> - LİSTENİ TAMAMEN SİLER."
    )


def other_commands_text() -> str:
    """Diğer komutlar açıklama metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.CMD_OTHER}">📊</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>DİĞER KOMUTLAR:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "• <b>/bul</b> [SÖZ/VİDEO]\n"
        "├ YAZDIĞINIZ SÖZLERDEN ŞARKIYI BULUR,\n"
        "├ YANITLADIĞINIZ VİDEODAKİ MÜZİĞİ BULUR,\n"
        "├ MAKSİMUM 10MB VİDEO DESTEKLENİR,\n"
        "├ BULUNAN ŞARKIYI YOUTUBE'DA İZLE,\n"
        "└ İSTERSEN DİREKT OYNAT.\n\n"
        "• <b>/oneri</b>\n"
        "├ TREND LİSTESİNİ GÖRÜNTÜLE,\n"
        "├ İSTEDİKLERİNE TIKLAYIP İŞARETLE,\n"
        "└ SEÇİLENLERİ OYNAT VE DİNLE.\n\n"
        "• <b>/yarisma</b>\n"
        "├ ŞARKI DİLİ SEÇ (TÜRKÇE, İNGİLİZCE),\n"
        "├ TÜRÜ SEÇ (ARABESK, POP VB.),\n"
        "├ BOT 20SN MÜZİK KESİTLERİ ATACAK,\n"
        "└ İSİMLERİNİ BİL VE PUAN KAZAN.\n\n"
        "• <b>/hediye</b>\n"
        "├ ALICI İD VEYA KULLANICI ADI GİR,\n"
        "├ İSMİN GÖRÜNSÜN MÜ SEÇ,\n"
        "└ ŞARKI ADINI YAZ VE GÖNDER.\n\n"
        "• <b>/ruhesi</b> [YANITLA]\n"
        "├ YANITLADIĞIN KİŞİYLE EŞLEŞ,\n"
        "├ EŞİN HANGİ ŞARKIYI DİNLİYOR GÖR,\n"
        "├ HANGİ GRUPTA DİNLİYOR ÖĞREN,\n"
        "└ ŞARKI AÇTIĞINDA BİLGİ AL.\n\n"
        "• <b>/ayril</b> - MEVCUT RUH EŞİNİZDEN AYRILIN.\n"
        "• <b>/stat</b> - DİNLEME İSTATİSTİKLERİNİZİ ALIN.\n"
        "• <b>/kart</b> - İSTATİSTİK KARTINIZI ALIN.\n\n"
        "• <b>/son</b> VEYA <b>/bitir</b>\n"
        "└ AKTİF YARIŞMAYI, MÜZİĞİ VEYA ETİKETLEME İŞLEMİNİ "
        "ANINDA SONLANDIRIR."
    )


def tagging_commands_text() -> str:
    """Etiketleme komutları açıklama metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.TAG}">📢</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>ETİKETLEME KOMUTLARI:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "• <b>/tag</b> [MESAJ/YANITLA]\n"
        "├ TÜM GRUP ÜYELERİNİ ETİKETLER,\n"
        "├ İSTER METİN YAZARAK BAŞLAT,\n"
        "└ İSTER BİR MESAJA YANIT VER.\n\n"
        "• <b>/atag</b> [MESAJ/YANITLA]\n"
        "└ SADECE YÖNETİCİLERİ ETİKETLER.\n\n"
        "• <b>/davet</b>\n"
        "├ OYNATMA SIRASINDA KULLANILIR,\n"
        "├ MÜZİK ÇALIYORSA DİNLEMEYE,\n"
        "├ VİDEO OYNUYORSA İZLEMEYE ÇAĞIRIR,\n"
        "└ KİŞİLERİ ETİKETLER.\n\n"
        "• <b>/son</b> VEYA <b>/bitir</b>\n"
        "└ AKTİF ETİKETLEME İŞLEMİNİ, MÜZİĞİ VEYA YARIŞMAYI ANINDA SONLANDIRIR."
    )


def download_commands_text() -> str:
    """İndirme / Medya indirici açıklama metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.CMD_DOWNLOAD}">💿</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>ŞARKI VE MEDYA İNDİRİCİ:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n\n'
        "• <b>/indir</b> [ŞARKI ADI] - ŞARKI İNDİRİR.\n\n"
        f'<tg-emoji emoji-id="{emoji.CMD_DOWNLOAD}">💿</tg-emoji>'
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>'
        " <b>MEDYA İNDİRİCİ:</b>"
        f' <tg-emoji emoji-id="{emoji.ID_SPARKLE}">✨</tg-emoji>\n'
        "<i>Aşağıdaki platformların medya paylaşım linklerini gruba atmanız yeterlidir:</i>\n\n"
        "• <b>INSTAGRAM</b>\n"
        "└ (GÖNDERİ, HİKAYE, REELS)\n\n"
        "• <b>YOUTUBE</b>\n"
        "└ (VİDEO, SHORTS, SES)\n\n"
        "• <b>TİKTOK</b>\n"
        "└ (FİLİGRANSIZ VİDEO)\n\n"
        "• <b>FACEBOOK</b>\n"
        "└ (GÖNDERİ, REELS)\n\n"
        "• <b>PINTEREST</b>\n"
        "└ (FOTOĞRAF, VİDEO)\n\n"
        "• <b>SNAPCHAT</b>\n"
        "└ (FOTOĞRAF, VİDEO)\n\n"
        "• <b>TELEGRAM</b>\n"
        "└ (HİKAYE İNDİRME)\n\n"
        "• <b>LIKEE</b>\n"
        "└ (FİLİGRANSIZ VİDEO)\n\n"
        "• <b>THREADS</b>\n"
        "└ (FOTOĞRAF, VİDEO)"
    )


def developer_text() -> str:
    """Sahip & Yönetici komutları metni."""
    return (
        f'<tg-emoji emoji-id="{emoji.CROWN}">👑</tg-emoji>'
        " <b>SAHİP & YÖNETİCİ KOMUTLARI:</b>\n\n"
        f'<tg-emoji emoji-id="{emoji.WRENCH}">🛠️</tg-emoji>'
        " <b>TEMEL KOMUTLAR:</b>\n"
        "• <b>/panel</b> - YÖNETİCİ PANELİNİ AÇAR.\n"
        "• <b>/uyku</b> - BOTU BAKIM MODUNA ALIR.\n"
        "• <b>/ban</b> [ID] - KULLANICIYI YASAKLAR.\n"
        "• <b>/unban</b> [ID] - YASAĞI KALDIRIR.\n\n"
        f'<tg-emoji emoji-id="{emoji.GEAR}">⚙️</tg-emoji>'
        " <b>PANEL İŞLEYİCİLERİ:</b>\n"
        f'<tg-emoji emoji-id="{emoji.ROCKET}">🚀</tg-emoji>'
        " <b>HIZ TESTİ:</b> SUNUCU İNTERNET HIZINI ÖLÇER.\n"
        f'<tg-emoji emoji-id="{emoji.NOW_PLAYING}">🎧</tg-emoji>'
        " <b>SES/VİDEO KALİTESİ:</b> YAYIN ÇÖZÜNÜRLÜĞÜNÜ DEĞİŞTİRİR.\n"
        f'<tg-emoji emoji-id="{emoji.STATS}">📊</tg-emoji>'
        " <b>İSTATİSTİKLER:</b> BOTUN GENEL KULLANIM VERİLERİDİR.\n"
        f'<tg-emoji emoji-id="{emoji.BROADCAST}">📢</tg-emoji>'
        " <b>GELİŞMİŞ REKLAM:</b> TÜM GRUP VE KİŞİLERE DUYURU ATAR.\n"
        f'<tg-emoji emoji-id="{emoji.BROOM}">🔔</tg-emoji>'
        " <b>ÖNBELLEK TEMİZLE:</b> BOTU RAHATLATIR, KASMALARI ÇÖZER.\n"
        f'<tg-emoji emoji-id="{emoji.SLEEP}">💤</tg-emoji>'
        " <b>UYKU MODU:</b> BOTU DIŞARIYA KAPATIR, SADECE SİZ DİNLERSİNİZ.\n"
        f'<tg-emoji emoji-id="{emoji.BAN}">🔨</tg-emoji>'
        " <b>YASAKLAMA:</b> BAN EKLEME VE KALDIRMA MENÜSÜ.\n"
        f'<tg-emoji emoji-id="{emoji.GROUP_SETTINGS}">👥</tg-emoji>'
        " <b>GRUP AYARLARI:</b> GRUPLARDAN AYRILMA VE MESAJ ATMA.\n"
        f'<tg-emoji emoji-id="{emoji.DATABASE}">📁</tg-emoji>'
        " <b>KAYITLAR:</b> VERİTABANI YEDEĞİNİ DOSYA OLARAK ALIR.\n"
        f'<tg-emoji emoji-id="{emoji.WEB}">🔗</tg-emoji>'
        " <b>WEB PANEL:</b> TARAYICI ÜZERİNDEN GÖRSEL YÖNETİM."
    )
