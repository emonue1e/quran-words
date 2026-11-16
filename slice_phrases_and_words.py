#!/usr/bin/env python3
"""
Скрипт для нарезки точных аудиофрагментов чтения шейха Мишари Рашида аль-Афаси:
1. Вырезает ТОЛЬКО фразу из аята (без лишнего текста до и после)
2. Скачивает изолированные слова из Quran.com Word-by-Word
"""

import os
import subprocess
import wave
import urllib.request
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 1. Точные тайминги фраз (в миллисекундах)
PHRASES = [
    {
        "file": "phrase_qadir.m4a",
        "source": "002020.mp3",
        "start": 21040,
        "end": 27900,
        "title": "Инна-Ллаха ʻаля кулли шей'ин кадир"
    },
    {
        "file": "phrase_alhamdu.m4a",
        "source": "001002.mp3",
        "start": 0,
        "end": 4200,
        "title": "Аль-хамду ли-Ллях"
    },
    {
        "file": "phrase_bismillah.m4a",
        "source": "001001.mp3",
        "start": 0,
        "end": 5970,
        "title": "Бисмилляхи-р-Рахмани-р-Рахим"
    },
    {
        "file": "phrase_la_ilaha_illa_huwa.m4a",
        "source": "002255.mp3",
        "start": 990,
        "end": 4580,
        "title": "Ля иляха илля Хува"
    },
    {
        "file": "phrase_hasbuna_llah.m4a",
        "source": "003173.mp3",
        "start": 18160,
        "end": 23910,
        "title": "Хасбуна-Ллаху ва ниʻма-ль-Вакиль"
    },
    {
        "file": "phrase_ya_ayyuha_llazina_amanu.m4a",
        "source": "002153.mp3",
        "start": 130,
        "end": 4380,
        "title": "Йа айюха-ллязина аману"
    },
    {
        "file": "phrase_inna_llaha_maa_sabirin.m4a",
        "source": "002153.mp3",
        "start": 9140,
        "end": 14120,
        "title": "Инна-Ллаха маʻа-с-сабирин"
    },
    {
        "file": "phrase_allazina_amanu_wa_amilu.m4a",
        "source": "002025.mp3",
        "start": 980,
        "end": 4740,
        "title": "Аллязина аману ва ʻамилю-с-салихат"
    },
    {
        "file": "phrase_jannatin_tajri.m4a",
        "source": "002025.mp3",
        "start": 5750,
        "end": 12200,
        "title": "Джаннатин таджри мин тахтиха-ль-анхар"
    },
    {
        "file": "phrase_inna_llaha_ghafurun_rahim.m4a",
        "source": "002173.mp3",
        "start": 22190,
        "end": 26850,
        "title": "Инна-Ллаха Гафурун Рахим"
    },
    {
        "file": "phrase_inna_llaha_samiun_alim.m4a",
        "source": "002181.mp3",
        "start": 10740,
        "end": 15320,
        "title": "Инна-Ллаха Самиʻун ʻАлим"
    },
    {
        "file": "phrase_wallahu_bima_tamaluna_basir.m4a",
        "source": "002096.mp3",
        "start": 22960,
        "end": 28470,
        "title": "Ва-Ллаху бима таʻмалюна Басыр"
    },
    {
        "file": "phrase_wa_kana_llahu_aliman_hakima.m4a",
        "source": "004017.mp3",
        "start": 24950,
        "end": 28970,
        "title": "Ва кана-Ллаху ʻАлиман Хакима"
    },
    {
        "file": "phrase_wa_huwa_al_azizu_al_hakim.m4a",
        "source": "059024.mp3",
        "start": 11500,
        "end": 16200,
        "title": "Ва хува-ль-ʻАзизу-ль-Хаким"
    },
    {
        "file": "phrase_qul_huwa_llahu_ahad.m4a",
        "source": "112001.mp3",
        "start": 0,
        "end": 3000,
        "title": "Куль хува-Ллаху Ахад"
    },
    {
        "file": "phrase_rabbana_atina.m4a",
        "source": "002201.mp3",
        "start": 100,
        "end": 7500,
        "title": "Раббана атина фи-д-дунья хасанатан"
    },
    {
        "file": "phrase_wa_tawakkal_ala_llah.m4a",
        "source": "033003.mp3",
        "start": 80,
        "end": 3400,
        "title": "Ва таваккаль ʻаля-Ллах"
    }
]

# 2. Изолированные отдельные слова шейха Мишари (Quran.com Word-by-Word CDN)
WORDS = [
    ("word_min.mp3", "114_006_001.mp3", "مِنْ"),
    ("word_fi.mp3", "114_005_003.mp3", "فِي"),
    ("word_ma.mp3", "113_002_002.mp3", "مَا"),
    ("word_la.mp3", "109_002_001.mp3", "لَا"),
    ("word_allah.mp3", "112_001_003.mp3", "اللَّهُ"),
    ("word_rabb.mp3", "114_001_003.mp3", "رَبِّ"),
    ("word_nas.mp3", "114_001_004.mp3", "النَّاسِ"),
    ("word_khalaq.mp3", "113_002_003.mp3", "خَلَقَ"),
    ("word_sharr.mp3", "113_002_001.mp3", "شَرِّ"),
    ("word_huwa.mp3", "112_001_002.mp3", "هُوَ"),
    ("word_ahad.mp3", "112_001_004.mp3", "أَحَدٌ"),
    ("word_allazi.mp3", "114_005_001.mp3", "الَّذِي"),
    ("word_kana.mp3", "110_003_005.mp3", "كَانَ"),
    ("word_jaa.mp3", "110_001_002.mp3", "جَاءَ"),
    ("word_amana.mp3", "002_285_001.mp3", "آمَنَ"),
    ("word_qul.mp3", "112_001_001.mp3", "قُلْ"),
]


def slice_phrase(item):
    target = AUDIO_DIR / item["file"]
    src = AUDIO_DIR / item["source"]
    if not src.exists():
        print(f"  [!] Исходник не найден: {src}")
        return

    tmp_wav = Path(f"/tmp/src_{item['source']}.wav")
    sliced_wav = Path(f"/tmp/slice_{item['file']}.wav")

    try:
        # Convert to WAV
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16", str(src), str(tmp_wav)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Slice exact milliseconds
        with wave.open(str(tmp_wav), "rb") as w:
            params = w.getparams()
            rate = w.getframerate()
            start_frame = int((item["start"] / 1000.0) * rate)
            duration_frames = int(((item["end"] - item["start"]) / 1000.0) * rate)
            w.setpos(start_frame)
            frames = w.readframes(duration_frames)

        with wave.open(str(sliced_wav), "wb") as out:
            out.setparams(params)
            out.writeframes(frames)

        # Convert to m4a (AAC)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(sliced_wav), str(target)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  [✓] Вырезана фраза: {item['title']} -> {item['file']}")
    except Exception as e:
        print(f"  [!] Ошибка при нарезке {item['file']}: {e}")
    finally:
        if tmp_wav.exists(): tmp_wav.unlink()
        if sliced_wav.exists(): sliced_wav.unlink()


def download_word(filename, wbw_name, word_ar):
    target = AUDIO_DIR / filename
    if target.exists() and target.stat().st_size > 1000:
        return
    url = f"https://audio.qurancdn.com/wbw/{wbw_name}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp, open(target, "wb") as out:
            out.write(resp.read())
        print(f"  [✓] Скачано слово ({word_ar}): {filename}")
    except Exception as e:
        print(f"  [!] Ошибка скачивания слова {word_ar}: {e}")


def main():
    print("=" * 60)
    print(" ✂️ ТОЧНАЯ НАРЕЗКА ФРАЗ И СКАЧИВАНИЕ ИЗОЛИРОВАННЫХ СЛОВ")
    print("=" * 60)
    
    print("\n--- 1. Нарезка точных фраз шейха Мишари ---")
    for p in PHRASES:
        slice_phrase(p)

    print("\n--- 2. Скачивание изолированных слов шейха Мишари ---")
    for fn, wbw, ar in WORDS:
        download_word(fn, wbw, ar)

    print("\nГотово! Все аудиофайлы в папке audio/ строго ограничены фразой или словом.")

if __name__ == "__main__":
    main()
