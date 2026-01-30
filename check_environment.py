#!/usr/bin/env python3
"""
Environment readiness checker for Combined FLUX + SAP Pipeline
Проверка готовности окружения к запуску
"""

import sys
import os
import json
from pathlib import Path
from typing import Tuple, Dict, List

class EnvironmentChecker:
    """Проверка окружения для запуска pipeline"""
    
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Проверка версии Python"""
        version = sys.version_info
        required_version = (3, 9)
        
        if version >= required_version:
            msg = f"✅ Python {version.major}.{version.minor}.{version.micro} (требуется {required_version[0]}.{required_version[1]}+)"
            self.checks_passed.append(msg)
            return True, msg
        else:
            msg = f"❌ Python {version.major}.{version.minor} (требуется {required_version[0]}.{required_version[1]}+)"
            self.checks_failed.append(msg)
            return False, msg
    
    def check_gpu_availability(self) -> Tuple[bool, str]:
        """Проверка доступности GPU"""
        try:
            import torch
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / 1e9
                msg = f"✅ CUDA доступна ({device_count} GPU): {device_name} ({vram:.1f}GB VRAM)"
                
                if vram < 16:
                    warn = f"⚠️  VRAM недостаточно: {vram:.1f}GB (минимум 16GB рекомендуется)"
                    self.warnings.append(warn)
                
                self.checks_passed.append(msg)
                return True, msg
            else:
                msg = "⚠️  CUDA недоступна (будет использован CPU - медленно!)"
                self.warnings.append(msg)
                return False, msg
        except Exception as e:
            msg = f"❌ Ошибка при проверке GPU: {e}"
            self.checks_failed.append(msg)
            return False, msg
    
    def check_required_packages(self) -> Tuple[bool, List[str]]:
        """Проверка обязательных пакетов"""
        required_packages = {
            'torch': 'PyTorch',
            'diffusers': 'Diffusers',
            'transformers': 'Transformers',
            'PIL': 'Pillow',
            'requests': 'Requests'
        }
        
        all_installed = True
        messages = []
        
        for package, friendly_name in required_packages.items():
            try:
                __import__(package)
                msg = f"✅ {friendly_name} установлен"
                self.checks_passed.append(msg)
                messages.append(msg)
            except ImportError:
                msg = f"❌ {friendly_name} НЕ установлен"
                self.checks_failed.append(msg)
                messages.append(msg)
                all_installed = False
        
        return all_installed, messages
    
    def check_optional_packages(self) -> Dict[str, bool]:
        """Проверка опциональных пакетов"""
        optional = {
            'sentencepiece': 'Sentence Piece (для LLM)',
            'bitsandbytes': 'BitsAndBytes (оптимизация)',
            'scipy': 'SciPy (общие функции)'
        }
        
        optional_status = {}
        
        for package, friendly_name in optional.items():
            try:
                __import__(package)
                msg = f"✅ {friendly_name} установлен"
                self.checks_passed.append(msg)
                optional_status[package] = True
            except ImportError:
                msg = f"⚠️  {friendly_name} НЕ установлен (опционально)"
                self.warnings.append(msg)
                optional_status[package] = False
        
        return optional_status
    
    def check_project_files(self) -> Tuple[bool, List[str]]:
        """Проверка наличия необходимых файлов проекта"""
        required_files = [
            'combined_flux_sap.py',
            'SAP_pipeline_flux.py',
            'llm_interface/llm_SAP.py',
            'prompts.txt'
        ]
        
        all_exist = True
        messages = []
        
        for file in required_files:
            if os.path.exists(file):
                msg = f"✅ {file} найден"
                self.checks_passed.append(msg)
                messages.append(msg)
            else:
                msg = f"❌ {file} НЕ найден"
                self.checks_failed.append(msg)
                messages.append(msg)
                all_exist = False
        
        return all_exist, messages
    
    def check_output_directory(self) -> Tuple[bool, str]:
        """Проверка директории для результатов"""
        output_dir = 'results_combined'
        
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            # Проверка прав доступа
            test_file = Path(output_dir) / '.writetest'
            test_file.touch()
            test_file.unlink()
            
            msg = f"✅ Директория {output_dir} доступна для записи"
            self.checks_passed.append(msg)
            return True, msg
        except Exception as e:
            msg = f"❌ Ошибка с директорией {output_dir}: {e}"
            self.checks_failed.append(msg)
            return False, msg
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Проверка переменных окружения для API"""
        api_keys = {}
        
        # OpenAI API
        if os.getenv('OPENAI_API_KEY'):
            msg = "✅ OPENAI_API_KEY установлен"
            self.checks_passed.append(msg)
            api_keys['openai'] = True
        else:
            msg = "⚠️  OPENAI_API_KEY НЕ установлен (нужен для GPT режима)"
            self.warnings.append(msg)
            api_keys['openai'] = False
        
        # Hugging Face Token
        if os.getenv('HF_TOKEN'):
            msg = "✅ HF_TOKEN установлен"
            self.checks_passed.append(msg)
            api_keys['hf'] = True
        else:
            msg = "⚠️  HF_TOKEN НЕ установлен (опционально)"
            self.warnings.append(msg)
            api_keys['hf'] = False
        
        return api_keys
    
    def check_disk_space(self) -> Tuple[bool, str]:
        """Проверка свободного места на диске"""
        import shutil
        
        try:
            stat = shutil.disk_usage('.')
            free_gb = stat.free / (1024 ** 3)
            
            if free_gb > 100:
                msg = f"✅ Свободное место: {free_gb:.1f}GB (достаточно)"
                self.checks_passed.append(msg)
                return True, msg
            elif free_gb > 50:
                msg = f"⚠️  Свободное место: {free_gb:.1f}GB (минимально)"
                self.warnings.append(msg)
                return True, msg
            else:
                msg = f"❌ Недостаточно свободного места: {free_gb:.1f}GB (требуется 50GB+)"
                self.checks_failed.append(msg)
                return False, msg
        except Exception as e:
            msg = f"⚠️  Не удалось проверить диск: {e}"
            self.warnings.append(msg)
            return True, msg
    
    def check_memory(self) -> Tuple[bool, str]:
        """Проверка доступной оперативной памяти"""
        try:
            import psutil
            
            total_memory_gb = psutil.virtual_memory().total / (1024 ** 3)
            available_memory_gb = psutil.virtual_memory().available / (1024 ** 3)
            
            if total_memory_gb >= 32:
                msg = f"✅ RAM: {total_memory_gb:.1f}GB (доступно: {available_memory_gb:.1f}GB)"
                self.checks_passed.append(msg)
                return True, msg
            elif total_memory_gb >= 16:
                msg = f"⚠️  RAM: {total_memory_gb:.1f}GB (минимально, рекомендуется 32GB)"
                self.warnings.append(msg)
                return True, msg
            else:
                msg = f"❌ RAM: {total_memory_gb:.1f}GB (недостаточно, требуется 16GB+)"
                self.checks_failed.append(msg)
                return False, msg
        except ImportError:
            msg = "⚠️  psutil не установлен, пропускаем проверку памяти"
            self.warnings.append(msg)
            return True, msg
    
    def generate_report(self) -> str:
        """Генерация полного отчета"""
        report = []
        report.append("=" * 70)
        report.append("🔍 ENVIRONMENT READINESS CHECK")
        report.append("=" * 70)
        report.append("")
        
        # Выполнение всех проверок
        report.append("📋 ПРОВЕРКИ:\n")
        
        # Python
        self.check_python_version()
        
        # GPU
        self.check_gpu_availability()
        
        # Required packages
        all_required, pkg_msgs = self.check_required_packages()
        for msg in pkg_msgs:
            pass  # Уже добавлено в check_passed/check_failed
        
        # Optional packages
        self.check_optional_packages()
        
        # Project files
        all_files, file_msgs = self.check_project_files()
        
        # Output directory
        self.check_output_directory()
        
        # API keys
        api_status = self.check_api_keys()
        
        # Disk space
        self.check_disk_space()
        
        # Memory
        self.check_memory()
        
        # Вывод результатов
        if self.checks_passed:
            report.append("✅ УСПЕШНЫЕ ПРОВЕРКИ:")
            for check in self.checks_passed:
                report.append(f"  {check}")
            report.append("")
        
        if self.checks_failed:
            report.append("❌ ОШИБКИ:")
            for check in self.checks_failed:
                report.append(f"  {check}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.warnings:
                report.append(f"  {warning}")
            report.append("")
        
        # Рекомендации
        report.append("=" * 70)
        report.append("💡 РЕКОМЕНДАЦИИ:")
        report.append("")
        
        if not api_status.get('openai'):
            report.append("  1. Установите OPENAI_API_KEY для использования GPT в SAP режиме:")
            report.append("     export OPENAI_API_KEY=\"sk-...\"")
            report.append("")
        
        if self.checks_failed:
            report.append("  2. Установите недостающие пакеты:")
            report.append("     pip install -r requirements.txt")
            report.append("")
        
        # Статус готовности
        report.append("=" * 70)
        if self.checks_failed:
            report.append("❌ ОКРУЖЕНИЕ НЕ ГОТОВО")
            report.append("")
            report.append("Действия для решения проблем:")
            report.append("  1. Установите недостающие пакеты: pip install -r requirements.txt")
            report.append("  2. Проверьте наличие всех файлов проекта")
            report.append("  3. Убедитесь, что используется правильный Python интерпретатор")
            status = False
        elif self.warnings and not api_status.get('openai'):
            report.append("⚠️  ОКРУЖЕНИЕ ГОТОВО (ограниченно)")
            report.append("")
            report.append("Можно запустить:")
            report.append("  • Direct FLUX режим: python combined_flux_sap.py --mode direct")
            report.append("  • SAP с Zephyr: python combined_flux_sap.py --mode sap --llm Zephyr")
            report.append("")
            report.append("Для полной функциональности установите OPENAI_API_KEY")
            status = True
        else:
            report.append("✅ ОКРУЖЕНИЕ ГОТОВО!")
            report.append("")
            report.append("Вы можете запустить любой из режимов:")
            report.append("  • Быстрое тестирование: python quick_launch.py --preset compare")
            report.append("  • Кастомная генерация: python combined_flux_sap.py ...")
            report.append("  • Анализ результатов: python compare_results.py --batch-dir results_combined/batch_*")
            status = True
        
        report.append("=" * 70)
        
        return "\n".join(report), status

def main():
    """Главная функция"""
    checker = EnvironmentChecker()
    report, status = checker.generate_report()
    
    print(report)
    
    # Сохранение отчета
    report_file = 'environment_check_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📁 Отчет сохранен: {report_file}")
    
    return 0 if status else 1

if __name__ == "__main__":
    sys.exit(main())
