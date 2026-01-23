#!/bin/bash
#SBATCH --job-name=flux_image_gen       # Название эксперимента
#SBATCH --error=runs/flux-%j.err        # Файл для вывода ошибок
#SBATCH --output=runs/flux-%j.log       # Файл для вывода результатов
#SBATCH --gpus=1                        # Количество запрашиваемых GPU
#SBATCH --cpus-per-task=8               # Количество CPU ядер
#SBATCH --time=2:00:00                  # Максимальное время выполнения (чч:мм:сс)
#SBATCH --constraint="[type_a|type_b|type_c|type_e]"  # Выбор типа узла (а, b, c содержат V100; e - A100)

# Загрузка модуля Python
module load Python/Anaconda_v03.2023

# Деактивация текущего окружения и активация нужного
source deactivate
source activate flux_env
# или альтернативно: conda activate flux_env

# Переход в директорию с скриптом
cd /path/to/SAP/flux_hpc

# Запуск генератора изображений
python3 02_generate_images.py \
    --model_path /path/to/models/flux_dev \
    --prompts_file ./prompts.json \
    --output_dir ./results \
    --num_without_hints 2 \
    --num_with_hints 5 \
    --height 1024 \
    --width 1024 \
    --seed_base 42

echo "✅ Работа завершена!"
