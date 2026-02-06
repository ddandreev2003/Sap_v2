#!/usr/bin/env python
"""
=============================================================================
        FLUX Direct - Генерирование БЕЗ SAP
=============================================================================

Запускает обычный FLUX для всех примеров с несколькими seed'ами
"""

import torch
import argparse
from pathlib import Path
from datetime import datetime

# Примеры для генерирования
EXAMPLES = {
    "grown_man": "A grown man wearing a pacifier",
    "dragon": "A dragon blowing water",
    "pizza": "A pizza with grape toppings",
    "coin": "A coin floats on the surface of the water",
    "cockatoo_parrot": "A cockatoo parrot swimming in the ocean",
    "woman": "A woman writing with a dart",
    "shrek": "Shrek is blue"
}

def generate_flux_direct(
    num_steps=50,
    height=1024,
    width=1024,
    seeds=None,
    num_seeds=4
):
    """
    Генерирует изображения с Direct FLUX для всех примеров
    
    Параметры:
    - num_steps: количество шагов дифузии
    - height, width: размер изображения
    - seeds: список seed'ов (если None, будут сгенерированы)
    - num_seeds: количество seed'ов для каждого примера
    """
    
    if seeds is None:
        seeds = [30498 + i * 1000 for i in range(num_seeds)]
    
    print(f"\n{'='*80}")
    print(f"🎨 FLUX Direct Generation")
    print(f"{'='*80}")
    print(f"  Примеров: {len(EXAMPLES)}")
    print(f"  Seeds на пример: {len(seeds)}")
    print(f"  Шагов дифузии: {num_steps}")
    print(f"  Размер: {height}x{width}")
    print(f"  Всего изображений: {len(EXAMPLES) * len(seeds)}")
    
    # Загружаем FLUX
    print(f"\n📥 Загружаю FLUX модель...")
    try:
        from diffusers import FluxPipeline
        pipeline = FluxPipeline.from_pretrained(
            parser = argparse.ArgumentParser()
            parser.add_argument('--flux-version', type=str, default='1-dev', help='Версия FLUX: 1-dev или 2-dev')
            # ...добавьте остальные аргументы, если нужно...
            args = parser.parse_args()

            model_repo = f"black-forest-labs/FLUX.{args.flux_version}"
            pipeline = FluxPipeline.from_pretrained(
                model_repo,
                torch_dtype=torch.bfloat16
            )
        pipeline = pipeline.to("cuda")
        # Оптимизируем для памяти
        pipeline.enable_attention_slicing()
        print(f"✅ FLUX модель загружена")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке FLUX: {e}")
        return
    
    # Генерируем для каждого примера
    total_generated = 0
    failed = []
    
    for example_idx, (name, prompt) in enumerate(EXAMPLES.items(), 1):
        print(f"\n{'─'*80}")
        print(f"[{example_idx}/{len(EXAMPLES)}] 🎨 {name.upper()}")
        print(f"{'─'*80}")
        print(f"  Промт: {prompt}")
        print(f"  Генерирую {len(seeds)} изображений...")
        
        # Создаём директорию для результатов
        output_dir = Path(f"results_flux_direct/{name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for seed_idx, seed in enumerate(seeds, 1):
            try:
                print(f"    [{seed_idx}/{len(seeds)}] Seed {seed}... ", end="", flush=True)
                
                # Создаём генератор
                gen_device = "cuda" if torch.cuda.is_available() else "cpu"
                generator = torch.Generator(device=gen_device)
                generator.manual_seed(seed)
                
                # Генерируем
                output = pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_steps,
                    guidance_scale=3.5,
                    generator=generator
                )
                
                # Сохраняем
                image = output.images[0]
                filename = f"{name}_seed_{seed}.png"
                filepath = output_dir / filename
                image.save(filepath)
                
                print(f"✅ {filename}")
                total_generated += 1
                
            except Exception as e:
                print(f"❌ Ошибка: {str(e)[:50]}")
                failed.append((name, seed, str(e)))
        
        print(f"  ✅ Завершено: {len(seeds)} изображений в {output_dir}")
    
    # Итоги
    print(f"\n{'='*80}")
    print(f"📊 ИТОГИ ГЕНЕРИРОВАНИЯ")
    print(f"{'='*80}")
    print(f"  ✅ Успешно: {total_generated} изображений")
    if failed:
        print(f"  ❌ Ошибок: {len(failed)}")
        for name, seed, error in failed[:5]:
            print(f"     - {name} (seed {seed}): {error[:40]}")
    else:
        print(f"  ❌ Ошибок: 0")
    print(f"  📁 Результаты: results_flux_direct/")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FLUX Direct генерирование")
    parser.add_argument("--num-steps", type=int, default=50, help="Количество шагов (5-100)")
    parser.add_argument("--num-seeds", type=int, default=4, help="Seed'ов на пример")
    parser.add_argument("--height", type=int, default=1024, help="Высота изображения")
    parser.add_argument("--width", type=int, default=1024, help="Ширина изображения")
    
    args = parser.parse_args()
    
    generate_flux_direct(
        num_steps=args.num_steps,
        height=args.height,
        width=args.width,
        num_seeds=args.num_seeds
    )
