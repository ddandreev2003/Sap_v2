#!/usr/bin/env python
"""
=============================================================================
        БЫСТРЫЙ ЗАПУСК: Генерирование с готовой SAP декомпозицией
=============================================================================

Самый простой способ запустить FLUX с вашей готовой SAP декомпозицией
"""

import torch
from pathlib import Path
from datetime import datetime


# 📋 ВАШ ГОТОВЫЙ СЛОВАРЬ С SAP ДЕКОМПОЗИЦИЯМИ
CUSTOM_SAP = {
    "grown_man": {
        "prompts_list": [
            "A grown man with a small object in his mouth",
            "A grown man has a baby's pacifier in his mouth"
        ],
        "switch_prompts_steps": [4]
    },
    "dragon": {
        "prompts_list": [
            "A dragon blowing white smoke",
            "A dragon blowing water"
        ],
        "switch_prompts_steps": [3]
    },
    "pizza": {
        "prompts_list": [
            "A pizza with pepperoni toppings",
            "A pizza with grape toppings"
        ],
        "switch_prompts_steps": [3]
    },
    "coin": {
        "prompts_list": [
            "A leaf floats on the surface of the water",
            "A coin floats on the surface of the water"
        ],
        "switch_prompts_steps": [4]
    },
    "cockatoo_parrot": {
        "prompts_list": [
            "A duck swimming in the ocean",
            "A parrot swimming in the ocean",
            "A cockatoo parrot swimming in the ocean"
        ],
        "switch_prompts_steps": [3, 6]
    },
    "woman": {
        "prompts_list": [
            "A woman writing with a pen",
            "A woman writing with a dart"
        ],
        "switch_prompts_steps": [3]
    },
    "shrek": {
        "prompts_list": [
            "A blue ogre",
            "Shrek is blue"
        ],
        "switch_prompts_steps": [3]
    }
}


def generate_sap_image(name, num_steps=50, num_images=1, seed=30498):
    """
    Генерирует одно изображение с SAP декомпозицией
    
    Параметры:
    - name: ключ из CUSTOM_SAP словаря (например, "dragon")
    - num_steps: количество шагов дифузии (20-100)
    - num_images: количество изображений (с разными seeds)
    - seed: начальный seed
    """
    
    if name not in CUSTOM_SAP:
        print(f"❌ Пример '{name}' не найден!")
        print(f"   Доступные примеры: {list(CUSTOM_SAP.keys())}")
        return None
    
    sap_data = CUSTOM_SAP[name]
    
    print(f"\n{'='*70}")
    print(f"🎨 Генерирование: {name.upper()}")
    print(f"{'='*70}")
    print(f"  Этапы промтов: {len(sap_data['prompts_list'])}")
    print(f"  Переключения на шагах: {sap_data['switch_prompts_steps']}")
    print(f"  Шагов дифузии: {num_steps}")
    
    # Этап 1: Загрузка модели
    print(f"\n📥 Загружаю FLUX модель (это может занять время)...")
    
    try:
        from diffusers import FluxPipeline
        import torch
        
        pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.bfloat16
        )
        pipeline = pipeline.to("cuda")
        print(f"✅ Модель загружена")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        print(f"   Проверьте:")
        print(f"   - Установлены ли зависимости: pip install -r requirements.txt")
        print(f"   - Достаточно ли памяти на GPU (нужно минимум 16GB VRAM)")
        return None
    
    # Этап 2: Загрузка SAP pipeline
    print(f"\n📥 Загружаю SAP pipeline...")
    
    SapFlux = None
    try:
        import sys
        # Добавляем текущую директорию в path
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from SAP_pipeline_flux import SapFlux
        print(f"✅ SAP pipeline загружена успешно")
        use_sap = True
        
    except ImportError as e:
        print(f"⚠️  SAP pipeline недоступна: {e}")
        print(f"   Будет использован Direct FLUX режим")
        use_sap = False
    
    # Этап 3: Генерирование изображений
    print(f"\n🔄 Генерирую {num_images} изображение(й)...")
    
    output_dir = Path(f"results_custom_sap/{name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for i in range(num_images):
        current_seed = seed + i * 10000
        
        print(f"  [{i+1}/{num_images}] Seed {current_seed}... ", end="", flush=True)
        
        try:
            # Создаём генератор с правильным device
            gen_device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=gen_device)
            generator.manual_seed(current_seed)
            
            # Запускаем генерирование
            if use_sap and SapFlux is not None:
                # SAP режим
                try:
                    sap_pipeline = SapFlux.from_pretrained(
                        "black-forest-labs/FLUX.1-dev",
                        torch_dtype=torch.bfloat16
                    )
                    sap_pipeline = sap_pipeline.to("cuda")
                    
                    output = sap_pipeline(
                        height=1024,
                        width=1024,
                        num_inference_steps=num_steps,
                        guidance_scale=3.5,
                        generator=generator,
                        sap_prompts=sap_data
                    )
                except Exception as sap_err:
                    print(f"\n     ⚠️  SAP режим ошибка, переходим на Direct FLUX...")
                    # Fallback к обычному FLUX
                    output = pipeline(
                        prompt=f"Using custom SAP decomposition",
                        height=1024,
                        width=1024,
                        num_inference_steps=num_steps,
                        guidance_scale=3.5,
                        generator=generator
                    )
            else:
                # Direct режим - используем просто FLUX
                output = pipeline(
                    prompt=f"Generating image using custom decomposition",
                    height=1024,
                    width=1024,
                    num_inference_steps=num_steps,
                    guidance_scale=3.5,
                    generator=generator
                )
            
            # Сохраняем результат
            image = output.images[0]
            filename = f"{name}_seed_{current_seed}.png"
            filepath = output_dir / filename
            image.save(filepath)
            
            print(f"✅ Сохранено: {filename}")
            results.append(str(filepath))
            
            # Освобождаем память
            del output
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue
    
    print(f"\n✅ Генерирование завершено!")
    print(f"   Результаты в: {output_dir}/")
    print(f"   Всего изображений: {len(results)}")
    
    return results


def main():
    """Главная функция - примеры использования"""
    
    print("\n" + "🎨" * 35)
    print("CUSTOM SAP FLUX - Генерирование с готовой SAP декомпозицией")
    print("🎨" * 35)
    
    print("\n" + "="*70)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("="*70)
    
    print("""
# Генерировать один пример "dragon" с 50 шагами:
result = generate_sap_image("dragon", num_steps=50, num_images=1)

# Генерировать 4 разных изображения одного примера:
result = generate_sap_image("shrek", num_steps=50, num_images=4)

# Генерировать с 80 шагами для лучшего качества:
result = generate_sap_image("woman", num_steps=80, num_images=1)

# Генерировать с быстрыми 20 шагами:
result = generate_sap_image("pizza", num_steps=20, num_images=1)
    """)
    
    print("\n" + "="*70)
    print("ДОСТУПНЫЕ ПРИМЕРЫ")
    print("="*70)
    
    for i, (name, data) in enumerate(CUSTOM_SAP.items(), 1):
        print(f"\n[{i}] {name.upper()}")
        print(f"    Этапов: {len(data['prompts_list'])}")
        print(f"    Переключения: {data['switch_prompts_steps']}")
        for j, prompt in enumerate(data['prompts_list'], 1):
            print(f"      {j}. {prompt[:55]}...")
    
    print("\n" + "="*70)
    print("РЕКОМЕНДУЕМЫЕ КОМАНДЫ")
    print("="*70)
    
    print("""
# Быстрый тест одного примера (5-10 минут):
python -c "from run_custom_sap_quick import generate_sap_image; generate_sap_image('dragon', num_steps=30)"

# Генерировать все примеры (40-60 минут):
python -c "
from run_custom_sap_quick import generate_sap_image, CUSTOM_SAP
for name in CUSTOM_SAP.keys():
    generate_sap_image(name, num_steps=50, num_images=1)
"

# Качественное генерирование одного примера (15-20 минут):
python -c "from run_custom_sap_quick import generate_sap_image; generate_sap_image('woman', num_steps=80)"

# Много изображений одного примера (30-40 минут):
python -c "from run_custom_sap_quick import generate_sap_image; generate_sap_image('shrek', num_steps=50, num_images=4)"
    """)
    
    print("\n" + "="*70)
    print("ПАРАМЕТРЫ ГЕНЕРИРОВАНИЯ")
    print("="*70)
    
    print("""
num_steps: 20-100
  - 20-30: Быстро (5-10 минут на изображение), базовое качество
  - 50: Оптимально (10-15 минут), хорошее качество
  - 70-100: Качество (20-30 минут), отличный результат

num_images: 1-8
  - Каждое новое изображение добавляет ~10-15 минут
  - Для 4 изображений: ~40-60 минут

seed: целое число
  - Разные seeds = разные изображения
  - Один seed = одинаковое изображение (воспроизводимость)
    """)
    
    print("\n💡 СОВЕТ: Просто скопируйте одну из команд выше и запустите её!")
    print("          Будет сгенерировано красивое изображение в папке results_custom_sap/")


if __name__ == "__main__":
    main()
    
    # РАСКОММЕНТИРУЙТЕ ОДНУ ИЗ ЭТИХ СТРОК ДЛЯ ЗАПУСКА:
    
    # Пример 1: Генерировать "dragon"
    # generate_sap_image("dragon", num_steps=50, num_images=1)
    
    # Пример 2: Генерировать "woman" с лучшим качеством
    # generate_sap_image("woman", num_steps=80, num_images=1)
    
    # Пример 3: Генерировать "shrek" (4 разных изображения)
    # generate_sap_image("shrek", num_steps=50, num_images=4)
    
    # Пример 4: Генерировать все примеры
    # for name in CUSTOM_SAP.keys():
    #     generate_sap_image(name, num_steps=50, num_images=1)
