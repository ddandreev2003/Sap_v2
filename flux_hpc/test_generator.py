#!/usr/bin/env python3
"""
Локальный тест генератора (для отладки ДО загрузки на HPC)

Использует меньше шагов и меньшее разрешение для быстрого тестирования
"""

import argparse
import sys
from pathlib import Path

# Добавить путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from generate_images import FluxImageGenerator


def run_test(model_path: str, num_images: int = 2):
    """
    Запустить быстрый тест генератора
    
    Args:
        model_path: Путь к модели FLUX
        num_images: Количество изображений для теста
    """
    
    print("\n" + "="*60)
    print("🧪 Тест FLUX генератора")
    print("="*60)
    
    # Инициализация
    try:
        generator = FluxImageGenerator(model_path, device="cuda")
    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        return False
    
    # Тестовые промпты
    test_prompts = [
        "A beautiful sunset over mountains",
        "A futuristic city with neon lights"
    ][:num_images]
    
    print(f"\n🎨 Генерирование {num_images} тестовых изображений...")
    print(f"   📐 Размер: 512x512 (уменьшенный для теста)")
    print(f"   🔄 Шагов дифузии: 20 (уменьшено для скорости)")
    
    try:
        # Быстрое тестирование с меньшим разрешением и шагами
        images = generator.generate_images(
            prompts=test_prompts,
            num_images_per_prompt=1,
            height=512,
            width=512,
            num_inference_steps=20,
            guidance_scale=3.5
        )
        
        print(f"✅ Генерирование успешно!")
        print(f"   Сгенерировано: {len(images)} изображений")
        
        # Сохранить результаты
        output_dir = "test_results"
        generator.save_images(images, output_dir, prefix="test")
        
        print(f"✅ Результаты сохранены в: {output_dir}/")
        print(f"\n🎉 Тест пройден! Модель работает корректно.")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при генерировании: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Тест FLUX генератора")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Путь к загруженной модели FLUX"
    )
    parser.add_argument(
        "--num_images",
        type=int,
        default=2,
        help="Количество изображений для теста"
    )
    
    args = parser.parse_args()
    
    success = run_test(args.model_path, args.num_images)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
