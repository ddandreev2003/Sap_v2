# 💾 Pre-generation Workflow Guide

## Обзор

Это руководство описывает рекомендуемый workflow, который использует **предгенерирование SAP декомпозиций**.

### Зачем это нужно?

**SAP (Sequential Attention Prompting)** требует вызова LLM для каждого набора промтов. Если нужно сгенерировать много изображений с теми же промтами, LLM вызывается повторно.

**Решение:** Сгенерируйте SAP декомпозиции один раз, сохраните в JSON, потом используйте многократно.

## Преимущества

| Преимущество | Бенефит |
|---|---|
| ⚡ **Быстрее** | LLM вызывается один раз вместо N раз |
| 💰 **Дешевле** | Дорогой GPT один раз, дешевый FLUX много раз |
| 📝 **Прозрачнее** | Можно проверить/отредактировать SAP перед использованием |
| 💾 **Экономнее** | LLM выгружается, освобождая память для FLUX |
| 🔄 **Гибче** | Разные модели для SAP и FLUX генерирования |

## Три основных компонента

### 1. `generate_sap_prompts.py` - Генерирование SAP

Читает текстовые промты и генерирует SAP декомпозиции.

```bash
python generate_sap_prompts.py \
  --prompts-file prompts.txt \
  --output-file SAP_prompts.json \
  --llm GPT
```

**Вход:** `prompts.txt` (текстовые промты)  
**Выход:** `SAP_prompts.json` (JSON с декомпозициями)

### 2. `sap_prompts_loader.py` - Управление SAP

Загружает и управляет сохраненными SAP декомпозициями.

```python
from sap_prompts_loader import SAPPromptsLoader

loader = SAPPromptsLoader("SAP_prompts.json")
sap_decomposition = loader.get_sap_decomposition("original prompt text")
```

### 3. `combined_flux_sap.py` - Использование SAP

Генерирует изображения с использованием предгенерированных SAP.

```bash
python combined_flux_sap.py \
  --mode sap \
  --use-pregenerated-sap SAP_prompts.json
```

## Полный workflow

### Вариант 1: Пошаговый workflow

```bash
# ШАГ 1: Генерирование SAP (10-30 минут)
python workflow_example.py --step 1 --llm GPT --sap-output SAP_prompts.json

# ШАГ 1.5 (опционально): Проверка результатов
python workflow_example.py --step 1.5 --sap-output SAP_prompts.json
# Отредактируйте SAP_prompts.json если нужно

# ШАГ 2: Генерирование изображений (5-20 минут)
python workflow_example.py --step 2 --mode sap --sap-output SAP_prompts.json

# ШАГ 2 (повторить): Можно запустить еще раз с другими параметрами
python workflow_example.py --step 2 --mode sap --num-steps 50 --num-seeds 4
```

### Вариант 2: Полный workflow одной командой

```bash
python workflow_example.py --full --llm GPT --mode sap --num-steps 30
```

## Формат `SAP_prompts.json`

```json
{
  "metadata": {
    "total_prompts": 10,
    "successful": 10,
    "failed": 0,
    "llm_model": "GPT",
    "timestamp": "2024-01-30T14:30:22"
  },
  "prompts": [
    {
      "id": 0,
      "original_prompt": "A beautiful sunset over mountains",
      "sap_decomposition": {
        "explanation": "Focused attention progression: starting with sky colors, then landscape shapes, and finally adding fine details to create depth and realism",
        "prompts_list": [
          "A beautiful sky with warm sunset colors painting mountains silhouette",
          "Mountains with intricate details and golden sunlight creating shadows and depth"
        ],
        "switch_prompts_steps": [25]
      }
    },
    ...
  ]
}
```

## Примеры использования

### Пример 1: Базовый workflow с GPT

```bash
# 1. Генерируем SAP с GPT
export OPENAI_API_KEY="sk-..."
python workflow_example.py --step 1 --llm GPT

# 2. Генерируем изображения
python workflow_example.py --step 2 --mode sap
```

**Время:** 30-40 минут  
**Стоимость:** 1-2 доллара (за API)  
**Качество:** Высокое

### Пример 2: Локальный workflow с Zephyr

```bash
# 1. Генерируем SAP с локальной моделью
python workflow_example.py --step 1 --llm Zephyr

# 2. Генерируем изображения (несколько раз)
python workflow_example.py --step 2 --mode sap
python workflow_example.py --step 2 --mode sap --num-seeds 4
python workflow_example.py --step 2 --mode sap --num-steps 50
```

**Время:** 40-60 минут  
**Стоимость:** Бесплатно  
**Качество:** Хорошее (хуже, чем GPT)

### Пример 3: Гибридный workflow

```bash
# 1. Генерируем SAP с дорогой GPT (один раз)
export OPENAI_API_KEY="sk-..."
python workflow_example.py --step 1 --llm GPT

# 2. Генерируем изображения много раз (FLUX работает локально, дешево)
python workflow_example.py --step 2 --mode sap
python workflow_example.py --step 2 --mode sap --num-seeds 4
python workflow_example.py --step 2 --mode sap --num-seeds 8 --num-steps 50
```

**Время:** 30-50 минут  
**Стоимость:** 1 доллар (один раз за GPT)  
**Качество:** Высокое  
**Рекомендуется для:** Производства (когда нужны разные версии одного набора изображений)

## Редактирование SAP вручную

Вы можете отредактировать `SAP_prompts.json` перед использованием:

```json
{
  "original_prompt": "A beautiful sunset over mountains",
  "sap_decomposition": {
    "explanation": "Custom decomposition created manually",
    "prompts_list": [
      "Stage 1: Sunset sky with warm colors",
      "Stage 2: Mountains with shadows and depth"
    ],
    "switch_prompts_steps": [25]
  }
}
```

Просто измените `prompts_list` и `switch_prompts_steps` на нужные вам значения.

## Интеграция с другими моделями

### Использование FLUX 1.5 (когда выйдет)

```bash
# SAP генерируется один раз
python workflow_example.py --step 1 --llm GPT

# FLUX можно обновить на новую версию,
# SAP остается прежней
# (просто обновите combined_flux_sap.py)
python workflow_example.py --step 2
```

### Использование разных моделей

```python
# Генерируем SAP с одной моделью
from llm_interface.llm_SAP import LLM_SAP
sap_decompositions = LLM_SAP(prompts, llm="GPT")

# Генерируем изображения с другой моделью
from combined_flux_sap import SAPFluxGenerator
generator = SAPFluxGenerator(llm="Zephyr")  # или другая FLUX версия
```

## Параметры `workflow_example.py`

```bash
python workflow_example.py --help
```

Основные параметры:

| Параметр | Значение | Описание |
|----------|----------|---------|
| `--step` | 1, 1.5, 2, 1-2 | Какой шаг выполнить |
| `--full` | флаг | Выполнить все шаги (1→1.5→2) |
| `--prompts-file` | prompts.txt | Входной файл с промтами |
| `--sap-output` | SAP_prompts.json | Выходной файл с SAP |
| `--llm` | GPT, Zephyr | Какой LLM использовать |
| `--mode` | direct, sap, both | Режим генерирования |
| `--num-seeds` | 1-8 | Количество изображений на промт |
| `--num-steps` | 20-100 | Шагов дифузии |
| `--enable-cpu-offload` | флаг | Экономия памяти |

## Параметры `combined_flux_sap.py` с pre-generated SAP

```bash
python combined_flux_sap.py \
  --mode sap \
  --use-pregenerated-sap SAP_prompts.json \
  --num-inference-steps 50 \
  --seeds 12345 54321 \
  --height 1024 \
  --width 1024
```

## Troubleshooting

### "SAP_prompts.json not found"

```bash
# Проверьте, что файл существует
ls -la SAP_prompts.json

# Если не существует, создайте его
python workflow_example.py --step 1 --llm GPT
```

### "Prompt not found in SAP database"

Значит, в JSON отсутствует этот промт. Варианты:

1. Используйте `--step 1` чтобы добавить его в JSON
2. Добавьте вручную в JSON файл
3. Используйте флаг без `--use-pregenerated-sap` для онлайн генерирования

### "JSON parsing error"

Проверьте синтаксис JSON:

```bash
# Валидация JSON
python -c "import json; json.load(open('SAP_prompts.json'))"

# Если ошибка, исправьте JSON вручную или пересоздайте
python workflow_example.py --step 1 --llm GPT
```

## Практические советы

1. **Начните с малого:** Тестируйте с 2-3 промтами перед полным набором
2. **Сохраняйте JSON:** Создавайте разные версии для разных LLM (`SAP_prompts_gpt.json`, `SAP_prompts_zephyr.json`)
3. **Контролируйте качество:** Всегда проверяйте SAP на шаге 1.5
4. **Переиспользуйте:** Сохраняйте и переиспользуйте JSON для новых FLUX версий
5. **Экспериментируйте:** Отредактируйте SAP вручную и сравните результаты

## Дополнительные ресурсы

- [QUICKSTART.md](QUICKSTART.md) - Быстрый старт
- [README.md](README.md) - Полное описание
- [COMBINED_FLUX_SAP_README.md](COMBINED_FLUX_SAP_README.md) - Техническое описание системы
