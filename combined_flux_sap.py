"""
Combined FLUX + SAP Image Generation Pipeline
Генерирует изображения в двух режимах:
1. Direct FLUX generation - прямая генерация с базовыми промтами
2. SAP generation - генерация с декомпозицией промтов через LLM
"""

import os
import sys
import torch
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Импорты из проекта
from SAP_pipeline_flux import SapFlux
from llm_interface.llm_SAP import LLM_SAP
from diffusers import FluxPipeline

# ==================== КОНФИГУРАЦИЯ ====================
BASE_FOLDER = os.getcwd()
API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY")
RESULTS_DIR = os.path.join(BASE_FOLDER, "results_combined")

# ==================== УТИЛИТЫ ====================
def create_timestamp_dir(base_dir: str, prefix: str = "batch") -> str:
    """Создает директорию с временной меткой"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = os.path.join(base_dir, f"{prefix}_{timestamp}")
    Path(batch_dir).mkdir(parents=True, exist_ok=True)
    return batch_dir

def read_prompts_from_file(filepath: str) -> List[str]:
    """Читает промты из файла (по одному на строку)"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл промтов не найден: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    if not prompts:
        raise ValueError("Файл промтов пуст")
    
    print(f"✅ Загружено {len(prompts)} промтов из {filepath}")
    return prompts

def save_results(images, output_dir: str, prompt_name: str, image_type: str, seeds: List[int] = None):
    """Сохраняет сгенерированные изображения"""
    prompt_dir = os.path.join(output_dir, prompt_name.replace(" ", "_")[:50])
    Path(prompt_dir).mkdir(parents=True, exist_ok=True)
    
    for i, image in enumerate(images):
        if seeds and i < len(seeds):
            filename = f"{image_type}_seed_{seeds[i]}.png"
        else:
            filename = f"{image_type}_{i:03d}.png"
        
        filepath = os.path.join(prompt_dir, filename)
        image.save(filepath)
        print(f"  💾 Сохранено: {filepath}")

def save_metadata(output_dir: str, metadata: Dict, filename: str = "metadata.txt"):
    """Сохраняет метаданные генерации"""
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")

# ==================== ГЕНЕРАЦИЯ С ПОМОЩЬЮ FLUX (DIRECT) ====================
class DirectFluxGenerator:
    """Генератор изображений с прямым использованием Flux без SAP"""
    
    def __init__(self, device: str = "cuda"):
        """Инициализация генератора"""
        print("\n🔧 Инициализация Direct FLUX Generator...")
        self.device = device
        self.pipeline = None
    
    def load_model(self):
        """Загружает модель Flux"""
        print("📥 Загрузка модели black-forest-labs/FLUX.1-dev...")
        self.pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.bfloat16
        )
        self.pipeline.enable_model_cpu_offload()
        self.pipeline = self.pipeline.to(self.device)
        print("✅ Модель загружена!")
    
    def generate(
        self,
        prompts: List[str],
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 3.5,
        seeds: List[int] = None,
        num_images_per_prompt: int = 1
    ) -> Dict[str, List]:
        """Генерирует изображения для каждого промта"""
        if self.pipeline is None:
            self.load_model()
        
        if seeds is None:
            seeds = list(range(num_images_per_prompt))
        
        results = {}
        
        for prompt in prompts:
            print(f"\n🎨 Генерация для: '{prompt}'")
            
            # Создание генераторов
            generators = []
            for seed in seeds:
                gen = torch.Generator(device=self.device)
                gen.manual_seed(seed)
                generators.append(gen)
            
            try:
                # Генерация
                output = self.pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generators[0] if len(generators) == 1 else generators,
                    num_images_per_prompt=len(generators)
                )
                
                images = output.images
                results[prompt] = images
                print(f"✅ Сгенерировано {len(images)} изображений")
                
            except Exception as e:
                print(f"❌ Ошибка при генерации: {e}")
                results[prompt] = []
        
        return results

# ==================== ГЕНЕРАЦИЯ С ПОМОЩЬЮ SAP ====================
class SAPFluxGenerator:
    """Генератор изображений с использованием SAP (prompt decomposition через LLM)"""
    
    def __init__(self, llm: str = "GPT", device: str = "cuda"):
        """Инициализация генератора"""
        print("\n🔧 Инициализация SAP FLUX Generator...")
        self.device = device
        self.llm = llm
        self.pipeline = None
    
    def load_model(self):
        """Загружает модель SapFlux"""
        print("📥 Загрузка модели black-forest-labs/FLUX.1-dev (SAP версия)...")
        self.pipeline = SapFlux.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.bfloat16
        )
        self.pipeline.enable_model_cpu_offload()
        self.pipeline = self.pipeline.to(self.device)
        print("✅ Модель загружена!")
    
    def generate(
        self,
        prompts: List[str],
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 3.5,
        seeds: List[int] = None,
        num_images_per_prompt: int = 1
    ) -> Dict[str, List]:
        """Генерирует изображения с декомпозицией через LLM"""
        if self.pipeline is None:
            self.load_model()
        
        if seeds is None:
            seeds = list(range(num_images_per_prompt))
        
        results = {}
        sap_metadata = {}
        
        print(f"\n🧠 Запуск LLM для декомпозиции {len(prompts)} промтов (LLM: {self.llm})...")
        
        # Получение декомпозиции всех промтов от LLM
        sap_prompts_list = LLM_SAP(prompts, llm=self.llm, key=API_KEY)
        
        if len(sap_prompts_list) != len(prompts):
            print(f"⚠️  Ожидалось {len(prompts)} результатов, получено {len(sap_prompts_list)}")
        
        # Генерация для каждого оригинального промта
        for i, original_prompt in enumerate(prompts):
            print(f"\n🎨 Генерация SAP для: '{original_prompt}'")
            
            # Проверка корректности SAP результата
            if i >= len(sap_prompts_list) or sap_prompts_list[i] is None:
                print(f"⚠️  Не удалось получить SAP декомпозицию для промта {i+1}")
                continue
            
            sap_prompt_data = sap_prompts_list[i]
            
            # Сохранение метаданных
            sap_metadata[original_prompt] = {
                "explanation": sap_prompt_data.get("explanation", "N/A"),
                "prompts_count": len(sap_prompt_data.get("prompts_list", [])),
                "switch_steps": sap_prompt_data.get("switch_prompts_steps", [])
            }
            
            # Создание генераторов
            generators = []
            for seed in seeds:
                gen = torch.Generator(device=self.device)
                gen.manual_seed(seed)
                generators.append(gen)
            
            try:
                # Генерация с SAP
                output = self.pipeline(
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generators,
                    num_images_per_prompt=len(generators),
                    sap_prompts=sap_prompt_data
                )
                
                images = output.images
                results[original_prompt] = images
                print(f"✅ Сгенерировано {len(images)} изображений (с SAP декомпозицией)")
                
            except Exception as e:
                print(f"❌ Ошибка при SAP генерации: {e}")
                results[original_prompt] = []
        
        return results, sap_metadata

# ==================== ГЛАВНОЕ ПРИЛОЖЕНИЕ ====================
def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="Combined FLUX + SAP Image Generation Pipeline"
    )
    
    # Основные аргументы
    parser.add_argument(
        '--prompts-file',
        type=str,
        default='prompts.txt',
        help='Путь к файлу с промтами (по одному на строку)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default=RESULTS_DIR,
        help='Директория для сохранения результатов'
    )
    
    # Параметры генерации
    parser.add_argument(
        '--height',
        type=int,
        default=1024,
        help='Высота генерируемого изображения'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='Ширина генерируемого изображения'
    )
    
    parser.add_argument(
        '--num-inference-steps',
        type=int,
        default=50,
        help='Количество шагов дифузии'
    )
    
    parser.add_argument(
        '--guidance-scale',
        type=float,
        default=3.5,
        help='Масштаб гайданса'
    )
    
    parser.add_argument(
        '--seeds',
        nargs='+',
        type=int,
        default=[30498],
        help='Список seeds для генерации'
    )
    
    # Выбор режимов
    parser.add_argument(
        '--mode',
        type=str,
        choices=['direct', 'sap', 'both'],
        default='both',
        help='Режим генерации: direct (Flux), sap (SAP), both (оба)'
    )
    
    parser.add_argument(
        '--llm',
        type=str,
        choices=['GPT', 'Zephyr'],
        default='GPT',
        help='LLM для SAP декомпозиции'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        default='cuda',
        help='Устройство для генерации'
    )
    
    return parser.parse_args()

def main():
    """Главная функция"""
    args = parse_arguments()
    
    print("=" * 60)
    print("🚀 Combined FLUX + SAP Image Generation Pipeline")
    print("=" * 60)
    
    # Загрузка промтов
    try:
        prompts = read_prompts_from_file(args.prompts_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    
    # Создание директории для результатов
    batch_dir = create_timestamp_dir(args.output_dir)
    print(f"📁 Результаты будут сохранены в: {batch_dir}")
    
    # ===== РЕЖИМ DIRECT =====
    if args.mode in ['direct', 'both']:
        print("\n" + "=" * 60)
        print("ЭТАП 1: Direct FLUX Generation (без SAP)")
        print("=" * 60)
        
        direct_dir = os.path.join(batch_dir, "direct_flux")
        Path(direct_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            direct_generator = DirectFluxGenerator(device=args.device)
            direct_results = direct_generator.generate(
                prompts=prompts,
                height=args.height,
                width=args.width,
                num_inference_steps=args.num_inference_steps,
                guidance_scale=args.guidance_scale,
                seeds=args.seeds,
                num_images_per_prompt=len(args.seeds)
            )
            
            # Сохранение результатов
            print("\n💾 Сохранение результатов Direct FLUX...")
            for prompt, images in direct_results.items():
                if images:
                    save_results(images, direct_dir, prompt, "direct", args.seeds)
            
            # Сохранение метаданных
            metadata = {
                "mode": "direct_flux",
                "num_prompts": len(prompts),
                "image_size": f"{args.height}x{args.width}",
                "num_inference_steps": args.num_inference_steps,
                "guidance_scale": args.guidance_scale,
                "seeds": args.seeds
            }
            save_results_metadata(direct_dir, metadata)
            print("✅ Direct FLUX генерация завершена!")
            
        except Exception as e:
            print(f"❌ Ошибка при Direct FLUX генерации: {e}")
            import traceback
            traceback.print_exc()
    
    # ===== РЕЖИМ SAP =====
    if args.mode in ['sap', 'both']:
        print("\n" + "=" * 60)
        print("ЭТАП 2: SAP Generation (с LLM декомпозицией)")
        print("=" * 60)
        
        sap_dir = os.path.join(batch_dir, "sap_flux")
        Path(sap_dir).mkdir(parents=True, exist_ok=True)
        
        try:
            sap_generator = SAPFluxGenerator(llm=args.llm, device=args.device)
            sap_results, sap_metadata = sap_generator.generate(
                prompts=prompts,
                height=args.height,
                width=args.width,
                num_inference_steps=args.num_inference_steps,
                guidance_scale=args.guidance_scale,
                seeds=args.seeds,
                num_images_per_prompt=len(args.seeds)
            )
            
            # Сохранение результатов
            print("\n💾 Сохранение результатов SAP FLUX...")
            for prompt, images in sap_results.items():
                if images:
                    save_results(images, sap_dir, prompt, "sap", args.seeds)
            
            # Сохранение метаданных SAP
            metadata = {
                "mode": "sap_flux",
                "llm": args.llm,
                "num_prompts": len(prompts),
                "image_size": f"{args.height}x{args.width}",
                "num_inference_steps": args.num_inference_steps,
                "guidance_scale": args.guidance_scale,
                "seeds": args.seeds,
                "sap_details": str(sap_metadata)
            }
            save_results_metadata(sap_dir, metadata)
            print("✅ SAP FLUX генерация завершена!")
            
        except Exception as e:
            print(f"❌ Ошибка при SAP FLUX генерации: {e}")
            import traceback
            traceback.print_exc()
    
    # Завершение
    print("\n" + "=" * 60)
    print("🎉 Генерация завершена!")
    print(f"📁 Все результаты находятся в: {batch_dir}")
    print("=" * 60)

def save_results_metadata(output_dir: str, metadata: Dict):
    """Вспомогательная функция для сохранения метаданных"""
    filepath = os.path.join(output_dir, "metadata.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")

if __name__ == "__main__":
    main()
