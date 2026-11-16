#!/usr/bin/env python3
"""
Скрипт для скачивания официального чтения шейха Мишари Рашида аль-Афаси (Mishary Rashid Alafasy).
Скачивает:
1. Ключевые суры Корана целиком (Аль-Фатиха, Аль-Ихляс, Аль-Фаляк, Ан-Нас, Аль-Мульк, Йа Син и др.)
2. Самые частые аяты и формулы Корана (Аят аль-Курси, формулы единобожия, мольбы, концовки аятов)
"""

import os
import urllib.request
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 1. Частые аяты и фразы (EveryAyah / Quran.com CDN)
AYAHS_TO_DOWNLOAD = {
    "001001.mp3": ("Бисмиллях (1:1)", "https://verses.quran.com/Alafasy/mp3/001001.mp3"),
    "001002.mp3": ("Аль-хамду ли-Ллях (1:2)", "https://verses.quran.com/Alafasy/mp3/001002.mp3"),
    "002020.mp3": ("Инна-Ллаха ʻаля кулли шей'ин кадир (2:20)", "https://verses.quran.com/Alafasy/mp3/002020.mp3"),
    "002025.mp3": ("Аллязина аману ва ʻамилю-с-салихат... Сады под которыми текут реки (2:25)", "https://verses.quran.com/Alafasy/mp3/002025.mp3"),
    "002096.mp3": ("Ва-Ллаху бима таʻмалюна Басыр (2:96)", "https://verses.quran.com/Alafasy/mp3/002096.mp3"),
    "002153.mp3": ("Йа айюха-ллязина аману... Инна-Ллаха маʻа-с-сабирин (2:153)", "https://verses.quran.com/Alafasy/mp3/002153.mp3"),
    "002173.mp3": ("Инна-Ллаха Гафурун Рахим (2:173)", "https://verses.quran.com/Alafasy/mp3/002173.mp3"),
    "002181.mp3": ("Инна-Ллаха Самиʻун ʻАлим (2:181)", "https://verses.quran.com/Alafasy/mp3/002181.mp3"),
    "002201.mp3": ("Раббана атина фи-д-дунья хасанатан (2:201)", "https://verses.quran.com/Alafasy/mp3/002201.mp3"),
    "002255.mp3": ("Аят аль-Курси (2:255)", "https://verses.quran.com/Alafasy/mp3/002255.mp3"),
    "003173.mp3": ("Хасбуна-Ллаху ва ниʻма-ль-Вакиль (3:173)", "https://verses.quran.com/Alafasy/mp3/003173.mp3"),
    "004017.mp3": ("Ва кана-Ллаху ʻАлиман Хакима (4:17)", "https://verses.quran.com/Alafasy/mp3/004017.mp3"),
    "004059.mp3": ("Атиʻу-Ллаха ва атиʻу-р-Расуль (4:59)", "https://verses.quran.com/Alafasy/mp3/004059.mp3"),
    "033003.mp3": ("Ва таваккаль ʻаля-Ллах, ва кафа би-Лляхи Вакиля (33:3)", "https://verses.quran.com/Alafasy/mp3/033003.mp3"),
    "059024.mp3": ("Ва хува-ль-ʻАзизу-ль-Хаким (59:24)", "https://verses.quran.com/Alafasy/mp3/059024.mp3"),
    "112001.mp3": ("Куль хува-Ллаху Ахад (112:1)", "https://verses.quran.com/Alafasy/mp3/112001.mp3")
}

# 2. Суры целиком (MP3Quran CDN)
SURAHS_TO_DOWNLOAD = {
    "surah_001_al_fatihah.mp3": ("Сура 1: Аль-Фатиха (Открывающая)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/001.mp3"),
    "surah_036_ya_sin.mp3": ("Сура 36: Йа Син", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/036.mp3"),
    "surah_067_al_mulk.mp3": ("Сура 67: Аль-Мульк (Власть)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/067.mp3"),
    "surah_094_ash_sharh.mp3": ("Сура 94: Аш-Шарх (Раскрытие)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/094.mp3"),
    "surah_097_al_qadr.mp3": ("Сура 97: Аль-Кадр (Предопределение)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/097.mp3"),
    "surah_103_al_asr.mp3": ("Сура 103: Аль-ʻАср (Предвечернее время)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/103.mp3"),
    "surah_108_al_kawthar.mp3": ("Сура 108: Аль-Каусар (Изобилие)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/108.mp3"),
    "surah_112_al_ikhlas.mp3": ("Сура 112: Аль-Ихляс (Искренность)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/112.mp3"),
    "surah_113_al_falaq.mp3": ("Сура 113: Аль-Фаляк (Рассвет)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/113.mp3"),
    "surah_114_an_nas.mp3": ("Сура 114: Ан-Нас (Люди)", "https://cdn.mp3quran.net/audio/mishary-alafasy/r1/114.mp3"),
}


def download_file(filename, title, url):
    target = AUDIO_DIR / filename
    if target.exists() and target.stat().st_size > 1000:
        print(f"  [✓] Уже скачано: {title} ({filename})")
        return
    print(f"  [↓] Скачивание: {title}...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp, open(target, "wb") as out:
            out.write(resp.read())
        size_kb = target.stat().st_size / 1024
        print(f"      Готово: {size_kb:.1f} KB")
    except Exception as e:
        print(f"      Ошибка при скачивании {filename}: {e}")


def main():
    print("=" * 65)
    print(" 🎙️ СКАЧИВАНИЕ ЧТЕНИЯ ШЕЙХА МИШАРИ РАШИДА АЛЬ-АФАСИ")
    print(f" Папка сохранения: {AUDIO_DIR}")
    print("=" * 65)

    print("\n--- 1. Ключевые аяты и частые формулы Корана ---")
    for fn, (title, url) in AYAHS_TO_DOWNLOAD.items():
        download_file(fn, title, url)

    print("\n--- 2. Популярные суры целиком ---")
    for fn, (title, url) in SURAHS_TO_DOWNLOAD.items():
        download_file(fn, title, url)

    print("\n" + "=" * 65)
    total_files = len(list(AUDIO_DIR.glob("*.mp3")))
    total_mb = sum(f.stat().st_size for f in AUDIO_DIR.glob("*.mp3")) / (1024 * 1024)
    print(f" Завершено! Скачано {total_files} файлов ({total_mb:.1f} MB).")
    print("=" * 65)


if __name__ == "__main__":
    main()
