#!/usr/bin/env python
"""
=============================================================================
                        СИСТЕМА ТЕСТИРОВАНИЯ
=============================================================================

Проверяет целостность и функциональность всех компонентов системы
"""

import os
import sys
import json
from pathlib import Path


def test_imports():
    """Тест 1: Проверка импортов"""
    print("\n" + "=" * 70)
    print("ТЕСТ 1: ПРОВЕРКА ИМПОРТОВ")
    print("=" * 70)
    
    tests = [
        ("torch", "PyTorch"),
        ("diffusers", "Diffusers"),
        ("transformers", "Transformers"),
        ("PIL", "Pillow"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
    ]
    
    all_ok = True
    for module_name, display_name in tests:
        try:
            __import__(module_name)
            print(f"✅ {display_name:<15} - OK")
        except ImportError:
            print(f"❌ {display_name:<15} - MISSING")
            all_ok = False
    
    return all_ok


def test_files():
    """Тест 2: Проверка файлов"""
    print("\n" + "=" * 70)
    print("ТЕСТ 2: ПРОВЕРКА ФАЙЛОВ")
    print("=" * 70)
    
    required_files = [
        "combined_flux_sap.py",
        "SAP_pipeline_flux.py",
        "llm_interface/llm_SAP.py",
        "generate_sap_prompts.py",
        "sap_prompts_loader.py",
        "workflow_example.py",
        "prompts.txt",
        "requirements.txt",
    ]
    
    optional_files = [
        "SAP_prompts.json",
        "config.json",
        "QUICKSTART.md",
        "PREGENERATION_WORKFLOW.md",
    ]
    
    all_ok = True
    
    print("\n📋 ОБЯЗАТЕЛЬНЫЕ файлы:")
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path:<40} - НАЙДЕН")
        else:
            print(f"❌ {file_path:<40} - НЕ НАЙДЕН")
            all_ok = False
    
    print("\n📋 ОПЦИОНАЛЬНЫЕ файлы:")
    for file_path in optional_files:
        if Path(file_path).exists():
            print(f"✅ {file_path:<40} - НАЙДЕН")
        else:
            print(f"⚠️  {file_path:<40} - не найден (создастся при использовании)")
    
    return all_ok


def test_prompts():
    """Тест 3: Проверка файла промтов"""
    print("\n" + "=" * 70)
    print("ТЕСТ 3: ПРОВЕРКА ФАЙЛА ПРОМТОВ")
    print("=" * 70)
    
    if not Path("prompts.txt").exists():
        print("❌ Файл prompts.txt не найден!")
        return False
    
    try:
        with open("prompts.txt", "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Файл найден")
        print(f"✅ Количество промтов: {len(prompts)}")
        
        if len(prompts) > 0:
            print(f"✅ Минимальная длина: {min(len(p) for p in prompts)} символов")
            print(f"✅ Максимальная длина: {max(len(p) for p in prompts)} символов")
            print(f"\n📝 Примеры промтов:")
            for i, prompt in enumerate(prompts[:3], 1):
                print(f"  {i}. {prompt[:70]}...")
            return True
        else:
            print("❌ Файл пуст!")
            return False
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return False


def test_sap_prompts():
    """Тест 4: Проверка SAP_prompts.json (если существует)"""
    print("\n" + "=" * 70)
    print("ТЕСТ 4: ПРОВЕРКА SAP_prompts.json")
    print("=" * 70)
    
    if not Path("SAP_prompts.json").exists():
        print("⚠️  Файл SAP_prompts.json не найден (создастся при использовании)")
        return True
    
    try:
        with open("SAP_prompts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"✅ Файл найден и валиден")
        
        if "metadata" in data:
            meta = data["metadata"]
            print(f"✅ Всего промтов: {meta.get('total_prompts', 'N/A')}")
            print(f"✅ Успешных: {meta.get('successful', 'N/A')}")
            print(f"✅ Ошибок: {meta.get('failed', 'N/A')}")
            print(f"✅ LLM модель: {meta.get('llm_model', 'N/A')}")
        
        if "prompts" in data and len(data["prompts"]) > 0:
            first = data["prompts"][0]
            if first.get("sap_decomposition"):
                print(f"✅ SAP декомпозиции присутствуют")
            else:
                print(f"⚠️  SAP декомпозиции отсутствуют")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка при парсинге JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return False


def test_class_imports():
    """Тест 5: Проверка импортов классов"""
    print("\n" + "=" * 70)
    print("ТЕСТ 5: ПРОВЕРКА ИМПОРТОВ КЛАССОВ")
    print("=" * 70)
    
    tests = [
        ("SAP_pipeline_flux", "SapFluxPipeline", "SAP Pipeline"),
        ("combined_flux_sap", "DirectFluxGenerator", "Direct FLUX Generator"),
        ("combined_flux_sap", "SAPFluxGenerator", "SAP FLUX Generator"),
        ("sap_prompts_loader", "SAPPromptsLoader", "SAP Prompts Loader"),
    ]
    
    all_ok = True
    for module_name, class_name, display_name in tests:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print(f"✅ {display_name:<30} - OK")
        except (ImportError, AttributeError) as e:
            print(f"❌ {display_name:<30} - ERROR: {e}")
            all_ok = False
    
    return all_ok


def test_environment():
    """Тест 6: Проверка окружения"""
    print("\n" + "=" * 70)
    print("ТЕСТ 6: ПРОВЕРКА ОКРУЖЕНИЯ")
    print("=" * 70)
    
    # Проверка CUDA
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"{'✅' if cuda_available else '⚠️ '} CUDA доступна: {cuda_available}")
        if cuda_available:
            print(f"  - GPU: {torch.cuda.get_device_name(0)}")
            print(f"  - Памяти: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    except Exception as e:
        print(f"⚠️  Ошибка при проверке CUDA: {e}")
    
    # Проверка API ключей
    api_key_set = "OPENAI_API_KEY" in os.environ
    print(f"{'✅' if api_key_set else '⚠️ '} OPENAI_API_KEY установлен: {api_key_set}")
    
    if not api_key_set:
        print("  💡 Совет: установите переменную окружения для использования GPT")
        print("     Linux/Mac: export OPENAI_API_KEY='sk-...'")
        print("     Windows:   set OPENAI_API_KEY=sk-...")
    
    return True


def test_config():
    """Тест 7: Проверка конфигурации"""
    print("\n" + "=" * 70)
    print("ТЕСТ 7: ПРОВЕРКА КОНФИГУРАЦИИ")
    print("=" * 70)
    
    if not Path("config.json").exists():
        print("⚠️  config.json не найден (будут использованы значения по умолчанию)")
        return True
    
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"✅ config.json найден и валиден")
        print(f"\n📝 Ключевые параметры:")
        for key, value in config.items():
            if isinstance(value, dict):
                print(f"  - {key}:")
                for k, v in value.items():
                    print(f"      {k}: {v}")
            else:
                print(f"  - {key}: {value}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка при парсинге config.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при чтении config.json: {e}")
        return False


def test_directories():
    """Тест 8: Проверка директорий"""
    print("\n" + "=" * 70)
    print("ТЕСТ 8: ПРОВЕРКА ДИРЕКТОРИЙ")
    print("=" * 70)
    
    directories = [
        "llm_interface",
        "benchmarks",
        "flux_hpc",
        "images",
    ]
    
    for dir_name in directories:
        if Path(dir_name).exists():
            print(f"✅ {dir_name:<20} - существует")
        else:
            print(f"⚠️  {dir_name:<20} - не найдена (создастся при использовании)")
    
    return True


def main():
    """Главная функция тестирования"""
    print("\n" + "🧪" * 35)
    print("СИСТЕМА ТЕСТИРОВАНИЯ - COMBINED FLUX + SAP PIPELINE")
    print("🧪" * 35)
    
    tests = [
        ("Импорты", test_imports),
        ("Файлы", test_files),
        ("Промты", test_prompts),
        ("SAP JSON", test_sap_prompts),
        ("Импорты классов", test_class_imports),
        ("Окружение", test_environment),
        ("Конфигурация", test_config),
        ("Директории", test_directories),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Исключение в тесте '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Финальный отчет
    print("\n" + "=" * 70)
    print("ФИНАЛЬНЫЙ ОТЧЕТ")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} - {test_name}")
    
    print("-" * 70)
    print(f"Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система готова к использованию.")
        print("\n💡 Следующий шаг:")
        print("   python workflow_example.py --show-options")
        print("   python workflow_example.py --step 1 --llm GPT")
        return 0
    else:
        print(f"\n❌ ОШИБКИ: {total - passed} тестов не пройдено")
        print("   Устраните проблемы и повторите тестирование")
        return 1


if __name__ == "__main__":
    sys.exit(main())
