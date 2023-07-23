from openpyxl.styles import Border, Side

# Все границы
thin_border = Border(left=Side(style='thin'),
                     right=Side(style='thin'),
                     top=Side(style='thin'),
                     bottom=Side(style='thin'))


def borders_cells(ws, start: str, end="", multi=False, ):
    if not multi:
        ws[start].border = thin_border
    else:
        for cell in ws[f'{start}:{end}']:
            cell[0].border = thin_border

    return ws

