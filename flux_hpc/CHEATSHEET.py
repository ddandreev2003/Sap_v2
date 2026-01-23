#!/usr/bin/env python3
"""
Шпаргалка команд для FLUX HPC
Быстрый справочник всех основных команд
"""

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                     FLUX HPC - ШПАРГАЛКА КОМАНД                          ║
╚══════════════════════════════════════════════════════════════════════════╝

📍 ЛОКАЛЬНАЯ МАШИНА (интернет необходим)
═══════════════════════════════════════════════════════════════════════════

🔧 УСТАНОВКА И ПОДГОТОВКА:

  # Перейти в папку
  cd SAP/flux_hpc

  # Создать окружение Python
  conda create -n flux_env python=3.10
  conda activate flux_env

  # Установить зависимости
  pip install -r requirements.txt

  # Проверить готовность
  bash check_readiness.sh
  python3 utils.py --check-env

  # Загрузить модель FLUX (ОДИН РАЗ, ~25GB, 10-20 мин)
  python3 01_download_models.py --output_dir ./models


📝 РАБОТА С ПРОМПТАМИ:

  # Создать шаблон
  python3 utils.py --create-template prompts.json

  # Валидировать промпты
  python3 utils.py --validate-prompts prompts.json

  # Создать свой файл
  vim my_prompts.json
  python3 utils.py --validate-prompts my_prompts.json


🧪 ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ (если есть GPU):

  # Быстрый тест с меньшим размером и шагами
  python3 test_generator.py --model_path ./models/flux_dev

  # Или прямой запуск генератора для теста
  python3 02_generate_images.py \\
      --model_path ./models/flux_dev \\
      --prompts_file my_prompts.json \\
      --output_dir test_results \\
      --height 512 --width 512 \\
      --num_inference_steps 20


📂 ПОДГОТОВКА К ОТПРАВКЕ НА HPC:

  # Создать архив для передачи
  tar -czf flux_hpc_with_models.tar.gz models/ *.py *.sbatch *.json

  # Или просто скопировать
  scp -r models/ username@hpc.cluster:/path/to/project/flux_hpc/
  scp prompts.json username@hpc.cluster:/path/to/project/flux_hpc/


═══════════════════════════════════════════════════════════════════════════

📍 HPC КЛАСТЕР (без интернета)
═══════════════════════════════════════════════════════════════════════════

🔐 ПОДКЛЮЧЕНИЕ И ПОДГОТОВКА:

  # Подключиться к HPC
  ssh username@hpc.cluster

  # Перейти в папку проекта
  cd /path/to/project/SAP/flux_hpc

  # Создать необходимые директории
  bash setup_directories.sh

  # Проверить что модель скопирована
  ls -la models/flux_dev/  # должно быть >10GB
  ls -la prompts.json


⚙️ КОНФИГУРАЦИЯ ПЕРЕД ЗАПУСКОМ:

  # ОТРЕДАКТИРОВАТЬ ПУТИ В script.sbatch!
  vim script.sbatch

  # Заменить:
  # cd /path/to/SAP/flux_hpc  →  cd /full/path/to/your/project/SAP/flux_hpc
  # --model_path /path/to/models  →  /full/path/to/models/flux_dev

  # Проверить пути
  pwd  # узнать полный путь текущей директории
  grep "path" script.sbatch


🚀 ЗАПУСК ЗАДАНИЙ:

  # Простой запуск
  sbatch script.sbatch

  # С переопределением параметров
  sbatch --job-name=flux_test --time=1:00:00 script.sbatch

  # Запуск batch заданий
  bash run_batch.sh

  # Запуск с массивом (5 заданий)
  sbatch --array=1-5 script.sbatch


📊 МОНИТОРИНГ ВЫПОЛНЕНИЯ:

  # Посмотреть все свои задания
  squeue -u $USER

  # Подробная информация о задании
  scontrol show job JOBID

  # Просмотр логов (по мере выполнения)
  tail -f runs/flux-JOBID.log

  # Просмотр 50 последних строк логов
  tail -50 runs/flux-JOBID.log

  # Поиск ошибок в логах
  grep "ERROR\\|error\\|Failed" runs/flux-JOBID.log

  # Постоянный мониторинг очереди
  watch -n 2 'squeue -u $USER'

  # Проверить GPU использование (если подключены к узлу)
  nvidia-smi


❌ УПРАВЛЕНИЕ ЗАДАНИЯМИ:

  # Отмена задания
  scancel JOBID

  # История выполненных заданий
  sacct -u $USER

  # Подробная история
  sacct -u $USER --format=JobID,JobName,State,Elapsed,MaxRSS

  # Остановить все задания
  scancel -u $USER


📂 ПРОВЕРКА РЕЗУЛЬТАТОВ:

  # Посмотреть структуру результатов
  find results/ -type d | head -20

  # Посчитать сгенерированные изображения
  find results/ -name "*.png" | wc -l

  # По папкам
  for dir in results/*/; do
      count=$(find "$dir" -name "*.png" | wc -l)
      echo "$(basename $dir): $count изображений"
  done

  # Размер результатов
  du -sh results/

  # Проверить метаданные
  cat results/prompt_name/metadata.json

  # Посмотреть одно изображение (через cat, если подключены)
  file results/prompt_1/without_hints/img_0000.png


💾 КОПИРОВАНИЕ РЕЗУЛЬТАТОВ:

  # На локальную машину (с локальной машины)
  scp -r username@hpc:/path/to/project/SAP/flux_hpc/results ./

  # Или через rsync (безопаснее для больших файлов)
  rsync -avz --progress username@hpc:/path/to/project/SAP/flux_hpc/results ./

  # Только первый промпт
  scp -r username@hpc:/path/to/project/SAP/flux_hpc/results/prompt_1 ./


═══════════════════════════════════════════════════════════════════════════

🔧 ПАРАМЕТРЫ В script.sbatch
═══════════════════════════════════════════════════════════════════════════

SLURM параметры:

  #SBATCH --job-name=flux           # Имя задания
  #SBATCH --gpus=1                 # Количество GPU
  #SBATCH --cpus-per-task=8        # CPU ядер
  #SBATCH --time=2:00:00           # Максимальное время (чч:мм:сс)
  #SBATCH --output=runs/flux-%j.log    # Файл логов (stdout)
  #SBATCH --error=runs/flux-%j.err     # Файл ошибок (stderr)

Генерация параметры:

  --model_path ./models/flux_dev        # Путь к модели
  --prompts_file ./prompts.json         # JSON с промптами
  --output_dir ./results                # Директория результатов
  --num_without_hints 2                 # Кол-во без подсказок
  --num_with_hints 5                    # Кол-во с подсказками
  --height 1024 --width 1024            # Размер изображения
  --num_inference_steps 50              # Шагов дифузии (50 = качество)
  --guidance_scale 3.5                  # Масштаб гайданса
  --seed_base 42                        # Начальный seed


═══════════════════════════════════════════════════════════════════════════

📚 БЫСТРЫЕ ССЫЛКИ НА ДОКУМЕНТАЦИЮ
═══════════════════════════════════════════════════════════════════════════

cat SAP/flux_hpc/INDEX.md              # Обзор системы
cat SAP/flux_hpc/QUICKSTART.md         # За 5 минут
cat SAP/flux_hpc/SETUP_GUIDE.md        # Полная инструкция
cat SAP/flux_hpc/HPC_GUIDE.md          # Для HPC кластера
cat SAP/flux_hpc/GETTING_STARTED.md    # Начало работы


═══════════════════════════════════════════════════════════════════════════

🆘 РЕШЕНИЕ ПРОБЛЕМ
═══════════════════════════════════════════════════════════════════════════

"ModuleNotFoundError: No module named 'diffusers'"
  → pip install -r requirements.txt

"CUDA out of memory"
  → --num_inference_steps 30 (вместо 50)
  → --height 512 --width 512 (вместо 1024)

"No such file or directory" при запуске на HPC
  → Проверить пути в script.sbatch (должны быть АБСОЛЮТНЫЕ)
  → pwd (узнать полный путь)

Job не запускается на HPC
  → cat runs/flux-JOBID.err (посмотреть ошибку)
  → scontrol show job JOBID (подробная информация)
  → Проверить что модель в директории

Долгая очередь в SLURM
  → Использовать меньше ресурсов (#SBATCH --cpus-per-task=4)
  → Запросить V100 вместо других GPU (#SBATCH --constraint=type_a)


═══════════════════════════════════════════════════════════════════════════

⏱️ ПРИМЕРНОЕ ВРЕМЯ ВЫПОЛНЕНИЯ
═══════════════════════════════════════════════════════════════════════════

GPU V100:
  • 1 изображение: 15-30 сек
  • 1 промпт (7 изображений): 2-3 мин
  • 3 промпта (21 изображение): 5-10 мин

GPU A100:
  • 1 изображение: 5-10 сек
  • 1 промпт (7 изображений): 40-70 сек
  • 3 промпта (21 изображение): 2-3 мин


═══════════════════════════════════════════════════════════════════════════

🎓 ПРИМЕР ПОЛНОГО WORKFLOW
═══════════════════════════════════════════════════════════════════════════

1. ЛОКАЛЬНО:
   cd SAP/flux_hpc
   conda create -n flux_env python=3.10
   conda activate flux_env
   pip install -r requirements.txt
   python3 01_download_models.py --output_dir ./models
   python3 utils.py --validate-prompts prompts.json

2. КОПИРОВАТЬ НА HPC:
   scp -r models/ username@hpc:/path/to/project/SAP/flux_hpc/
   scp prompts.json username@hpc:/path/to/project/SAP/flux_hpc/

3. НА HPC:
   ssh username@hpc
   cd /path/to/project/SAP/flux_hpc
   bash setup_directories.sh
   vim script.sbatch  # отредактировать пути!
   sbatch script.sbatch

4. МОНИТОРИТЬ:
   squeue -u $USER
   tail -f runs/flux-*.log

5. РЕЗУЛЬТАТЫ:
   find results/ -name "*.png" | wc -l
   scp -r username@hpc:/path/to/results ./


═══════════════════════════════════════════════════════════════════════════

✨ ГОТОВО! Начните работу с одной из команд выше.

Вопросы? Читайте SAP/flux_hpc/INDEX.md или QUICKSTART.md

═══════════════════════════════════════════════════════════════════════════
""")
