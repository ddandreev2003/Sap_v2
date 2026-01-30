#!/usr/bin/env python3
"""
Quick launcher for Combined FLUX + SAP pipeline
Быстрый запуск с предустановленными конфигурациями
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd):
    """Запускает команду в терминале"""
    print(f"🚀 Запуск: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(
        description="Quick launcher for Combined FLUX + SAP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

1. Быстрое сравнение (Direct vs SAP):
   python quick_launch.py --preset compare

2. Только Direct FLUX (быстро):
   python quick_launch.py --preset direct-fast

3. Только SAP с GPT (качество):
   python quick_launch.py --preset sap-quality

4. Полное сравнение с разными seeds:
   python quick_launch.py --preset full-compare

5. Локальная генерация (Zephyr, без API):
   python quick_launch.py --preset local-zephyr

6. Пользовательские параметры:
   python quick_launch.py --mode sap --llm GPT --seeds 123 456 789
        """
    )
    
    parser.add_argument(
        '--preset',
        type=str,
        choices=['compare', 'direct-fast', 'direct-quality', 'sap-quality', 'sap-fast', 
                 'full-compare', 'local-zephyr', 'experimental'],
        help='Предустановленная конфигурация'
    )
    
    parser.add_argument('--mode', type=str, choices=['direct', 'sap', 'both'],
                        help='Режим генерации')
    parser.add_argument('--llm', type=str, choices=['GPT', 'Zephyr'],
                        help='LLM для SAP')
    parser.add_argument('--prompts-file', type=str, default='prompts.txt',
                        help='Файл с промтами')
    parser.add_argument('--seeds', nargs='+', type=int,
                        help='Seeds для генерации')
    parser.add_argument('--height', type=int, help='Высота изображения')
    parser.add_argument('--width', type=int, help='Ширина изображения')
    parser.add_argument('--steps', type=int, dest='num_inference_steps',
                        help='Количество шагов дифузии')
    
    args = parser.parse_args()
    
    # Базовая команда
    cmd = ['python', 'combined_flux_sap.py']
    
    # Применение предустановок
    if args.preset == 'compare':
        print("⚙️  Предустановка: Быстрое сравнение Direct vs SAP")
        cmd.extend(['--mode', 'both', '--num-inference-steps', '30', '--seeds', '30498'])
    
    elif args.preset == 'direct-fast':
        print("⚙️  Предустановка: Direct FLUX - Быстро")
        cmd.extend(['--mode', 'direct', '--num-inference-steps', '20', '--seeds', '30498'])
    
    elif args.preset == 'direct-quality':
        print("⚙️  Предустановка: Direct FLUX - Качество")
        cmd.extend(['--mode', 'direct', '--num-inference-steps', '50', '--seeds', '30498', '40123'])
    
    elif args.preset == 'sap-quality':
        print("⚙️  Предустановка: SAP FLUX - Качество")
        cmd.extend(['--mode', 'sap', '--llm', 'GPT', '--num-inference-steps', '50', 
                    '--seeds', '30498', '40123'])
    
    elif args.preset == 'sap-fast':
        print("⚙️  Предустановка: SAP FLUX - Быстро")
        cmd.extend(['--mode', 'sap', '--llm', 'Zephyr', '--num-inference-steps', '30', 
                    '--seeds', '30498'])
    
    elif args.preset == 'full-compare':
        print("⚙️  Предустановка: Полное сравнение (Direct vs SAP с разными seeds)")
        cmd.extend(['--mode', 'both', '--num-inference-steps', '50', 
                    '--seeds', '30498', '40123', '50456'])
    
    elif args.preset == 'local-zephyr':
        print("⚙️  Предустановка: Локальная генерация (Zephyr, без API)")
        cmd.extend(['--mode', 'sap', '--llm', 'Zephyr', '--num-inference-steps', '40',
                    '--seeds', '30498'])
    
    elif args.preset == 'experimental':
        print("⚙️  Предустановка: Экспериментальная (высокое качество)")
        cmd.extend(['--mode', 'both', '--num-inference-steps', '60',
                    '--seeds', '12345', '67890', '11111'])
    
    # Применение пользовательских параметров (перезаписывают предустановку)
    if args.mode:
        cmd.extend(['--mode', args.mode])
    
    if args.llm:
        cmd.extend(['--llm', args.llm])
    
    if args.prompts_file != 'prompts.txt':
        cmd.extend(['--prompts-file', args.prompts_file])
    
    if args.seeds:
        cmd.append('--seeds')
        cmd.extend(map(str, args.seeds))
    
    if args.height:
        cmd.extend(['--height', str(args.height)])
    
    if args.width:
        cmd.extend(['--width', str(args.width)])
    
    if args.num_inference_steps:
        cmd.extend(['--num-inference-steps', str(args.num_inference_steps)])
    
    # Запуск команды
    return_code = run_command(cmd)
    
    if return_code == 0:
        print("\n✅ Генерация успешно завершена!")
    else:
        print(f"\n❌ Ошибка при генерации (код: {return_code})")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
