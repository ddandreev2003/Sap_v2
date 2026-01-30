#!/bin/bash

# 🚀 Combined FLUX + SAP Pipeline - Installer & Quick Start
# Инсталлятор и быстрый старт для Combined FLUX + SAP Pipeline

set -e  # Exit on error

echo "=================================="
echo "🚀 Combined FLUX + SAP Pipeline"
echo "Quick Start Installer"
echo "=================================="
echo ""

# Определение цветов
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка Python
log_info "Проверка Python версии..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
log_success "Python версия: $python_version"

# Проверка наличия файлов
log_info "Проверка наличия файлов проекта..."

required_files=(
    "combined_flux_sap.py"
    "SAP_pipeline_flux.py"
    "llm_interface/llm_SAP.py"
    "prompts.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        log_success "Найден: $file"
    else
        log_error "НЕ НАЙДЕН: $file"
        exit 1
    fi
done

echo ""
log_info "Все основные файлы найдены! ✅"
echo ""

# Предложить действия
echo "=================================="
echo "📋 Доступные действия:"
echo "=================================="
echo ""
echo "1) Проверить окружение"
echo "   python check_environment.py"
echo ""
echo "2) Быстрая генерация (сравнение Direct vs SAP)"
echo "   python quick_launch.py --preset compare"
echo ""
echo "3) Только Direct FLUX (быстро)"
echo "   python quick_launch.py --preset direct-fast"
echo ""
echo "4) Только SAP с локальной моделью (без API)"
echo "   python quick_launch.py --preset local-zephyr"
echo ""
echo "5) Примеры использования"
echo "   python examples.py --list"
echo ""
echo "6) Полная документация"
echo "   Читайте: 00_START_HERE.md"
echo ""

# Предложить проверку
echo "=================================="
read -p "🔍 Хотите проверить окружение? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    log_info "Запуск проверки окружения..."
    python3 check_environment.py
    echo ""
fi

# Предложить быструю генерацию
read -p "🎨 Хотите запустить быструю генерацию? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    log_info "Запуск быстрой генерации (это займет 10-20 минут)..."
    python3 quick_launch.py --preset compare
    echo ""
    log_success "Генерация завершена!"
    echo "Результаты находятся в: results_combined/batch_*/batch_*/"
    echo ""
fi

echo "=================================="
log_success "Готово! 🎉"
echo "=================================="
echo ""
echo "Следующие шаги:"
echo "1. Прочитайте: 00_START_HERE.md"
echo "2. Используйте: python quick_launch.py --preset [название]"
echo "3. Анализируйте: python compare_results.py --batch-dir results_combined/batch_*"
echo ""
