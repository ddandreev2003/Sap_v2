#!/usr/bin/env python3
"""
Comparison and analysis tool for Direct FLUX vs SAP results
Инструмент для сравнения и анализа результатов Direct FLUX vs SAP
"""

import os
import json
import argparse
from pathlib import Path
from PIL import Image
from datetime import datetime
from typing import Dict, List, Tuple

class FluxSAPComparator:
    """Класс для сравнения результатов"""
    
    def __init__(self, results_dir: str):
        """Инициализация компаратора"""
        self.results_dir = results_dir
        self.analysis_results = {}
    
    def analyze_directory(self, batch_dir: str) -> Dict:
        """Анализирует директорию с результатами"""
        analysis = {
            "batch_path": batch_dir,
            "direct_flux": self._analyze_mode(os.path.join(batch_dir, "direct_flux")),
            "sap_flux": self._analyze_mode(os.path.join(batch_dir, "sap_flux")),
            "timestamp": datetime.now().isoformat()
        }
        return analysis
    
    def _analyze_mode(self, mode_dir: str) -> Dict:
        """Анализирует одну директорию режима"""
        result = {
            "exists": os.path.exists(mode_dir),
            "prompts_count": 0,
            "total_images": 0,
            "image_stats": {},
            "metadata": {}
        }
        
        if not result["exists"]:
            return result
        
        # Чтение метаданных
        metadata_file = os.path.join(mode_dir, "metadata.txt")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                result["metadata"] = dict(line.strip().split(': ', 1) 
                                         for line in f if ': ' in line)
        
        # Анализ изображений
        for prompt_dir in os.listdir(mode_dir):
            prompt_path = os.path.join(mode_dir, prompt_dir)
            if not os.path.isdir(prompt_path):
                continue
            
            images = [f for f in os.listdir(prompt_path) if f.endswith('.png')]
            result["prompts_count"] += 1
            result["total_images"] += len(images)
            
            # Статистика по изображениям
            image_stats = {
                "count": len(images),
                "sizes": [],
                "total_size_mb": 0
            }
            
            for img_file in images:
                img_path = os.path.join(prompt_path, img_file)
                try:
                    # Размер файла
                    file_size = os.path.getsize(img_path) / (1024 * 1024)  # в MB
                    image_stats["sizes"].append(file_size)
                    image_stats["total_size_mb"] += file_size
                    
                    # Разрешение
                    with Image.open(img_path) as img:
                        image_stats["resolution"] = f"{img.width}x{img.height}"
                except Exception as e:
                    print(f"⚠️  Ошибка при анализе {img_file}: {e}")
            
            result["image_stats"][prompt_dir] = image_stats
        
        return result
    
    def generate_comparison_report(self, batch_dir: str, output_file: str = None) -> str:
        """Генерирует отчет сравнения"""
        analysis = self.analyze_directory(batch_dir)
        
        report = []
        report.append("=" * 70)
        report.append("📊 FLUX + SAP COMPARISON REPORT")
        report.append("=" * 70)
        report.append(f"Batch Directory: {batch_dir}")
        report.append(f"Analysis Timestamp: {analysis['timestamp']}")
        report.append("")
        
        # Сравнение режимов
        direct = analysis["direct_flux"]
        sap = analysis["sap_flux"]
        
        report.append("📈 SUMMARY")
        report.append("-" * 70)
        
        if direct["exists"] and sap["exists"]:
            report.append("✅ Оба режима сгенерировали результаты")
            report.append("")
            
            report.append("Direct FLUX:")
            report.append(f"  • Промтов обработано: {direct['prompts_count']}")
            report.append(f"  • Всего изображений: {direct['total_images']}")
            report.append(f"  • Общий размер: {direct.get('image_stats', {}) and sum(s.get('total_size_mb', 0) for s in direct.get('image_stats', {}).values()):.2f} MB")
            report.append(f"  • Параметры: {direct.get('metadata', {})}")
            report.append("")
            
            report.append("SAP FLUX:")
            report.append(f"  • Промтов обработано: {sap['prompts_count']}")
            report.append(f"  • Всего изображений: {sap['total_images']}")
            report.append(f"  • Общий размер: {sap.get('image_stats', {}) and sum(s.get('total_size_mb', 0) for s in sap.get('image_stats', {}).values()):.2f} MB")
            report.append(f"  • Параметры: {sap.get('metadata', {})}")
            report.append("")
            
            # Сравнение
            report.append("🔄 СРАВНЕНИЕ")
            report.append("-" * 70)
            report.append(f"Одинаковое количество изображений: {'✅ Да' if direct['total_images'] == sap['total_images'] else '❌ Нет'}")
            report.append(f"Одинаковое количество промтов: {'✅ Да' if direct['prompts_count'] == sap['prompts_count'] else '❌ Нет'}")
            
            # Разница в размере
            direct_size = sum(s.get('total_size_mb', 0) for s in direct.get('image_stats', {}).values())
            sap_size = sum(s.get('total_size_mb', 0) for s in sap.get('image_stats', {}).values())
            
            if direct_size > 0:
                size_diff_percent = ((sap_size - direct_size) / direct_size * 100) if direct_size > 0 else 0
                report.append(f"Разница в размере: {size_diff_percent:+.1f}% (SAP vs Direct)")
            
        elif direct["exists"]:
            report.append("⚠️  Только Direct FLUX режим сгенерировал результаты")
        elif sap["exists"]:
            report.append("⚠️  Только SAP FLUX режим сгенерировал результаты")
        else:
            report.append("❌ Не найдены результаты ни для одного режима")
        
        report.append("")
        report.append("=" * 70)
        
        # Возвращение отчета как строки
        report_text = "\n".join(report)
        
        # Сохранение в файл если указано
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Отчет сохранен в: {output_file}")
        
        return report_text
    
    def create_side_by_side_gallery(self, batch_dir: str, output_dir: str = None) -> str:
        """Создает HTML галерею для сравнения"""
        if output_dir is None:
            output_dir = os.path.join(batch_dir, "gallery")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        direct_dir = os.path.join(batch_dir, "direct_flux")
        sap_dir = os.path.join(batch_dir, "sap_flux")
        
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLUX vs SAP Comparison</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
            border-top: 2px solid #eee;
            padding-top: 20px;
        }
        
        .comparison-group h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .prompt-section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #f9f9f9;
        }
        
        .prompt-text {
            font-style: italic;
            color: #555;
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .image-container {
            position: relative;
            width: 100%;
            aspect-ratio: 1;
            border-radius: 6px;
            overflow: hidden;
            background: #f0f0f0;
        }
        
        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .method-label {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .direct { border-left: 4px solid #667eea; }
        .sap { border-left: 4px solid #764ba2; }
        
        .footer {
            text-align: center;
            color: #999;
            margin-top: 30px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .comparison-grid { grid-template-columns: 1fr; }
            h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 FLUX vs SAP Comparison Gallery</h1>
"""
        
        # Сбор изображений
        comparisons = {}
        
        # Прямое сравнение по названиям папок
        if os.path.exists(direct_dir):
            for prompt_folder in os.listdir(direct_dir):
                if prompt_folder.startswith('.'):
                    continue
                
                prompt_path_direct = os.path.join(direct_dir, prompt_folder)
                if not os.path.isdir(prompt_path_direct):
                    continue
                
                if prompt_folder not in comparisons:
                    comparisons[prompt_folder] = {"direct": [], "sap": []}
                
                # Сбор изображений Direct
                for img_file in sorted(os.listdir(prompt_path_direct)):
                    if img_file.endswith('.png'):
                        comparisons[prompt_folder]["direct"].append(
                            os.path.join(prompt_folder, img_file)
                        )
        
        # Сбор SAP изображений
        if os.path.exists(sap_dir):
            for prompt_folder in os.listdir(sap_dir):
                if prompt_folder.startswith('.'):
                    continue
                
                prompt_path_sap = os.path.join(sap_dir, prompt_folder)
                if not os.path.isdir(prompt_path_sap):
                    continue
                
                if prompt_folder not in comparisons:
                    comparisons[prompt_folder] = {"direct": [], "sap": []}
                
                # Сбор изображений SAP
                for img_file in sorted(os.listdir(prompt_path_sap)):
                    if img_file.endswith('.png'):
                        comparisons[prompt_folder]["sap"].append(
                            os.path.join(prompt_folder, img_file)
                        )
        
        # Генерация HTML
        for i, (prompt_name, images) in enumerate(sorted(comparisons.items()), 1):
            html_content += f"""
        <div class="comparison-grid">
            <div class="comparison-group direct">
                <h2>Direct FLUX</h2>
"""
            
            # Direct FLUX images
            for img_path in images.get("direct", []):
                rel_path = os.path.relpath(os.path.join(direct_dir, img_path), output_dir)
                html_content += f"""
                <div class="prompt-section">
                    <div class="prompt-text">Prompt {i}</div>
                    <div class="image-container">
                        <img src="{rel_path}" alt="Direct FLUX">
                        <span class="method-label">Direct FLUX</span>
                    </div>
                </div>
"""
            
            html_content += """
            </div>
            <div class="comparison-group sap">
                <h2>SAP FLUX</h2>
"""
            
            # SAP FLUX images
            for img_path in images.get("sap", []):
                rel_path = os.path.relpath(os.path.join(sap_dir, img_path), output_dir)
                html_content += f"""
                <div class="prompt-section">
                    <div class="prompt-text">Prompt {i} (decomposed)</div>
                    <div class="image-container">
                        <img src="{rel_path}" alt="SAP FLUX">
                        <span class="method-label">SAP FLUX</span>
                    </div>
                </div>
"""
            
            html_content += """
            </div>
        </div>
"""
        
        html_content += """
        <div class="footer">
            <p>Generated by FLUX + SAP Comparison Tool</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Сохранение HTML
        html_file = os.path.join(output_dir, "comparison.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Галерея создана: {html_file}")
        return html_file

def main():
    parser = argparse.ArgumentParser(
        description="Comparison and analysis tool for FLUX vs SAP results"
    )
    
    parser.add_argument(
        '--batch-dir',
        type=str,
        required=True,
        help='Директория с результатами генерации (batch_YYYYMMDD_HHMMSS)'
    )
    
    parser.add_argument(
        '--report',
        type=str,
        default=None,
        help='Сохранить отчет в файл'
    )
    
    parser.add_argument(
        '--gallery',
        type=str,
        default=None,
        help='Создать HTML галерею в указанной директории'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Создать отчет и галерею'
    )
    
    args = parser.parse_args()
    
    # Проверка директории
    if not os.path.exists(args.batch_dir):
        print(f"❌ Директория не найдена: {args.batch_dir}")
        return 1
    
    comparator = FluxSAPComparator(args.batch_dir)
    
    # Генерация отчета
    if args.report or args.all:
        report_file = args.report or os.path.join(args.batch_dir, "comparison_report.txt")
        report = comparator.generate_comparison_report(args.batch_dir, report_file)
        print("\n" + report)
    
    # Создание галереи
    if args.gallery or args.all:
        gallery_dir = args.gallery or os.path.join(args.batch_dir, "gallery")
        comparator.create_side_by_side_gallery(args.batch_dir, gallery_dir)
    
    print("\n✅ Анализ завершен!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
