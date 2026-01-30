#!/usr/bin/env python3
"""
Fallback SAP decomposition for Zephyr
Резервное решение для декомпозиции с Zephyr когда LLM не возвращает правильный формат
"""

def create_simple_sap_decomposition(original_prompt):
    """
    Создает простую SAP декомпозицию промта когда LLM не справляется
    Разбивает промт на логические части и применяет их на разных шагах
    
    Args:
        original_prompt: исходный промт
        
    Returns:
        dict с структурой SAP декомпозиции
    """
    
    # Разделение промта на части (наивный подход)
    parts = original_prompt.split(" and ")
    
    if len(parts) >= 2:
        # Если есть "и", разделяем
        prompts_list = [
            parts[0].strip(),  # Первая часть (начало)
            original_prompt,    # Полный промт (конец)
        ]
        switch_prompts_steps = [25]  # Переключение на половине
    else:
        # Иначе просто разделяем на начало и конец с деталями
        words = original_prompt.split()
        
        if len(words) > 4:
            # Разделяем на две части
            mid = len(words) // 2
            first_part = " ".join(words[:mid])
            second_part = original_prompt  # полный промт с деталями
            
            prompts_list = [
                first_part,
                second_part
            ]
            switch_prompts_steps = [20]  # переключение на 20-м шаге из 50
        else:
            # Просто используем один промт
            prompts_list = [original_prompt]
            switch_prompts_steps = []
    
    return {
        "explanation": f"Simple decomposition created as fallback (LLM failed to parse)",
        "prompts_list": prompts_list,
        "switch_prompts_steps": switch_prompts_steps
    }

# Пример использования
if __name__ == "__main__":
    test_prompt = "A serene landscape with mountains and a crystal clear lake at sunset"
    result = create_simple_sap_decomposition(test_prompt)
    print(result)
