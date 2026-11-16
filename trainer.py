#!/usr/bin/env python3
"""
Интерактивный консольный тренажер для заучивания частых слов и фраз Корана.
Читает quran_frequent_words.tsv и предлагает карточки для проверки знаний.
"""

import csv
import random
import sys
from pathlib import Path

TSV_PATH = Path(__file__).parent / "quran_frequent_words.tsv"


def load_words():
    words = []
    if not TSV_PATH.exists():
        print(f"Ошибка: файл {TSV_PATH} не найден.")
        sys.exit(1)

    with open(TSV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 5 and parts[0] != "Arabic":
                words.append({
                    "arabic": parts[0],
                    "translation": parts[1],
                    "translit": parts[2],
                    "freq": parts[3],
                    "category": parts[4],
                    "notes": parts[5] if len(parts) > 5 else ""
                })
    return words


def main():
    words = load_words()
    print("=" * 60)
    print(" 📖 ТРЕНАЖЕР ЧАСТЫХ СЛОВ И ФРАЗ КОРАНА")
    print(f" Всего карточек в базе: {len(words)}")
    print("=" * 60)

    categories = sorted(list({w["category"] for w in words}))
    print("\nВыберите категорию для тренировки:")
    print(" 0. Все слова и фразы подряд")
    for idx, cat in enumerate(categories, 1):
        count = sum(1 for w in words if w["category"] == cat)
        print(f" {idx}. {cat.replace('_', ' ')} ({count} карточек)")

    choice = input("\nВведите номер (или Enter для всех): ").strip()
    if choice and choice.isdigit() and 1 <= int(choice) <= len(categories):
        selected_cat = categories[int(choice) - 1]
        pool = [w for w in words if w["category"] == selected_cat]
    else:
        pool = list(words)

    random.shuffle(pool)
    print(f"\nВыбрано для тренировки: {len(pool)} карточек.")
    print("Подсказка: нажмите Enter, чтобы увидеть перевод, или 'q' для выхода.\n")

    correct = 0
    total = 0

    for item in pool:
        total += 1
        print("-" * 50)
        print(f"[{total}/{len(pool)}]  Частота в Коране: {item['freq']}  |  {item['category'].replace('_', ' ')}")
        print(f"\n   👉   \033[1;32m{item['arabic']}\033[0m")
        print(f"       ({item['translit']})\n")

        inp = input("Знаете перевод? Нажмите Enter для ответа (или 'q' для выхода): ").strip()
        if inp.lower() in ("q", "й", "exit"):
            break

        print(f"\n   ✅   \033[1;34mПеревод:\033[0m {item['translation']}")
        if item['notes']:
            print(f"   💡   \033[1;33mКонтекст:\033[0m {item['notes']}")

        ans = input("\nВы знали это слово? (1 - Да, 0 - Нет): ").strip()
        if ans == "1":
            correct += 1
            print("Отлично! 👍")
        else:
            print("Ничего, повторим еще раз! 💪")

    print("\n" + "=" * 60)
    print(f" Сессия завершена! Результат: {correct} из {total} ({int((correct/total)*100) if total else 0}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
