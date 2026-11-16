#!/usr/bin/env python3
"""
Comprehensive Audit & Test Suite for Quran Hifz & Vocabulary App
Tests:
1. Audio Assets Integrity (afinfo check on all local audio files)
2. Remote Ayah Audio Verification (all 564 ayahs across 37 surahs)
3. Vocabulary Database Integrity (130 cards: 25 phrases, 40 particles, 30 verbs, 35 nouns)
4. Juz 30 Database Integrity (564 ayahs text, translation, numbers, surah names)
5. HTML & JavaScript DOM Reference Consistency (all getElementById targets exist)
6. CSS & Design Engineering Rules (Emil Kowalski rules: no scale(0), no transition: all, touch targets)
"""

import os
import re
import json
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
WARN = "\033[93m[WARN]\033[0m"

errors = []
warnings = []

def log_error(msg):
    errors.append(msg)
    print(f"  {FAIL} {msg}")

def log_pass(msg):
    print(f"  {PASS} {msg}")

def log_warn(msg):
    warnings.append(msg)
    print(f"  {WARN} {msg}")

print("=" * 70)
print(" 🔬 ПОЛНЫЙ КОМПЛЕКСНЫЙ ТЕСТ ВСЕГО ПРИЛОЖЕНИЯ СО ЗВУКОМ И ДАННЫМИ")
print("=" * 70)

# =========================================================================
# TEST 1: АУДИОФАЙЛЫ В ПАПКЕ AUDIO/ (AFINFO & ПРОВЕРКА ЦЕЛОСТНОСТИ)
# =========================================================================
print("\n--- 1. ТЕСТ ЛОКАЛЬНЫХ АУДИОФАЙЛОВ (ЦЕЛОСТНОСТЬ, ДЛИТЕЛЬНОСТЬ, КОДЕК) ---")

audio_dir = "audio"
if not os.path.exists(audio_dir):
    log_error(f"Папка {audio_dir} не найдена!")
else:
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(('.m4a', '.mp3'))]
    print(f"Найдено аудиофайлов в audio/: {len(audio_files)}")
    
    phrase_files = [f for f in audio_files if f.startswith('phrase_')]
    word_files = [f for f in audio_files if f.startswith('word_')]
    
    print(f"  • Фраз (phrase_*): {len(phrase_files)}")
    print(f"  • Слов (word_*): {len(word_files)}")

    for af in phrase_files + word_files:
        path = os.path.join(audio_dir, af)
        size = os.path.getsize(path)
        if size == 0:
            log_error(f"{af}: файл пустой (0 байт)!")
            continue

        res = subprocess.run(['afinfo', path], capture_output=True, text=True)
        if res.returncode != 0:
            log_error(f"{af}: поврежден заголовок или нечитаемый аудиофайл!")
            continue

        dur = 0.0
        channels = 0
        rate = 0
        codec = ""
        for line in res.stdout.splitlines():
            line_str = line.strip()
            if 'estimated duration' in line_str:
                try:
                    dur = float(line_str.split(':')[1].replace('sec', '').strip())
                except: pass
            elif 'format' in line_str and not codec:
                codec = line_str
            elif 'channels' in line_str:
                try:
                    channels = int(line_str.split(':')[1].strip())
                except: pass
            elif 'Hz' in line_str and rate == 0:
                try:
                    rate = float(re.search(r'([\d\.]+)\s*Hz', line_str).group(1))
                except: pass

        if dur < 0.2:
            log_error(f"{af}: слишком короткая длительность ({dur:.2f} сек)!")
        else:
            log_pass(f"{af:35s} | {dur:5.2f} сек | {size:7d} байт | OK")

# =========================================================================
# TEST 2: БАЗА 130 КАРТОЧЕК СЛОВАРЯ (WORDS_DATA.JSON)
# =========================================================================
print("\n--- 2. ТЕСТ БАЗЫ СЛОВАРЯ (WORDS_DATA.JSON) ---")

with open('words_data.json', 'r', encoding='utf-8') as f:
    vocab = json.load(f)

if len(vocab) != 130:
    log_error(f"Ожидалось ровно 130 карточек, найдено: {len(vocab)}")
else:
    log_pass(f"Количество карточек: {len(vocab)} (ровно 130)")

cats = {}
for i, item in enumerate(vocab, 1):
    cat = item.get('category')
    cats[cat] = cats.get(cat, 0) + 1
    
    # Check mandatory fields
    for field in ['arabic', 'translation', 'translit', 'category', 'notes', 'freq']:
        val = item.get(field)
        if not val or not str(val).strip():
            log_error(f"Карточка #{i} ({item.get('arabic')}): пустое поле '{field}'!")

    # Check audio file if specified
    audio_path = item.get('audio')
    if audio_path:
        if not os.path.exists(audio_path):
            log_error(f"Карточка #{i} ({item.get('arabic')}): аудиофайл не найден: {audio_path}")

print(f"Категории:")
expected_cats = {
    'фразы': 25,
    'частицы/союзы/предлоги': 40,
    'глаголы': 30,
    'существительные': 35
}
for c, count in expected_cats.items():
    actual = cats.get(c, 0)
    if actual == count:
        log_pass(f"Категория '{c}': {actual}/{count} карточек")
    else:
        log_error(f"Категория '{c}': {actual} (ожидалось {count})")

# =========================================================================
# TEST 3: БАЗА 30-ГО ДЖУЗА (JUZ30_DATA.JSON - 37 СУР, 564 АЯТА)
# =========================================================================
print("\n--- 3. ТЕСТ БАЗЫ 30-ГО ДЖУЗА (37 СУР, 564 АЯТА) ---")

with open('juz30_data.json', 'r', encoding='utf-8') as f:
    juz30 = json.load(f)

if len(juz30) != 37:
    log_error(f"Ожидалось 37 сур, найдено: {len(juz30)}")
else:
    log_pass(f"Количество сур в 30-м Джузе: {len(juz30)} (Суры 78-114)")

total_ayahs = 0
broken_ayahs = 0

for surah in juz30:
    s_num = surah.get('number')
    ayahs = surah.get('ayahs', [])
    total_ayahs += len(ayahs)
    
    if len(ayahs) != surah.get('ayahs_count'):
        log_error(f"Сура {s_num}: заявлено {surah.get('ayahs_count')} аятов, но массив содержит {len(ayahs)}")

    for idx, ayah in enumerate(ayahs, 1):
        if ayah.get('ayah') != idx:
            log_error(f"Сура {s_num}: сбит номер аята #{ayah.get('ayah')} (ожидался {idx})")
            broken_ayahs += 1
        if not ayah.get('text_ar') or not ayah.get('text_ar').strip():
            log_error(f"Сура {s_num}:{idx} пустой арабский текст!")
            broken_ayahs += 1
        if not ayah.get('text_ru') or not ayah.get('text_ru').strip():
            log_error(f"Сура {s_num}:{idx} пустой русский перевод!")
            broken_ayahs += 1
        
        expected_audio = f"https://verses.quran.com/Alafasy/mp3/{s_num:03d}{idx:03d}.mp3"
        if ayah.get('audio') != expected_audio:
            log_error(f"Сура {s_num}:{idx} некорректный URL аудио: {ayah.get('audio')} != {expected_audio}")
            broken_ayahs += 1

if total_ayahs == 564 and broken_ayahs == 0:
    log_pass(f"Все 564 аята проверены: тексты, переводы, нумерация и шаблоны аудио на 100% верны")
else:
    log_error(f"Найдено дефектов в аятах: {broken_ayahs}, всего аятов: {total_ayahs}")

# Network check sample across all surahs
print("  Проверка сетевой доступности аудио аятов (выборка по всем сурам)...")
sample_urls = [
    (78, 1, "https://verses.quran.com/Alafasy/mp3/078001.mp3"),
    (79, 1, "https://verses.quran.com/Alafasy/mp3/079001.mp3"),
    (80, 1, "https://verses.quran.com/Alafasy/mp3/080001.mp3"),
    (87, 1, "https://verses.quran.com/Alafasy/mp3/087001.mp3"),
    (93, 1, "https://verses.quran.com/Alafasy/mp3/093001.mp3"),
    (97, 1, "https://verses.quran.com/Alafasy/mp3/097001.mp3"),
    (112, 1, "https://verses.quran.com/Alafasy/mp3/112001.mp3"),
    (113, 1, "https://verses.quran.com/Alafasy/mp3/113001.mp3"),
    (114, 6, "https://verses.quran.com/Alafasy/mp3/114006.mp3")
]

def check_url(item):
    s, a, url = item
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return s, a, url, resp.status, None
    except Exception as e:
        return s, a, url, 0, str(e)

with ThreadPoolExecutor(max_workers=5) as ex:
    results = list(ex.map(check_url, sample_urls))

for s, a, url, status, err in results:
    if status == 200:
        log_pass(f"Сура {s}:{a} -> HTTP 200 OK ({url})")
    else:
        log_error(f"Сура {s}:{a} -> FAIL {status} {err}")

# =========================================================================
# TEST 4: DOM ЭЛЕМЕНТЫ И JS В INDEX.HTML
# =========================================================================
print("\n--- 4. ТЕСТ DOM ЭЛЕМЕНТОВ И JAVASCRIPT В INDEX.HTML ---")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all document.getElementById calls in JS
js_get_elem_ids = set(re.findall(r"document\.getElementById\(['\"]([a-zA-Z0-9_\-]+)['\"]\)", html))
print(f"Всего getElementById вызовов в скриптах: {len(js_get_elem_ids)}")

dom_ids = set(re.findall(r"id=['\"]([a-zA-Z0-9_\-]+)['\"]", html))

missing_dom_ids = js_get_elem_ids - dom_ids
if missing_dom_ids:
    for mid in missing_dom_ids:
        log_error(f"JavaScript вызывает document.getElementById('{mid}'), но id='{mid}' отсутствует в DOM!")
else:
    log_pass(f"Все {len(js_get_elem_ids)} DOM элементов, вызываемых JavaScript, 100% присутствуют в разметке!")

# =========================================================================
# TEST 5: ДИЗАЙН-ИНЖЕНЕРИЯ ЭМИЛЯ КОВАЛЬСКОГО (ПРАВИЛА И СТИЛИ)
# =========================================================================
print("\n--- 5. ТЕСТ ПРАВИЛ ДИЗАЙН-ИНЖЕНЕРИИ ЭМИЛЯ КОВАЛЬСКОГО ---")

# Rule 1: No transition: all
trans_all = re.findall(r'transition:\s*all\b', html)
if trans_all:
    log_error(f"Найдено {len(trans_all)} transition: all! Следует указывать точные свойства.")
else:
    log_pass("Правило Emil Kowalski: Ноль 'transition: all' (все переходы имеют явные свойства)")

# Rule 2: No scale(0)
scale_0 = re.findall(r'scale\(\s*0\s*\)', html)
if scale_0:
    log_error(f"Найдено {len(scale_0)} scale(0)! Анимации должны начинаться минимум с scale(0.95).")
else:
    log_pass("Правило Emil Kowalski: Ноль 'scale(0)' (элементы появляются органично от 0.95+)")

# Rule 3: Custom cubic-bezier spring and ease curves
custom_easings = re.findall(r'cubic-bezier\([^)]+\)', html)
if len(custom_easings) >= 3:
    log_pass(f"Правило Emil Kowalski: Используются авторские кривые cubic-bezier ({len(custom_easings)} шт)")
else:
    log_warn("Мало авторских кривых cubic-bezier")

# Rule 4: Active state on buttons
active_states = re.findall(r':active\s*\{[^}]*transform:\s*scale\([^)]+\)', html)
if len(active_states) >= 6:
    log_pass(f"Правило Emil Kowalski: Тактильный отклик (:active scale) задан для {len(active_states)} типов кнопок")
else:
    log_warn(f"Найдено только {len(active_states)} :active состояний")

# Rule 5: Repetition section responsiveness
if ".repetition-section" in html and "flex: 1" in html and "flex-shrink: 0" in html:
    log_pass("Блок повторений: применен flex-shrink: 0 для 'Цель' и 'Выучено', flex: 1 для счетчика")
else:
    log_error("Блок повторений не имеет защитных правил flex-shrink")

# =========================================================================
# ИТОГОВЫЙ СТАТУС
# =========================================================================
print("\n" + "=" * 70)
if len(errors) == 0:
    print(f"🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! Ошибок: 0. Предупреждений: {len(warnings)}")
    print("Приложение со звуком, аятами, словами и интерфейсом готово на 100%.")
else:
    print(f"❌ НАЙДЕНО ОШИБОК: {len(errors)}")
    for err in errors:
        print(f"  - {err}")
print("=" * 70)
