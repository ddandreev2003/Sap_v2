#!/usr/bin/env python3
"""
Generate SAP decompositions for prompts in advance
Предварительно генерирует SAP декомпозиции промтов и сохраняет в JSON файл
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime
from llm_interface.llm_SAP import LLM_SAP

def load_prompts(filepath: str):
    """Загружает промты из текстового файла"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    return prompts

def generate_sap_decompositions(prompts, llm='GPT', api_key=''):
    """Генерирует SAP декомпозиции для всех промтов"""
    print(f"\n🧠 Генерирую SAP декомпозиции для {len(prompts)} промтов (LLM: {llm})...")
    
    sap_prompts_list = LLM_SAP(prompts, llm=llm, key=api_key)
    
    return sap_prompts_list

def save_sap_prompts(prompts, sap_decompositions, output_file='SAP_prompts.json'):
    """Сохраняет оригинальные промты и их SAP декомпозиции в JSON"""
    
    data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_prompts": len(prompts),
            "successfully_decomposed": sum(1 for x in sap_decompositions if x is not None)
        },
        "prompts": []
    }
    
    for i, (original, sap) in enumerate(zip(prompts, sap_decompositions), 1):
        entry = {
            "id": i,
            "original_prompt": original,
            "sap_decomposition": sap
        }
        data["prompts"].append(entry)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return output_file

def print_summary(prompts, sap_decompositions, output_file):
    """Выводит сводку генерации"""
    successful = sum(1 for x in sap_decompositions if x is not None)
    failed = len(sap_decompositions) - successful
    
    print("\n" + "=" * 70)
    print("📊 СВОДКА ГЕНЕРАЦИИ SAP ДЕКОМПОЗИЦИЙ")
    print("=" * 70)
    print(f"✅ Успешно декомпозировано: {successful}/{len(prompts)}")
    print(f"❌ Ошибок: {failed}/{len(prompts)}")
    print(f"📁 Сохранено в: {output_file}")
    print("=" * 70)
    
    # Показываем примеры
    print("\n📋 ПРИМЕРЫ:")
    for i, (prompt, sap) in enumerate(zip(prompts[:2], sap_decompositions[:2]), 1):
        print(f"\n{i}. Оригинальный промт:")
        print(f"   {prompt}")
        
        if sap:
            print(f"   SAP декомпозиция:")
            print(f"   • Промтов: {len(sap.get('prompts_list', []))}")
            print(f"   • Переключения: {sap.get('switch_prompts_steps', [])}")
            if 'explanation' in sap:
                print(f"   • Объяснение: {sap['explanation'][:100]}...")
        else:
            print(f"   ❌ Не удалось декомпозировать")

def main():
    parser = argparse.ArgumentParser(
        description="Generate SAP decompositions for prompts in advance"
    )
    
    parser.add_argument(
        '--prompts-file',
        type=str,
        default='prompts.txt',
        help='Файл с промтами'
    )
    
    parser.add_argument(
        '--output-file',
        type=str,
        default='SAP_prompts.json',
        help='Файл для сохранения SAP декомпозиций'
    )
    
    parser.add_argument(
        '--llm',
        type=str,
        choices=['GPT', 'Zephyr'],
        default='GPT',
        help='LLM для генерации'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        default=os.getenv('OPENAI_API_KEY', ''),
        help='OpenAI API ключ (или переменная окружения OPENAI_API_KEY)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧠 SAP Prompts Generator")
    print("=" * 70)
    
    # Загрузка промтов
    try:
        prompts = load_prompts(args.prompts_file)
        print(f"✅ Загружено {len(prompts)} промтов из {args.prompts_file}")
    except FileNotFoundError as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    # Генерация SAP декомпозиций
    try:
        sap_decompositions = generate_sap_decompositions(
            prompts, 
            llm=args.llm,
            api_key=args.api_key
        )
    except Exception as e:
        print(f"❌ Ошибка при генерации: {e}")
        return 1
    
    # Сохранение результатов
    try:
        output_file = save_sap_prompts(prompts, sap_decompositions, args.output_file)
        print(f"✅ Сохранено в: {output_file}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
        return 1
    
    # Вывод сводки
    print_summary(prompts, sap_decompositions, output_file)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
