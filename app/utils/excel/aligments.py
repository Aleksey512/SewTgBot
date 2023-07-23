from openpyxl.styles import Alignment

# По центру
al_center = Alignment(horizontal='center', vertical="center")

# Слева
al_left = Alignment(horizontal='left', vertical="center")

# Справа
al_right = Alignment(horizontal='right', vertical="center")

# Перенос текста
al_wrap = Alignment(horizontal='center', vertical="center", wrap_text=True)
