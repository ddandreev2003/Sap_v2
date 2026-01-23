#!/usr/bin/env python3
"""
Часть 2: Генерация изображений на HPC кластере (без интернета)
Использует предварительно загруженные модели
"""

import os
import json
import torch
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image
from diffusers import FluxPipeline

class FluxImageGenerator:
    """Генератор изображений на основе FLUX модели"""
    
    def __init__(self, model_path: str, device: str = "cuda"):
        """
        Инициализация генератора
        
        Args:
            model_path: Путь к загруженной модели FLUX
            device: Устройство для запуска (cuda/cpu)
        """
        self.device = device
        self.model_path = model_path
        
        print(f"🔧 Загрузка модели из {model_path}...")
        self.pipeline = FluxPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32
        )
        
        # Оптимизация памяти для HPC
        if device == "cuda":
            self.pipeline.enable_model_cpu_offload()
            # Опционально: использовать Flash Attention для ускорения
            # self.pipeline.enable_attention_slicing()
        
        self.pipeline = self.pipeline.to(device)
        print("✅ Модель загружена!")
    
    def generate_images(
        self,
        prompts: List[str],
        num_images_per_prompt: int = 1,
        seeds: List[int] = None,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 3.5
    ) -> List[Image.Image]:
        """
        Генерирует изображения для набора промптов
        
        Args:
            prompts: Список промптов для генерации
            num_images_per_prompt: Количество изображений на промпт
            seeds: Список seed'ов для воспроизводимости
            height: Высота генерируемого изображения
            width: Ширина генерируемого изображения
            num_inference_steps: Количество шагов дифузии
            guidance_scale: Масштаб гайданса
            
        Returns:
            Список сгенерированных изображений
        """
        if seeds is None:
            seeds = list(range(len(prompts) * num_images_per_prompt))
        
        # Создание генераторов с фиксированными seeds
        generators = []
        for seed in seeds:
            gen = torch.Generator(device=self.device)
            gen.manual_seed(seed)
            generators.append(gen)
        
        print(f"🎨 Генерация {len(prompts)} промптов...")
        print(f"   📐 Размер: {height}x{width}")
        print(f"   🔄 Шагов дифузии: {num_inference_steps}")
        print(f"   ⚡ Guidance scale: {guidance_scale}")
        
        with torch.no_grad():
            result = self.pipeline(
                prompt=prompts,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generators[0] if len(generators) == 1 else generators,
                num_images_per_prompt=num_images_per_prompt
            )
        
        return result.images
    
    def save_images(self, images: List[Image.Image], output_dir: str, prefix: str = ""):
        """
        Сохранение изображений в директорию
        
        Args:
            images: Список изображений для сохранения
            output_dir: Директория для сохранения
            prefix: Префикс для имен файлов
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        for i, image in enumerate(images):
            filename = f"{prefix}_{i:04d}.png" if prefix else f"image_{i:04d}.png"
            filepath = os.path.join(output_dir, filename)
            image.save(filepath)
            saved_paths.append(filepath)
            print(f"   ✅ Сохранено: {filename}")
        
        return saved_paths


def load_prompts_from_file(filepath: str) -> Dict[str, Dict]:
    """
    Загружает промпты из JSON файла
    
    Ожидаемый формат:
    {
        "prompt_name": {
            "text": "основной промпт",
            "hints": ["подсказка 1", "подсказка 2", ...]
        }
    }
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_prompts(
    generator: FluxImageGenerator,
    prompts_data: Dict[str, Dict],
    output_base_dir: str,
    num_without_hints: int = 2,
    num_with_hints: int = 5,
    seed_base: int = 42
) -> None:
    """
    Обрабатывает все промпты: генерирует изображения с и без подсказок
    
    Args:
        generator: Экземпляр FluxImageGenerator
        prompts_data: Данные промптов (из JSON)
        output_base_dir: Базовая директория для сохранения
        num_without_hints: Количество изображений БЕЗ подсказок
        num_with_hints: Количество изображений С подсказками
        seed_base: Базовое значение для seed'ов
    """
    
    for prompt_name, prompt_info in prompts_data.items():
        print(f"\n{'='*60}")
        print(f"📋 Обработка: {prompt_name}")
        print(f"{'='*60}")
        
        base_prompt = prompt_info.get("text", "")
        hints = prompt_info.get("hints", [])
        
        if not base_prompt:
            print(f"⚠️  Пропуск: нет основного промпта")
            continue
        
        # Создание директории для этого промпта
        prompt_dir = os.path.join(output_base_dir, prompt_name)
        
        # 1. Генерация без подсказок
        print(f"\n🖼️  Генерация {num_without_hints} изображений БЕЗ подсказок...")
        without_hints_dir = os.path.join(prompt_dir, "without_hints")
        
        seeds_without = list(range(seed_base, seed_base + num_without_hints))
        images_without = generator.generate_images(
            prompts=[base_prompt] * num_without_hints,
            num_images_per_prompt=1,
            seeds=seeds_without
        )
        generator.save_images(images_without, without_hints_dir, prefix="img")
        
        # 2. Генерация с подсказками
        print(f"\n💡 Генерация {num_with_hints} изображений С подсказками...")
        with_hints_dir = os.path.join(prompt_dir, "with_hints")
        
        # Создание расширенных промптов с подсказками
        extended_prompts = []
        for i in range(num_with_hints):
            hint_idx = i % len(hints) if hints else 0
            hint = hints[hint_idx] if hints else ""
            extended_prompt = f"{base_prompt}. {hint}" if hint else base_prompt
            extended_prompts.append(extended_prompt)
        
        seeds_with = list(range(seed_base + num_without_hints, seed_base + num_without_hints + num_with_hints))
        images_with = generator.generate_images(
            prompts=extended_prompts,
            num_images_per_prompt=1,
            seeds=seeds_with
        )
        generator.save_images(images_with, with_hints_dir, prefix="img_hint")
        
        print(f"\n✅ {prompt_name} завершено!")
        
        # Сохранение метаданных
        metadata = {
            "prompt": base_prompt,
            "hints": hints,
            "images_without_hints": num_without_hints,
            "images_with_hints": num_with_hints,
            "seeds_without_hints": seeds_without,
            "seeds_with_hints": seeds_with
        }
        
        metadata_path = os.path.join(prompt_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"   📝 Метаданные сохранены: {metadata_path}")


def main():
    parser = argparse.ArgumentParser(description="FLUX генератор изображений для HPC")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Путь к загруженной модели FLUX"
    )
    parser.add_argument(
        "--prompts_file",
        type=str,
        required=True,
        help="JSON файл с промптами"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./results",
        help="Директория для сохранения результатов"
    )
    parser.add_argument(
        "--num_without_hints",
        type=int,
        default=2,
        help="Количество изображений БЕЗ подсказок на промпт"
    )
    parser.add_argument(
        "--num_with_hints",
        type=int,
        default=5,
        help="Количество изображений С подсказками на промпт"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1024,
        help="Высота генерируемого изображения"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1024,
        help="Ширина генерируемого изображения"
    )
    parser.add_argument(
        "--seed_base",
        type=int,
        default=42,
        help="Базовое значение для seed'ов"
    )
    
    args = parser.parse_args()
    
    # Инициализация генератора
    generator = FluxImageGenerator(args.model_path)
    
    # Загрузка промптов
    print(f"\n📂 Загрузка промптов из {args.prompts_file}...")
    prompts_data = load_prompts_from_file(args.prompts_file)
    print(f"✅ Загружено {len(prompts_data)} промптов")
    
    # Обработка всех промптов
    process_prompts(
        generator=generator,
        prompts_data=prompts_data,
        output_base_dir=args.output_dir,
        num_without_hints=args.num_without_hints,
        num_with_hints=args.num_with_hints,
        seed_base=args.seed_base
    )
    
    print(f"\n{'='*60}")
    print("🎉 Все готово! Результаты сохранены в:", args.output_dir)
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
