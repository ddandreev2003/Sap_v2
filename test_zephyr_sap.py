#!/usr/bin/env python
"""
=============================================================================
                    ТЕСТИРОВАНИЕ ZEPHYR SAP ДЕКОМПОЗИЦИИ
=============================================================================

Диагностический скрипт для проверки работы Zephyr с SAP
"""

import sys
import os
from pathlib import Path


def test_zephyr_sap():
    """Тест SAP декомпозиции с Zephyr"""
    print("\n" + "=" * 70)
    print("ТЕСТ: SAP ДЕКОМПОЗИЦИЯ С ZEPHYR 7B")
    print("=" * 70)
    
    # Test prompts - разнообразный набор
    test_prompts = [
        "A serene landscape with mountains and a crystal clear lake at sunset",
        "A horse riding a bicycle",
        "A cat playing the piano",
        "A polar bear in a desert",
    ]
    
    print(f"\n📋 Тестовые промты ({len(test_prompts)} штук):")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"  {i}. {prompt}")
    
    print("\n🚀 Загружаю Zephyr модель (это может занять минуту)...")
    
    try:
        from llm_interface.llm_SAP import LLM_SAP
        
        print("\n🔄 Вызываю LLM_SAP с Zephyr...")
        results = LLM_SAP(test_prompts, llm='Zephyr')
        
        print("\n" + "=" * 70)
        print("РЕЗУЛЬТАТЫ")
        print("=" * 70)
        
        for i, (prompt, result) in enumerate(zip(test_prompts, results), 1):
            print(f"\n[Промт {i}] {prompt[:60]}...")
            
            if result:
                print(f"  ✅ Декомпозиция получена")
                print(f"     - Объяснение: {result.get('explanation', 'N/A')[:80]}...")
                prompts_list = result.get('prompts_list', [])
                switches = result.get('switch_prompts_steps', [])
                print(f"     - Этапов: {len(prompts_list)}")
                print(f"     - Переключения: {switches}")
                
                if len(prompts_list) > 0:
                    print(f"     - Этап 1: {prompts_list[0][:60]}...")
                    if len(prompts_list) > 1:
                        print(f"     - Этап 2: {prompts_list[1][:60]}...")
            else:
                print(f"  ❌ Не удалось получить декомпозицию")
        
        print("\n" + "=" * 70)
        print("АНАЛИЗ")
        print("=" * 70)
        
        successful = sum(1 for r in results if r and r.get('prompts_list'))
        total = len(results)
        
        print(f"✅ Успешных: {successful}/{total}")
        
        if successful == total:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Zephyr работает корректно.")
            return 0
        else:
            print(f"\n⚠️  Пройдено {successful}/{total} тестов")
            print("\n💡 Советы:")
            print("   - Увеличьте max_new_tokens в load_Zephyr_pipeline()")
            print("   - Уменьшите temperature для более консистентного вывода")
            print("   - Проверьте доступность GPU памяти")
            return 1
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_zephyr_pipeline():
    """Тест загрузки Zephyr pipeline"""
    print("\n" + "=" * 70)
    print("ТЕСТ: ЗАГРУЗКА ZEPHYR PIPELINE")
    print("=" * 70)
    
    try:
        from llm_interface.llm_SAP import load_Zephyr_pipeline
        
        print("\n📥 Загружаю Zephyr pipeline...")
        pipe = load_Zephyr_pipeline()
        print("✅ Pipeline успешно загружен")
        
        print("\n🧪 Тестовый промт...")
        test_input = "The capital of France is"
        
        output = pipe(
            test_input,
            max_new_tokens=50,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )[0]["generated_text"]
        
        print(f"✅ Вывод получен:")
        print(f"   Input: {test_input}")
        print(f"   Output: {output}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_templates():
    """Тест загрузки шаблонов"""
    print("\n" + "=" * 70)
    print("ТЕСТ: ЗАГРУЗКА ШАБЛОНОВ")
    print("=" * 70)
    
    templates = [
        'llm_interface/template/template_SAP_system_short.txt',
        'llm_interface/template/template_SAP_user.txt',
    ]
    
    all_ok = True
    for template_path in templates:
        if Path(template_path).exists():
            with open(template_path, 'r') as f:
                content = f.read()
            print(f"✅ {template_path}")
            print(f"   Размер: {len(content)} символов")
        else:
            print(f"❌ {template_path} - НЕ НАЙДЕН")
            all_ok = False
    
    return 0 if all_ok else 1


def main():
    """Главная функция"""
    print("\n" + "🔬" * 35)
    print("ДИАГНОСТИКА ZEPHYR SAP ДЕКОМПОЗИЦИИ")
    print("🔬" * 35)
    
    tests = [
        ("Загрузка шаблонов", test_templates),
        ("Загрузка Zephyr Pipeline", test_zephyr_pipeline),
        ("SAP декомпозиция", test_zephyr_sap),
    ]
    
    for test_name, test_func in tests:
        print(f"\n\n{'=' * 70}")
        print(f"▶️  {test_name.upper()}")
        print(f"{'=' * 70}")
        
        try:
            result = test_func()
            if result != 0:
                print(f"\n⚠️  {test_name} завершился с ошибкой")
                print("   Прерываю дальнейшее тестирование")
                return 1
        except KeyboardInterrupt:
            print(f"\n⏸️  Тестирование прервано пользователем")
            return 1
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n\n" + "✅" * 35)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("✅" * 35)
    print("\n💡 Дальше можно использовать:")
    print("   python generate_sap_prompts.py --prompts-file prompts.txt --llm Zephyr")
    print("   или")
    print("   python workflow_example.py --step 1 --llm Zephyr")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
