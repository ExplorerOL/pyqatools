import random
import string

from pyqatools.exceptions.general_exceptions import EmptyValueError, UnexpectedTypeError


class StringsGenerator:
    ASCII_LETTERS = string.ascii_letters
    ASCII_UPPERCASE = string.ascii_uppercase
    ASCII_LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SPECIAL_CHARS = '!@#$%^&*()_+-=[]{}|;:,.<>?~\'"\\/'
    CYRILLIC_LOWERCASE = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    CYRILLIC_UPPERCASE = CYRILLIC_LOWERCASE.upper()

    @staticmethod
    def generate_random_string(  # noqa C901
        length: int = 10,
        use_letters: bool = True,
        use_digits: bool = True,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_special_chars: bool = False,
        use_cyrillic: bool = False,
        charset: str | None = None,
    ) -> str:
        """Генерация случайной строки.

        Args:
            length (int): длина строки (по умолчанию 10)
            use_letters (bool): использовать буквы (по умолчанию True)
            use_digits (bool): использовать цифры (по умолчанию True)
            use_uppercase (bool): использовать заглавные буквы (по умолчанию True)
            use_lowercase (bool): использовать строчные буквы (по умолчанию True)
            use_special_chars (bool): использовать специальные символы (по умолчанию False)
            use_cyrillic (bool): использовать кириллические символы (по умолчанию False)
            charset (Optional[str]): пользовательский набор символов. Если указан, переопределяет другие
                параметры символов

        Returns:
            str: случайная строка

        Raises:
            EmptyValueError: при отрицательной длине строки, при пустом наборе символов
            UnexpectedTypeError: при неверном типе набора символов
        """
        if length < 0:
            raise EmptyValueError('Длина строки должна быть положительной!')

        if length == 0:
            return ''

        if charset is not None:
            if not isinstance(charset, str):
                raise UnexpectedTypeError('Набор символов должен быть строкой!')
            if not charset:
                raise EmptyValueError('Набор символов не может быть пустой строкой!')
            return ''.join(random.choices(charset, k=length))

        char_set = []

        if use_letters:
            if use_cyrillic:
                if use_uppercase:
                    char_set.append(StringsGenerator.CYRILLIC_UPPERCASE)
                if use_lowercase:
                    char_set.append(StringsGenerator.CYRILLIC_LOWERCASE)
            else:
                if use_uppercase:
                    char_set.append(StringsGenerator.ASCII_UPPERCASE)
                if use_lowercase:
                    char_set.append(StringsGenerator.ASCII_LOWERCASE)

        if use_digits:
            char_set.append(StringsGenerator.DIGITS)
        if use_special_chars:
            char_set.append(StringsGenerator.SPECIAL_CHARS)

        if not char_set:
            raise EmptyValueError('Не выбран ни один тип символов!')
        full_charset = ''.join(char_set)

        return ''.join(random.choices(full_charset, k=length))
