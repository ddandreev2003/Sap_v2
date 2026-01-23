#!/bin/bash
# FLUX HPC - Автоматическая проверка готовности

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         FLUX HPC Image Generator - Проверка готовности      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Счетчик
CHECKS_PASSED=0
CHECKS_FAILED=0

# Функция для проверки
check_item() {
    local name="$1"
    local condition="$2"
    
    if eval "$condition" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $name"
        ((CHECKS_PASSED++))
    else
        echo -e "  ${RED}❌${NC} $name"
        ((CHECKS_FAILED++))
    fi
}

# Функция для раздела
print_section() {
    echo ""
    echo "📋 $1"
    echo "─────────────────────────────────────────────────────────────"
}

# Проверка Python
print_section "Проверка Python"
check_item "Python установлен" "command -v python3"
check_item "Python 3.10+" "python3 -c 'import sys; exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null"

# Проверка PyTorch
print_section "Проверка PyTorch"
check_item "PyTorch установлен" "python3 -c 'import torch' 2>/dev/null"
check_item "CUDA доступна (опционально)" "python3 -c 'import torch; exit(0 if torch.cuda.is_available() else 1)' 2>/dev/null || true"

# Проверка файлов
print_section "Проверка структуры файлов"
check_item "01_download_models.py существует" "[ -f 01_download_models.py ]"
check_item "02_generate_images.py существует" "[ -f 02_generate_images.py ]"
check_item "utils.py существует" "[ -f utils.py ]"
check_item "requirements.txt существует" "[ -f requirements.txt ]"
check_item "script.sbatch существует" "[ -f script.sbatch ]"
check_item "prompts.json существует" "[ -f prompts.json ]"

# Проверка документации
print_section "Проверка документации"
check_item "INDEX.md существует" "[ -f INDEX.md ]"
check_item "QUICKSTART.md существует" "[ -f QUICKSTART.md ]"
check_item "SETUP_GUIDE.md существует" "[ -f SETUP_GUIDE.md ]"
check_item "HPC_GUIDE.md существует" "[ -f HPC_GUIDE.md ]"

# Проверка директорий
print_section "Проверка директорий"
check_item "Директория runs существует" "[ -d runs ]"
check_item "Директория results существует" "[ -d results ]"
check_item "Директория models существует" "[ -d models ]"

# Результат
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    РЕЗУЛЬТАТЫ ПРОВЕРКИ                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${GREEN}✅ Пройдено: $CHECKS_PASSED${NC}"
echo -e "  ${RED}❌ Не пройдено: $CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 Все проверки пройдены! Система готова к работе!${NC}"
    echo ""
    echo "📚 Рекомендуемый путь:"
    echo ""
    echo "1. Прочитайте QUICKSTART.md или INDEX.md"
    echo "2. Установите зависимости: pip install -r requirements.txt"
    echo "3. Загрузите модель: python3 01_download_models.py --output_dir ./models"
    echo "4. Запустите на HPC: sbatch script.sbatch"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  Обнаружены проблемы. Пожалуйста, исправьте их перед использованием.${NC}"
    echo ""
    echo "🔧 Помощь:"
    echo "  1. Убедитесь что Python 3.10+ установлен"
    echo "  2. Установите зависимости: pip install -r requirements.txt"
    echo "  3. Создайте директории: bash setup_directories.sh"
    echo "  4. Прочитайте документацию: cat INDEX.md"
    echo ""
    exit 1
fi
