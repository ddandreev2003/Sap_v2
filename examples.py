#!/usr/bin/env python3
"""
Example usage of Combined FLUX + SAP Pipeline
Примеры использования Combined FLUX + SAP Pipeline
"""

import os
import sys

# Примеры для документации
EXAMPLES = {
    "1_check_environment": {
        "description": "Проверка готовности окружения",
        "command": "python check_environment.py",
        "expected_output": "Environment readiness report",
        "time": "< 1 minute"
    },
    
    "2_quick_compare": {
        "description": "Быстрое сравнение Direct vs SAP (рекомендуется для первого запуска)",
        "command": "python quick_launch.py --preset compare",
        "expected_output": "Изображения в results_combined/batch_YYYYMMDD_HHMMSS/",
        "time": "10-20 minutes",
        "requirements": "GPU, 24GB+ VRAM"
    },
    
    "3_direct_only": {
        "description": "Только Direct FLUX генерация (быстро, без LLM)",
        "command": "python quick_launch.py --preset direct-fast",
        "expected_output": "Изображения в direct_flux/",
        "time": "5-10 minutes",
        "requirements": "GPU"
    },
    
    "4_sap_with_gpt": {
        "description": "SAP генерация с GPT (требует API ключ)",
        "commands": [
            "export OPENAI_API_KEY='sk-...'",
            "python quick_launch.py --preset sap-quality"
        ],
        "expected_output": "Изображения в sap_flux/ с LLM декомпозицией",
        "time": "15-25 minutes",
        "requirements": "GPU, OpenAI API key"
    },
    
    "5_sap_with_zephyr": {
        "description": "SAP генерация с локальной моделью Zephyr (бесплатно)",
        "command": "python quick_launch.py --preset local-zephyr",
        "expected_output": "Изображения в sap_flux/ с локальной LLM",
        "time": "20-30 minutes",
        "requirements": "GPU, 16GB+ VRAM"
    },
    
    "6_custom_prompts": {
        "description": "Генерация с пользовательскими промтами",
        "steps": [
            "1. Отредактируйте prompts.txt (один промт на строку)",
            "2. Запустите: python combined_flux_sap.py --prompts-file prompts.txt --mode both"
        ],
        "example_command": "python combined_flux_sap.py --prompts-file my_prompts.txt --height 1024 --width 1024 --seeds 123 456 789",
        "time": "Зависит от количества промтов и параметров"
    },
    
    "7_compare_results": {
        "description": "Анализ и сравнение результатов",
        "commands": [
            "python compare_results.py --batch-dir results_combined/batch_YYYYMMDD_HHMMSS --all",
            "# Откройте browser: results_combined/batch_YYYYMMDD_HHMMSS/gallery/comparison.html"
        ],
        "expected_output": "Текстовый отчет + HTML галерея"
    },
    
    "8_advanced_options": {
        "description": "Продвинутые параметры генерации",
        "examples": [
            {
                "name": "Высокое качество с разными seeds",
                "command": "python combined_flux_sap.py --mode sap --llm GPT --seeds 111 222 333 --num-inference-steps 60"
            },
            {
                "name": "Меньший размер для быстрой генерации",
                "command": "python combined_flux_sap.py --mode both --height 768 --width 768 --num-inference-steps 30"
            },
            {
                "name": "Большой размер для детальных изображений",
                "command": "python combined_flux_sap.py --mode direct --height 1024 --width 1024 --num-inference-steps 50"
            },
            {
                "name": "Только SAP с GPT и одним seed",
                "command": "export OPENAI_API_KEY='sk-...'; python combined_flux_sap.py --mode sap --llm GPT --seeds 30498"
            }
        ]
    }
}

def print_example(key: str, example: dict):
    """Выводит пример на экран"""
    print("\n" + "=" * 70)
    print(f"📌 ПРИМЕР {key}: {example.get('description', 'N/A')}")
    print("=" * 70)
    
    if 'command' in example:
        print(f"\n💻 Команда:")
        print(f"   {example['command']}")
    
    if 'commands' in example:
        print(f"\n💻 Команды:")
        for i, cmd in enumerate(example['commands'], 1):
            print(f"   {i}. {cmd}")
    
    if 'steps' in example:
        print(f"\n📋 Шаги:")
        for step in example['steps']:
            print(f"   {step}")
    
    if 'example_command' in example:
        print(f"\n💻 Пример команды:")
        print(f"   {example['example_command']}")
    
    if 'examples' in example:
        print(f"\n💻 Примеры команд:")
        for ex in example['examples']:
            print(f"\n   • {ex['name']}")
            print(f"     {ex['command']}")
    
    if 'expected_output' in example:
        print(f"\n📊 Ожидаемый результат:")
        print(f"   {example['expected_output']}")
    
    if 'time' in example:
        print(f"\n⏱️  Ожидаемое время:")
        print(f"   {example['time']}")
    
    if 'requirements' in example:
        print(f"\n📋 Требования:")
        print(f"   {example['requirements']}")

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Examples and guides for Combined FLUX + SAP Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ДОСТУПНЫЕ ПРИМЕРЫ:
  1_check_environment  - Проверка готовности окружения
  2_quick_compare      - Быстрое сравнение Direct vs SAP
  3_direct_only        - Только Direct генерация
  4_sap_with_gpt       - SAP с GPT
  5_sap_with_zephyr    - SAP с локальной моделью
  6_custom_prompts     - Генерация с пользовательскими промтами
  7_compare_results    - Анализ результатов
  8_advanced_options   - Продвинутые опции
  all                  - Показать все примеры

ИСПОЛЬЗОВАНИЕ:
  python examples.py --show 2_quick_compare
  python examples.py --show all
  python examples.py --run 1_check_environment
        """
    )
    
    parser.add_argument(
        '--show',
        type=str,
        help='Показать пример'
    )
    
    parser.add_argument(
        '--run',
        type=str,
        help='Запустить пример'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Показать список всех примеров'
    )
    
    args = parser.parse_args()
    
    if args.list or (not args.show and not args.run):
        print("\n" + "=" * 70)
        print("📖 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ Combined FLUX + SAP Pipeline")
        print("=" * 70)
        print("\nДоступные примеры:\n")
        
        for i, (key, example) in enumerate(EXAMPLES.items(), 1):
            print(f"  {key}")
            print(f"    └─ {example.get('description', 'N/A')}")
            if 'time' in example:
                print(f"       ⏱️  {example['time']}")
            print()
        
        print("\nКоманды:")
        print("  python examples.py --show 2_quick_compare")
        print("  python examples.py --show all")
        print("  python examples.py --list\n")
    
    elif args.show:
        if args.show == 'all':
            for key, example in EXAMPLES.items():
                print_example(key, example)
        elif args.show in EXAMPLES:
            print_example(args.show, EXAMPLES[args.show])
        else:
            print(f"❌ Пример '{args.show}' не найден")
            print("Используйте --list для просмотра доступных примеров")
            return 1
    
    elif args.run:
        if args.run == '1_check_environment':
            print("\n🔍 Запуск проверки окружения...\n")
            os.system('python check_environment.py')
        elif args.run in EXAMPLES:
            example = EXAMPLES[args.run]
            print(f"\n🚀 Запуск примера: {example.get('description')}\n")
            
            if 'command' in example:
                print(f"Команда: {example['command']}\n")
                os.system(example['command'])
            elif 'commands' in example:
                for cmd in example['commands']:
                    print(f"Команда: {cmd}\n")
                    os.system(cmd)
            else:
                print("❌ Этот пример требует ручного запуска")
                print_example(args.run, example)
        else:
            print(f"❌ Пример '{args.run}' не найден")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
