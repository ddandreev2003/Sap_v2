#!/usr/bin/env python
"""
=============================================================================
                   WORKFLOW: Предгенерирование SAP + Использование
=============================================================================

Полный пример использования системы:
1. Генерирование SAP декомпозиций из промтов (один раз)
2. Использование предгенерированных SAP декомпозиций для FLUX (многократно)

Преимущества:
- Экономия времени: LLM вызывается один раз, а FLUX может вызваться много раз
- Экономия памяти: LLM модель выгружается после первого этапа
- Возможность проверки/редактирования SAP декомпозиций перед использованием
- Возможность использования дорогих моделей (GPT-4) для decomposition
  и дешевых моделей (локальной FLUX) для generation
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def step_1_generate_sap_prompts(
    prompts_file: str = "prompts.txt",
    output_file: str = "SAP_prompts.json",
    llm: str = "GPT"
):
    """
    ШАГ 1: Генерирование SAP декомпозиций из текстовых промтов
    
    Аргументы:
    - prompts_file: Путь к файлу с промтами (один промт на строку)
    - output_file: Путь к выходному JSON файлу
    - llm: Какой LLM использовать ("GPT" или "Zephyr")
    """
    print("\n" + "=" * 70)
    print("ШАГ 1: ГЕНЕРИРОВАНИЕ SAP ДЕКОМПОЗИЦИЙ")
    print("=" * 70)
    print(f"📄 Входной файл: {prompts_file}")
    print(f"💾 Выходной файл: {output_file}")
    print(f"🤖 LLM модель: {llm}")
    print("-" * 70)
    
    # Проверяем, что файл с промтами существует
    if not Path(prompts_file).exists():
        print(f"❌ ОШИБКА: Файл '{prompts_file}' не найден!")
        print(f"   Создайте файл с промтами (один промт на строку)")
        return False
    
    # Запускаем скрипт генерирования
    cmd = [
        "python",
        "generate_sap_prompts.py",
        "--prompts-file", prompts_file,
        "--output-file", output_file,
        "--llm", llm
    ]
    
    print(f"🚀 Выполняю: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("\n✅ ШАГ 1 ЗАВЕРШЕН УСПЕШНО!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ОШИБКА при генерировании SAP промтов: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ ОШИБКА: Скрипт generate_sap_prompts.py не найден!")
        return False


def step_2_verify_sap_prompts(output_file: str = "SAP_prompts.json"):
    """
    ШАГ 1.5 (опционально): Проверка и просмотр сгенерированных SAP декомпозиций
    """
    print("\n" + "=" * 70)
    print("ШАГ 1.5: ПРОВЕРКА SAP ДЕКОМПОЗИЦИЙ")
    print("=" * 70)
    
    if not Path(output_file).exists():
        print(f"❌ Файл '{output_file}' не найден!")
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📊 Статистика SAP декомпозиций:")
        print(f"  - Всего промтов: {len(data['prompts'])}")
        print(f"  - Успешных: {sum(1 for p in data['prompts'] if p.get('sap_decomposition'))}")
        print(f"  - Ошибок: {sum(1 for p in data['prompts'] if not p.get('sap_decomposition'))}")
        
        print(f"\n📝 ПРИМЕРЫ (первые 2 промта):")
        for i, prompt_data in enumerate(data['prompts'][:2], 1):
            print(f"\n  [{i}] Оригинальный промт:")
            print(f"      {prompt_data['original_prompt'][:70]}...")
            
            if prompt_data.get('sap_decomposition'):
                sap = prompt_data['sap_decomposition']
                print(f"  SAP Декомпозиция:")
                if isinstance(sap, dict):
                    print(f"      - Объяснение: {sap.get('explanation', 'N/A')[:60]}...")
                    if 'prompts_list' in sap:
                        print(f"      - Количество этапов: {len(sap['prompts_list'])}")
                        print(f"      - Переключения: {sap.get('switch_prompts_steps', [])}")
                else:
                    print(f"      {str(sap)[:100]}...")
            else:
                print(f"  ❌ Ошибка при генерировании SAP")
        
        print("\n✅ Проверка завершена!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return False


def step_3_generate_images_with_sap(
    output_file: str = "SAP_prompts.json",
    mode: str = "sap",
    num_seeds: int = 1,
    num_steps: int = 30,
    use_cpu_offload: bool = True
):
    """
    ШАГ 2: Генерирование изображений с использованием предгенерированных SAP
    
    Аргументы:
    - output_file: Путь к JSON файлу с SAP декомпозициями
    - mode: "direct", "sap" или "both"
    - num_seeds: Количество изображений на промт (random seeds)
    - num_steps: Количество inference steps (20-50)
    - use_cpu_offload: Разгрузка модели на CPU для экономии памяти
    """
    print("\n" + "=" * 70)
    print("ШАГ 2: ГЕНЕРИРОВАНИЕ ИЗОБРАЖЕНИЙ С ИСПОЛЬЗОВАНИЕМ SAP")
    print("=" * 70)
    print(f"📊 Параметры:")
    print(f"  - Режим: {mode}")
    print(f"  - SAP файл: {output_file}")
    print(f"  - Изображений на промт: {num_seeds}")
    print(f"  - Шагов inference: {num_steps}")
    print(f"  - CPU offload: {use_cpu_offload}")
    print("-" * 70)
    
    if not Path(output_file).exists():
        print(f"❌ Файл '{output_file}' не найден!")
        print(f"   Сначала запустите ШАГ 1 для генерирования SAP декомпозиций")
        return False
    
    # Строим команду для запуска combined_flux_sap.py
    cmd = [
        "python",
        "combined_flux_sap.py",
        "--mode", mode,
        "--num-inference-steps", str(num_steps),
        "--num-images-per-seed", str(num_seeds),
        "--use-pregenerated-sap", output_file
    ]
    
    if use_cpu_offload:
        cmd.append("--enable-cpu-offload")
    
    print(f"🚀 Выполняю: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print("\n✅ ШАГ 2 ЗАВЕРШЕН УСПЕШНО!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ОШИБКА при генерировании изображений: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ ОШИБКА: Скрипт combined_flux_sap.py не найден!")
        return False


def show_workflow_options():
    """Показать доступные варианты использования"""
    print("\n" + "=" * 70)
    print("ВАРИАНТЫ ИСПОЛЬЗОВАНИЯ WORKFLOW")
    print("=" * 70)
    
    print("""
1. БАЗОВЫЙ WORKFLOW (рекомендуется):
   - Генерируем SAP один раз с GPT (дорого, но качественно)
   - Используем предгенерированные SAP много раз с локальной FLUX (дешево)
   
   Команды:
   $ python workflow_example.py --step 1 --llm GPT
   $ python workflow_example.py --step 2 --mode sap
   $ python workflow_example.py --step 2 --mode sap  (можно повторить)
   
2. БЫСТРЫЙ ЛОКАЛЬНЫЙ WORKFLOW:
   - Генерируем SAP с локальной Zephyr моделью (медленнее, но бесплатно)
   - Используем с локальной FLUX
   
   Команды:
   $ python workflow_example.py --step 1 --llm Zephyr
   $ python workflow_example.py --step 2 --mode sap
   
3. СРАВНЕНИЕ МЕТОДОВ:
   - Генерируем SAP один раз
   - Сравниваем Direct FLUX с SAP FLUX на одних и тех же промтах
   
   Команды:
   $ python workflow_example.py --step 1 --llm GPT
   $ python workflow_example.py --step 2 --mode both

4. ПРОВЕРКА И РЕДАКТИРОВАНИЕ:
   - Генерируем SAP
   - Просматриваем результаты
   - (опционально) редактируем SAP_prompts.json вручную
   - Используем для генерирования изображений
   
   Команды:
   $ python workflow_example.py --step 1 --llm GPT
   $ python workflow_example.py --step 1.5
   $ # Редактируем SAP_prompts.json при необходимости
   $ python workflow_example.py --step 2 --mode sap
""")


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Workflow: Предгенерирование SAP + Использование",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Генерирование SAP с GPT (один раз)
  python workflow_example.py --step 1 --llm GPT
  
  # Проверка сгенерированных SAP
  python workflow_example.py --step 1.5
  
  # Генерирование изображений с SAP
  python workflow_example.py --step 2 --mode sap
  
  # Полный workflow (генерирование + проверка + использование)
  python workflow_example.py --full --llm GPT --mode sap
  
  # Показать все варианты использования
  python workflow_example.py --show-options
        """
    )
    
    parser.add_argument(
        '--step',
        type=str,
        choices=['1', '1.5', '2', '1-2'],
        default=None,
        help='Какой шаг выполнить (1=генерировать SAP, 1.5=проверить, 2=генерировать FLUX)'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Выполнить полный workflow (шаги 1 -> 1.5 -> 2)'
    )
    
    parser.add_argument(
        '--show-options',
        action='store_true',
        help='Показать доступные варианты использования и выход'
    )
    
    parser.add_argument(
        '--prompts-file',
        type=str,
        default='prompts.txt',
        help='Входной файл с промтами (default: prompts.txt)'
    )
    
    parser.add_argument(
        '--sap-output',
        type=str,
        default='SAP_prompts.json',
        help='Выходной файл с SAP декомпозициями (default: SAP_prompts.json)'
    )
    
    parser.add_argument(
        '--llm',
        type=str,
        choices=['GPT', 'Zephyr'],
        default='GPT',
        help='Какой LLM использовать для генерирования SAP (default: GPT)'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['direct', 'sap', 'both'],
        default='sap',
        help='Режим генерирования изображений (default: sap)'
    )
    
    parser.add_argument(
        '--num-seeds',
        type=int,
        default=1,
        help='Количество изображений на промт (default: 1)'
    )
    
    parser.add_argument(
        '--num-steps',
        type=int,
        default=30,
        help='Количество inference steps (default: 30)'
    )
    
    parser.add_argument(
        '--enable-cpu-offload',
        action='store_true',
        help='Включить CPU offload для экономии памяти'
    )
    
    args = parser.parse_args()
    
    # Показать варианты использования и выход
    if args.show_options:
        show_workflow_options()
        return 0
    
    # Полный workflow
    if args.full:
        print("\n" + "🚀" * 35)
        print("ПОЛНЫЙ WORKFLOW: SAP GENERATION -> VERIFICATION -> IMAGE GENERATION")
        print("🚀" * 35)
        
        # Шаг 1: Генерирование SAP
        if not step_1_generate_sap_prompts(
            prompts_file=args.prompts_file,
            output_file=args.sap_output,
            llm=args.llm
        ):
            return 1
        
        # Шаг 1.5: Проверка
        if not step_2_verify_sap_prompts(output_file=args.sap_output):
            print("⚠️  Проверка завершилась с ошибками, но продолжаем...")
        
        # Шаг 2: Генерирование изображений
        if not step_3_generate_images_with_sap(
            output_file=args.sap_output,
            mode=args.mode,
            num_seeds=args.num_seeds,
            num_steps=args.num_steps,
            use_cpu_offload=args.enable_cpu_offload
        ):
            return 1
        
        print("\n" + "✅" * 35)
        print("ПОЛНЫЙ WORKFLOW ЗАВЕРШЕН УСПЕШНО!")
        print("✅" * 35)
        return 0
    
    # Отдельные шаги
    if args.step == '1':
        if not step_1_generate_sap_prompts(
            prompts_file=args.prompts_file,
            output_file=args.sap_output,
            llm=args.llm
        ):
            return 1
    
    elif args.step == '1.5':
        if not step_2_verify_sap_prompts(output_file=args.sap_output):
            return 1
    
    elif args.step == '2':
        if not step_3_generate_images_with_sap(
            output_file=args.sap_output,
            mode=args.mode,
            num_seeds=args.num_seeds,
            num_steps=args.num_steps,
            use_cpu_offload=args.enable_cpu_offload
        ):
            return 1
    
    elif args.step == '1-2':
        if not step_1_generate_sap_prompts(
            prompts_file=args.prompts_file,
            output_file=args.sap_output,
            llm=args.llm
        ):
            return 1
        if not step_3_generate_images_with_sap(
            output_file=args.sap_output,
            mode=args.mode,
            num_seeds=args.num_seeds,
            num_steps=args.num_steps,
            use_cpu_offload=args.enable_cpu_offload
        ):
            return 1
    
    else:
        # Если шаг не указан, показать справку
        parser.print_help()
        print("\n💡 Совет: используйте --help для подробной справки")
        print("          или --show-options для примеров использования")
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
