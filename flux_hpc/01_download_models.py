#!/usr/bin/env python3
"""
Часть 1: Загрузка моделей и зависимостей (интернет доступ необходим)
Запустить в зоне с доступом в интернет один раз перед использованием на HPC
"""

import os
import torch
import argparse
from pathlib import Path
from diffusers import FluxPipeline
from transformers import CLIPTokenizer

def download_models(output_dir: str = "./models"):
    """
    Загружает FLUX модель и необходимые компоненты
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Загрузка FLUX.1-dev модели в {output_dir}...")
    
    # Загрузка основной модели
    pipeline = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16,
        cache_dir=output_dir
    )
    
    # Сохранение модели
    model_path = os.path.join(output_dir, "flux_dev")
    print(f"💾 Сохранение модели в {model_path}...")
    pipeline.save_pretrained(model_path)
    
    print(f"✅ Модель успешно загружена и сохранена!")
    print(f"📂 Используйте папку {model_path} на HPC кластере")
    
    return model_path

def main():
    parser = argparse.ArgumentParser(description="Загрузка FLUX моделей для HPC")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./models",
        help="Директория для сохранения моделей"
    )
    
    args = parser.parse_args()
    download_models(args.output_dir)

if __name__ == "__main__":
    main()
