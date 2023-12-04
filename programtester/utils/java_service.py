def clear_java_comments(program_text: str) -> str:
    result = ''
    i = 0

    while i < len(program_text):
        # Пропуск содержимого строк
        if program_text[i] == '\"':
            result += program_text[i]
            i += 1
            while i < len(program_text):
                if program_text[i] == '\"' and program_text[i - 1] != '\\':
                    result += program_text[i]
                    i += 1
                    break
                result += program_text[i]
                i += 1

        # Пропуск содержимого однострочных комментариев
        elif i + 1 < len(program_text) and program_text[i:i+2] == '//':
            i = program_text.find('\n', i + 2)
            if i < 0:
                break

        # Пропуск содержимого многострочных комментариев
        elif i + 1 < len(program_text) and program_text[i:i+2] == '/*':
            i = program_text.find('*/', i + 2)
            if i < 0:
                break
            i += 2

        else:
            result += program_text[i]
            i += 1

    return result


def get_java_package(program_text: str) -> str | None:
    i_begin = program_text.find('package')
    if i_begin < 0:
        return None

    i_begin += len('package')
    i_end = program_text.find(';', i_begin)
    if i_end < 0:
        return None

    return ''.join(program_text[i_begin:i_end].split())


def get_java_class_name(program_text: str) -> str | None:
    i = program_text.find('class')
    if i < 0:
        return None

    i += len('class')
    while i < len(program_text) and program_text[i] <= ' ':
        i += 1

    class_name = ''
    while ('a' <= program_text[i] <= 'z' or 'A' <= program_text[i] <= 'Z' or
           '0' <= program_text[i] <= '9' or program_text[i] == '_'):
        class_name += program_text[i]
        i += 1

    return class_name
