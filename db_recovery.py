"""
Module: db_recovery
Description: Обеспечивает отказоустойчивость, валидацию структуры и экстренное 
             восстановление целостности таблиц базы данных учета выдачи корма.
Style: Strict PEP 8 Compliance, Type-Hinted.
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

# Настройка системного журналирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("EmergencyRecovery")

# Эталонная схема данных согласно техническому заданию
TARGET_COLUMNS: List[str] = [
    "fio", "birth_date", "passport_series", "passport_number",
    "passport_date", "passport_code", "phone", "district",
    "vk_link", "address", "feed_type", "photo_path", "visit_date"
]

class SystemRecoveryManager:
    """Управляет процессами резервного дублирования и санации поврежденных таблиц."""
    
    def __init__(self, backup_path: str = "backups_archive") -> None:
        self.backup_path = backup_path
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)

    def execute_dump(self, dataframe: pd.DataFrame) -> Optional[str]:
        """Сериализует текущий DataFrame в файл резервной копии."""
        if dataframe is None or dataframe.empty:
            logger.warning("Процедура прервана: передан пустой массив данных.")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_target = os.path.join(self.backup_path, f"db_dump_{timestamp}.csv")
        
        try:
            dataframe.to_csv(file_target, index=False, encoding="utf-8-sig")
            logger.info(f"Резервный дамп успешно сохранен: {file_target}")
            return file_target
        except Exception as err:
            logger.error(f"Критическая ошибка ввода-вывода при создании дампа: {err}")
            return None

    def enforce_schema_integrity(self, df_corrupted: pd.DataFrame) -> pd.DataFrame:
        """Проводит структурный аудит колонок и исправляет аномалии схемы."""
        if df_corrupted is None:
            logger.error("Входной объект равен None. Создается пустой шаблон.")
            return pd.DataFrame(columns=TARGET_COLUMNS)
            
        df_repaired = df_corrupted.copy()
        is_modified = False
        
        for column in TARGET_COLUMNS:
            if column not in df_repaired.columns:
                df_repaired[column] = "Не указана"
                is_modified = True
                logger.warning(f"Регенерация структуры: добавлено отсутствующее поле '{column}'")
                
        if is_modified:
            logger.info("Схема данных приведена к целевому стандарту.")
            
        return df_repaired[TARGET_COLUMNS]

    def reconstruct_from_json(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Аварийно воссоздает таблицы из сырых структур обмена данных."""
        if not raw_data:
            logger.warning("Передан пустой массив записей для реконструкции.")
            return pd.DataFrame(columns=TARGET_COLUMNS)
            
        try:
            constructed_df = pd.DataFrame(raw_data)
            return self.enforce_schema_integrity(constructed_df)
        except Exception as recovery_error:
            logger.critical(f"Сбой критического восстановления данных: {recovery_error}")
            return pd.DataFrame(columns=TARGET_COLUMNS)
