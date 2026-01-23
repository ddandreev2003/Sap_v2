#!/bin/bash
# Пример скрипта для запуска нескольких заданий параллельно

# Этот скрипт демонстрирует как запустить несколько наборов промптов
# одновременно с разными seed'ами

set -e  # Выход при ошибке

BASE_DIR="/path/to/flux_hpc"
MODEL_PATH="/path/to/flux_hpc/models/flux_dev"

echo "🚀 Запуск batch генерации изображений"
echo "════════════════════════════════════════════════"

# Batch 1: Ландшафты
echo "📝 Batch 1: Ландшафты (seed 0)"
sbatch --job-name=flux_landscapes \
    --export=MODEL_PATH=$MODEL_PATH,SEED_BASE=0 \
    $BASE_DIR/script.sbatch

# Batch 2: Архитектура  
echo "📝 Batch 2: Архитектура (seed 100)"
sbatch --job-name=flux_architecture \
    --export=MODEL_PATH=$MODEL_PATH,SEED_BASE=100 \
    $BASE_DIR/script.sbatch

# Batch 3: Персонажи
echo "📝 Batch 3: Персонажи (seed 200)"
sbatch --job-name=flux_characters \
    --export=MODEL_PATH=$MODEL_PATH,SEED_BASE=200 \
    $BASE_DIR/script.sbatch

echo ""
echo "✅ Задания поставлены в очередь!"
echo "📊 Проверьте статус: squeue -u \$USER"
