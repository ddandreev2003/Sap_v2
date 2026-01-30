#!/usr/bin/env python3
"""
Load SAP prompts from pre-generated JSON file
Загружает предгенерированные SAP промты из JSON файла
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class SAPPromptsLoader:
    """Загружает и управляет предгенерированными SAP промтами"""
    
    def __init__(self, json_file: str = 'SAP_prompts.json'):
        """
        Инициализация загружика
        
        Args:
            json_file: путь к JSON файлу с SAP промтами
        """
        self.json_file = json_file
        self.data = None
        self.load()
    
    def load(self) -> bool:
        """Загружает JSON файл с SAP промтами"""
        if not Path(self.json_file).exists():
            print(f"⚠️  Файл не найден: {self.json_file}")
            return False
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            print(f"✅ Загружено {len(self.data.get('prompts', []))} SAP промтов из {self.json_file}")
            return True
        except Exception as e:
            print(f"❌ Ошибка при загрузке JSON: {e}")
            return False
    
    def get_sap_decomposition(self, original_prompt: str) -> Optional[Dict]:
        """
        Получает SAP декомпозицию для оригинального промта
        
        Args:
            original_prompt: оригинальный промт
            
        Returns:
            dict с SAP декомпозицией или None если не найден
        """
        if not self.data:
            return None
        
        for entry in self.data.get('prompts', []):
            if entry.get('original_prompt') == original_prompt:
                return entry.get('sap_decomposition')
        
        return None
    
    def get_sap_decompositions_batch(self, prompts: List[str]) -> List[Optional[Dict]]:
        """
        Получает SAP декомпозиции для списка промтов
        
        Args:
            prompts: список оригинальных промтов
            
        Returns:
            список SAP декомпозиций (None если не найдены)
        """
        results = []
        for prompt in prompts:
            sap = self.get_sap_decomposition(prompt)
            results.append(sap)
        
        # Статистика
        found = sum(1 for x in results if x is not None)
        print(f"✅ Найдено {found}/{len(prompts)} SAP декомпозиций")
        
        return results
    
    def get_all_prompts(self) -> List[Tuple[str, Optional[Dict]]]:
        """
        Возвращает все промты с их SAP декомпозициями
        
        Returns:
            список кортежей (оригинальный_промт, sap_декомпозиция)
        """
        if not self.data:
            return []
        
        return [
            (entry.get('original_prompt'), entry.get('sap_decomposition'))
            for entry in self.data.get('prompts', [])
        ]
    
    def get_stats(self) -> Dict:
        """Возвращает статистику по загруженным промтам"""
        if not self.data:
            return {}
        
        total = len(self.data.get('prompts', []))
        successful = sum(1 for entry in self.data.get('prompts', []) 
                        if entry.get('sap_decomposition') is not None)
        
        return {
            "total_prompts": total,
            "successfully_decomposed": successful,
            "failed": total - successful,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%"
        }

# Пример использования
if __name__ == "__main__":
    loader = SAPPromptsLoader('SAP_prompts.json')
    
    if loader.data:
        print("\n📊 Статистика:")
        stats = loader.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n📋 Примеры:")
        for prompt, sap in loader.get_all_prompts()[:3]:
            print(f"\n  Оригинал: {prompt[:60]}...")
            if sap:
                print(f"  SAP: {len(sap.get('prompts_list', []))} промтов")
