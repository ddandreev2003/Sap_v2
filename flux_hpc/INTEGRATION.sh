#!/bin/bash
# Скрипт для интеграции flux_hpc в проект SAP

echo "🔧 Интеграция FLUX HPC генератора в проект SAP"
echo "════════════════════════════════════════════════"

# Проверить что мы в правильной директории
if [ ! -d "flux_hpc" ]; then
    echo "❌ Ошибка: директория flux_hpc не найдена"
    echo "   Запустите скрипт из директории SAP/"
    exit 1
fi

# Создать основные директории
echo "📁 Создание директорий..."
mkdir -p flux_hpc/runs
mkdir -p flux_hpc/results
mkdir -p flux_hpc/models

echo "✅ Директории созданы:"
echo "   - flux_hpc/runs/     (для логов и ошибок)"
echo "   - flux_hpc/results/  (для результатов)"
echo "   - flux_hpc/models/   (для моделей)"

echo ""
echo "📋 Проверка файлов..."

files=(
    "01_download_models.py"
    "02_generate_images.py"
    "script.sbatch"
    "download_models.sbatch"
    "prompts.json"
    "requirements.txt"
    "utils.py"
    "setup_directories.sh"
)

for file in "${files[@]}"; do
    if [ -f "flux_hpc/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (ОТСУТСТВУЕТ)"
    fi
done

echo ""
echo "📚 Документация:"
if [ -f "flux_hpc/QUICKSTART.md" ]; then
    echo "   ✅ QUICKSTART.md (быстрый старт)"
fi
if [ -f "flux_hpc/SETUP_GUIDE.md" ]; then
    echo "   ✅ SETUP_GUIDE.md (полное руководство)"
fi
if [ -f "flux_hpc/README.md" ]; then
    echo "   ✅ README.md (технические детали)"
fi

echo ""
echo "════════════════════════════════════════════════"
echo "✅ Интеграция завершена!"
echo ""
echo "🚀 Следующие шаги:"
echo ""
echo "1. ЛОКАЛЬНО (с интернетом):"
echo "   cd flux_hpc"
echo "   conda create -n flux_env python=3.10"
echo "   conda activate flux_env"
echo "   pip install -r requirements.txt"
echo ""
echo "2. Загрузить модель:"
echo "   python3 01_download_models.py --output_dir ./models"
echo ""
echo "3. На HPC кластере:"
echo "   sbatch script.sbatch"
echo ""
echo "📖 Документация в flux_hpc/QUICKSTART.md"
echo "════════════════════════════════════════════════"
