#!/usr/bin/env python3
"""
Скрипт для выгрузки 30-го Джуза (Джуз 'Амма, суры 78-114):
1. Оригинальный арабский текст (Усмани с огласовками)
2. Русский перевод (Эльмир Кулиев)
3. Привязка аудио шейха Мишари Рашида аль-Афаси для каждого аята
"""

import json
import urllib.request
from pathlib import Path

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("Загрузка 30-го Джуза (Арабский текст)...")
    ar_data = fetch_json("https://api.alquran.cloud/v1/juz/30/quran-uthmani")
    
    print("Загрузка 30-го Джуза (Русский перевод Кулиева)...")
    ru_data = fetch_json("https://api.alquran.cloud/v1/juz/30/ru.kuliev")

    ar_ayahs = ar_data["data"]["ayahs"]
    ru_ayahs = ru_data["data"]["ayahs"]

    surahs_dict = {}

    for ar, ru in zip(ar_ayahs, ru_ayahs):
        surah_num = ar["surah"]["number"]
        ayah_num = ar["numberInSurah"]
        surah_ar_name = ar["surah"]["name"].replace("سُورَةُ ", "")
        surah_en_name = ar["surah"]["englishName"]

        if surah_num not in surahs_dict:
            surahs_dict[surah_num] = {
                "number": surah_num,
                "name_ar": surah_ar_name,
                "name_en": surah_en_name,
                "ayahs_count": ar["surah"]["numberOfAyahs"],
                "ayahs": []
            }

        text_ar = ar["text"]
        # Убираем Бисмиллях в начале первого аята для сур кроме 1 (в Усмани часто склеено с 1 аятом)
        if ayah_num == 1 and surah_num != 1 and text_ar.startswith("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ "):
            text_ar = text_ar[len("بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ "):].strip()

        audio_url = f"https://verses.quran.com/Alafasy/mp3/{surah_num:03d}{ayah_num:03d}.mp3"

        surahs_dict[surah_num]["ayahs"].append({
            "ayah": ayah_num,
            "text_ar": text_ar,
            "text_ru": ru["text"],
            "audio": audio_url
        })

    result = list(surahs_dict.values())
    output_path = Path(__file__).parent / "juz30_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total_ayahs = sum(len(s["ayahs"]) for s in result)
    print(f"Успешно сохранено {len(result)} сур и {total_ayahs} аятов в {output_path}!")

if __name__ == "__main__":
    main()
