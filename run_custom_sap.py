#!/usr/bin/env python
"""
=============================================================================
        CUSTOM SAP FLUX - Генерирование с готовой SAP декомпозицией
=============================================================================

Запускает FLUX с вашей готовой SAP декомпозицией из словаря
"""

import os
import sys
import torch
from pathlib import Path
from datetime import datetime


# 📋 ВАШ ГОТОВЫЙ СЛОВАРЬ С SAP ДЕКОМПОЗИЦИЯМИ
CUSTOM_SAP_DECOMPOSITIONS = {
    "grown_man": {
        "original_prompt": "A grown man wearing a pacifier",
        "prompts_list": [
            "A grown man with a small object in his mouth",
            "A grown man has a baby's pacifier in his mouth"
        ],
        "switch_prompts_steps": [4]
    },
    
    "dragon": {
        "original_prompt": "A dragon blowing water",
        "prompts_list": [
            "A dragon blowing white smoke",
            "A dragon blowing water"
        ],
        "switch_prompts_steps": [3]
    },
    
    "pizza": {
        "original_prompt": "A pizza with grape toppings",
        "prompts_list": [
            "A pizza with pepperoni toppings",
            "A pizza with grape toppings"
        ],
        "switch_prompts_steps": [3]
    },
    
    "coin": {
        "original_prompt": "A coin floats on the surface of the water",
        "prompts_list": [
            "A leaf floats on the surface of the water",
            "A coin floats on the surface of the water"
        ],
        "switch_prompts_steps": [4]
    },
    
    "cockatoo_parrot": {
        "original_prompt": "A cockatoo parrot swimming in the ocean",
        "prompts_list": [
            "A duck swimming in the ocean",
            "A parrot swimming in the ocean",
            "A cockatoo parrot swimming in the ocean"
        ],
        "switch_prompts_steps": [3, 6]
    },
    
    "woman": {
        "original_prompt": "A woman writing with a dart",
        "prompts_list": [
            "A woman writing with a pen",
            "A woman writing with a dart"
        ],
        "switch_prompts_steps": [3]
    },
    
    "shrek": {
        "original_prompt": "Shrek is blue",
        "prompts_list": [
            "A blue ogre",
            "Shrek is blue"
        ],
        "switch_prompts_steps": [3]
    }
}


def generate_with_custom_sap(
    sap_data,
    name,
    num_inference_steps=50,
    guidance_scale=3.5,
    height=1024,
    width=1024,
    seeds=None,
        device="cuda",
        flux_version="1-dev"
):
    """
    Генерирует изображения с использованием готовой SAP декомпозиции
    
    Аргументы:
    - sap_data: dict с prompts_list и switch_prompts_steps
    - name: имя примера для сохранения результатов
    - num_inference_steps: количество шагов дифузии
    - guidance_scale: масштаб гайданса
    - height, width: размер изображения
    - seeds: список seeds для воспроизводимости
    - device: cuda или cpu
    """
    
    if seeds is None:
        seeds = [30498]
    
    print(f"\n{'='*70}")
    print(f"🎨 Генерирование SAP FLUX: {name}")
    print(f"{'='*70}")
    print(f"  Оригинальный промт: {sap_data['original_prompt']}")
    print(f"  Количество этапов: {len(sap_data['prompts_list'])}")
    print(f"  Переключения: {sap_data['switch_prompts_steps']}")
    print(f"  Seeds: {seeds}")
    
    # Импортируем необходимые модули
    SapFlux = None
    try:
        import sys
        from pathlib import Path as PathLib
        # Добавляем текущую директорию в sys.path если её ещё нет
        current_dir = str(PathLib.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from SAP_pipeline_flux import SapFlux
        print(f"✅ SAP Pipeline загружена успешно")
    except ImportError as import_err:
        print(f"⚠️  SAP Pipeline недоступна: {import_err}")
    
    try:
        # Загружаем модель FLUX
        print(f"\n📥 Загружаю FLUX модель...")
        
        # Создаём результирующую директорию
        output_dir = Path(f"results_custom_sap/{datetime.now().strftime('%Y%m%d_%H%M%S')}/{name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализируем pipeline
        pipeline = None
        try:
            if SapFlux is not None:
                # Пытаемся загрузить SAP Pipeline
                pipeline = SapFlux.from_pretrained(
                    "black-forest-labs/FLUX.1-dev",
                    torch_dtype=torch.bfloat16
                )
                pipeline = pipeline.to("cuda")
                print(f"✅ SAP FLUX модель загружена успешно")
                use_sap = True
            else:
                raise Exception("SapFlux not available")
                
        except Exception as pipeline_err:
            print(f"⚠️  SAP Pipeline не смог загрузиться: {pipeline_err}")
            print(f"   Переходим на обычный FLUX...")
            
            try:
                from diffusers import FluxPipeline
                pipeline = FluxPipeline.from_pretrained(
                    "black-forest-labs/FLUX.1-dev",
                    torch_dtype=torch.bfloat16
                )
                # Оптимизируем для VRAM
                pipeline.enable_attention_slicing()
                print(f"✅ FLUX модель загружена (Direct режим)")
                use_sap = False
            except Exception as flux_err:
                print(f"❌ Ошибка при загрузке FLUX: {flux_err}")
                print(f"   Проверьте что модель доступна и есть место на диске")
                return None
        
        # Генерируем изображения для каждого seed
                print(f"\n📥 Загружаю FLUX модель (версия: {flux_version})...")
        
        for seed_idx, seed in enumerate(seeds, 1):
            print(f"\n  [{seed_idx}/{len(seeds)}] Генерирую с seed={seed}...")
            
            try:
                # Создаём генератор с правильным device
                gen_device = "cuda" if device == "cuda" and torch.cuda.is_available() else "cpu"
                generator = torch.Generator(device=gen_device)
                generator.manual_seed(seed)
                
                # Запускаем генерирование
                if use_sap:
                    # SAP режим с деком позицией
                    output = pipeline(
                        height=height,
                        width=width,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        generator=generator,
                        sap_prompts={
                            "explanation": f"SAP decomposition for: {sap_data['original_prompt']}",
                            "prompts_list": sap_data["prompts_list"],
                            "switch_prompts_steps": sap_data["switch_prompts_steps"]
                        }
                    )
                else:
                    # Direct режим - используем оригинальный промт
                    output = pipeline(
                        prompt=sap_data["original_prompt"],
                        height=height,
                        width=width,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        generator=generator
                    )
                
                # Сохраняем результат
                image = output.images[0]
                filename = f"sap_{name}_seed_{seed}.png"
                filepath = output_dir / filename
                image.save(filepath)
                
                print(f"      ✅ Сохранено: {filename}")
                results.append((filename, filepath))
                
                # Освобождаем память
                del output
                torch.cuda.empty_cache()
                
            except Exception as e:
                print(f"      ❌ Ошибка при генерировании: {e}")
                continue
        
        print(f"\n✅ Генерирование завершено!")
        print(f"   Результаты сохранены в: {output_dir}")
        
        return {
            "name": name,
            "original_prompt": sap_data["original_prompt"],
            "output_dir": str(output_dir),
            "num_images": len(results),
            "results": results
        }
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Генерирование SAP FLUX с готовой декомпозицией",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Генерировать все примеры
  python run_custom_sap.py --all
  
  # Генерировать конкретный пример
  python run_custom_sap.py --name dragon
  
  # С пользовательскими параметрами
  python run_custom_sap.py --name dragon --num-steps 80 --num-seeds 4
  
  # Показать все доступные примеры
  python run_custom_sap.py --list
        """
    )
    
    parser.add_argument(
        '--name',
        type=str,
        choices=list(CUSTOM_SAP_DECOMPOSITIONS.keys()),
        default=None,
        help='Имя примера для генерирования'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Генерировать все примеры'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Показать все доступные примеры'
    )
    
    parser.add_argument(
        '--num-steps',
        type=int,
        default=50,
        help='Количество шагов дифузии (default: 50)'
    )
    
    parser.add_argument(
        '--num-seeds',
        type=int,
        default=1,
        help='Количество изображений (разные seeds) (default: 1)'
    )
    
    parser.add_argument(
        '--seeds',
        type=int,
        nargs='+',
        default=[30498],
        help='Конкретные seeds (default: 30498)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=1024,
        help='Высота изображения (default: 1024)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='Ширина изображения (default: 1024)'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        default='cuda',
        help='GPU или CPU (default: cuda)'
    )
    
    args = parser.parse_args()
    
    # Показать список примеров
    if args.list:
        print("\n" + "="*70)
        print("ДОСТУПНЫЕ ПРИМЕРЫ")
        print("="*70)
        
        for i, (key, data) in enumerate(CUSTOM_SAP_DECOMPOSITIONS.items(), 1):
            print(f"\n[{i}] {key.upper()}")
            print(f"    Оригинальный промт: {data['original_prompt']}")
            print(f"    Этапов: {len(data['prompts_list'])}")
            print(f"    Переключения: {data['switch_prompts_steps']}")
            for j, prompt in enumerate(data['prompts_list'], 1):
                print(f"      {j}. {prompt[:60]}...")
        
        return 0
    
    # Подготовка seeds
    if args.num_seeds > 1:
        seeds = [30498 + i * 10000 for i in range(args.num_seeds)]
    else:
        seeds = args.seeds
    
    print("\n" + "🎨" * 35)
    print("CUSTOM SAP FLUX - Генерирование с готовой SAP декомпозицией")
    print("🎨" * 35)
    
    # Генерирование
    if args.all:
        print(f"\n📋 Генерирую все {len(CUSTOM_SAP_DECOMPOSITIONS)} примеров...")
        
        all_results = []
        for name, sap_data in CUSTOM_SAP_DECOMPOSITIONS.items():
            result = generate_with_custom_sap(
                sap_data,
                name,
                num_inference_steps=args.num_steps,
                height=args.height,
                width=args.width,
                seeds=seeds,
                device=args.device
            )
            
            if result:
                all_results.append(result)
        
        print(f"\n{'='*70}")
        print(f"✅ ГЕНЕРИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"{'='*70}")
        print(f"\nВсего примеров: {len(all_results)}")
        print(f"Всего изображений: {sum(r['num_images'] for r in all_results)}")
        
        return 0
    
    elif args.name:
        sap_data = CUSTOM_SAP_DECOMPOSITIONS[args.name]
        result = generate_with_custom_sap(
            sap_data,
            args.name,
            num_inference_steps=args.num_steps,
            height=args.height,
            width=args.width,
            seeds=seeds,
            device=args.device
        )
        
        if result:
            print(f"\n✅ Результаты сохранены в: {result['output_dir']}")
            return 0
        else:
            return 1
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
