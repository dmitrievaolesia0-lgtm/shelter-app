import re

def validate_phone(phone_string):
    digits = re.sub(r'\D', '', phone_string)
    
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
        
    if len(digits) != 11:
        return False, f"❌ Ошибка в номере: должно быть ровно 11 цифр! Вы ввели {len(digits)}."
        
    if not digits.startswith('7'):
        return False, "❌ Ошибка: Номер должен начинаться с +7 или 8!"
        
    return True, f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
