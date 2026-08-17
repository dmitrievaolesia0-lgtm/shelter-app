# Этот файл связывает главный экран с ядром базы данных db_core
import db_core as core

def init_db():
    """Запуск и инициализация базы данных"""
    return core.init_db()

def add_recipient(new_record):
    """Сохранение нового получателя корма в базу данных"""
    return core.add_recipient(new_record)
