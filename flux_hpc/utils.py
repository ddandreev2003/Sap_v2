#!/usr/bin/env python3
"""
Утилита для управления конфигурацией генератора изображений

Позволяет:
- Проверить окружение
- Валидировать JSON файлы с промптами
- Сгенерировать шаблон промптов
"""

import os
import json
import argparse
import torch
from pathlib import Path


def check_environment():
    """Проверка окружения и необходимых зависимостей"""
    print("\n" + "="*60)
    print("🔍 Проверка окружения")
    print("="*60)
    
    checks = {
        "Python версия": f"{torch.__version__}",
        "PyTorch установлен": "✅" if torch else "❌",
        "CUDA доступна": "✅" if torch.cuda.is_available() else "⚠️ (нужен только на HPC)",
    }
    
    if torch.cuda.is_available():
        checks["CUDA версия"] = torch.version.cuda
        checks["Доступные GPU"] = torch.cuda.device_count()
        checks["Текущий GPU"] = torch.cuda.get_device_name(0)
    
    for key, value in checks.items():
        print(f"  {key:.<40} {value}")
    
    print("\n✅ Окружение готово к работе!\n")


def validate_prompts_file(filepath: str) -> bool:
    """Валидирование JSON файла с промптами"""
    print(f"\n{'='*60}")
    print(f"📋 Валидация: {filepath}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ JSON синтаксис корректен")
        
        total_prompts = 0
        total_hints = 0
        
        for prompt_name, prompt_info in data.items():
            total_prompts += 1
            
            if "text" not in prompt_info:
                print(f"  ⚠️  '{prompt_name}': отсутствует поле 'text'")
                return False
            
            if not prompt_info["text"]:
                print(f"  ⚠️  '{prompt_name}': пустой промпт")
                return False
            
            hints = prompt_info.get("hints", [])
            if isinstance(hints, list):
                total_hints += len(hints)
            else:
                print(f"  ⚠️  '{prompt_name}': 'hints' должен быть списком")
                return False
        
        print(f"\n📊 Статистика:")
        print(f"  Всего промптов: {total_prompts}")
        print(f"  Всего подсказок: {total_hints}")
        
        # Расчет генерируемых изображений
        num_images = total_prompts * (2 + 5)  # 2 без подсказок + 5 с подсказками
        print(f"  Будет сгенерировано изображений: {num_images}")
        
        print(f"\n✅ Файл промптов валиден!\n")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка JSON: {e}\n")
        return False
    except FileNotFoundError:
        print(f"❌ Файл не найден: {filepath}\n")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}\n")
        return False


def generate_template_prompts(output_file: str = "prompts_template.json"):
    """Генерирование шаблона JSON файла с промптами"""
    print(f"\n{'='*60}")
    print(f"📝 Создание шаблона: {output_file}")
    print(f"{'='*60}")
    
    template = {
        "landscape_sunset": {
            "text": "A serene landscape with mountains at sunset, golden hour lighting",
            "hints": [
                "soft warm colors, peaceful atmosphere",
                "dramatic clouds, cinematic composition",
                "detailed natural elements, realistic style",
                "vibrant colors, artistic impression",
                "minimalist approach, clean composition"
            ]
        },
        "cyberpunk_city": {
            "text": "A futuristic cityscape with flying cars and neon lights",
            "hints": [
                "cyberpunk aesthetic, vibrant neon colors",
                "detailed architecture, sci-fi style",
                "crowded streets, dynamic composition",
                "night scene, atmospheric lighting",
                "high contrast, dramatic perspective"
            ]
        },
        "cozy_cafe": {
            "text": "A cozy coffee shop interior with warm lighting and customers",
            "hints": [
                "warm ambient lighting, inviting atmosphere",
                "detailed interior design, comfortable furniture",
                "busy atmosphere, people interaction",
                "minimalist design, modern aesthetic",
                "vintage style, nostalgic feeling"
            ]
        }
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Шаблон создан: {output_file}")
        print(f"📝 Отредактируйте файл и добавьте свои промпты")
        print(f"\n✅ Готово!\n")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Утилита для управления конфигурацией FLUX генератора"
    )
    
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Проверить окружение и зависимости"
    )
    
    parser.add_argument(
        "--validate-prompts",
        type=str,
        help="Валидировать JSON файл с промптами"
    )
    
    parser.add_argument(
        "--create-template",
        nargs='?',
        const="prompts_template.json",
        help="Создать шаблон JSON файла с промптами"
    )
    
    args = parser.parse_args()
    
    if args.check_env:
        check_environment()
    elif args.validate_prompts:
        validate_prompts_file(args.validate_prompts)
    elif args.create_template is not None:
        generate_template_prompts(args.create_template)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
