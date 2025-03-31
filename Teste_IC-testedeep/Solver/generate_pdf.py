from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors


def generate_pdf(furnace, filename="output.pdf"):
    """
    Função que gera um PDF com a disposição das peças no forno,
    considerando as posições exatas das peças nas prateleiras.
    :param furnace: Objeto Furnace com as peças alocadas
    :param filename: Nome do arquivo PDF a ser gerado
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Configurações de margens e escala
    margin_left = 2 * cm
    margin_top = 10 * cm

    # Determinar dimensões máximas para calcular a escala adequada
    max_shelf_width = furnace.width
    max_shelf_length = furnace.length

    # Calcular escala considerando as dimensões reais do forno
    scale_factor_width = (width - 4 * cm) / max_shelf_length
    scale_factor_height = 2 * cm  # Altura fixa para cada prateleira
    scale_factor = min(scale_factor_width / cm, 0.5)  # Limitar escala para não ficar muito grande

    # Adicionar título e informações
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin_left, height - 1 * cm, "Disposição das Peças no Forno")

    c.setFont("Helvetica", 12)
    c.drawString(margin_left, height - 2 * cm,
                 f"Dimensões do forno: {furnace.length}x{furnace.width}x{furnace.height}")

    # Lista de cores para diferentes tipos de peças
    piece_colors = [
        (0.9, 0.7, 0.7), (0.7, 0.9, 0.7), (0.7, 0.7, 0.9),
        (0.9, 0.9, 0.7), (0.9, 0.7, 0.9), (0.7, 0.9, 0.9),
        (0.8, 0.8, 0.5), (0.5, 0.8, 0.8), (0.8, 0.5, 0.8),
        (0.6, 0.8, 0.6), (0.8, 0.6, 0.6), (0.6, 0.6, 0.8)
    ]

    # Mapear tipos de peças para cores e coletar informações únicas para a legenda
    piece_type_to_color = {}
    piece_type_info = {}  # Dicionário para armazenar informações únicas de cada tipo de peça

    # Debug info - para verificar o conteúdo
    c.setFont("Helvetica", 8)
    debug_y = height - margin_top - 0.5 * cm
    c.drawString(margin_left, debug_y, f"Total de prateleiras: {len(furnace.shelves)}")
    debug_y -= 0.5 * cm

    # Coletar informações únicas de todas as peças para a legenda
    for shelf in furnace.shelves:
        for piece in shelf.pieces:
            if piece.type not in piece_type_info:
                piece_type_info[piece.type] = {
                    'dimensions': f"{piece.length}x{piece.width}x{piece.height}",
                    'description': f"Peça tipo {piece.type}"
                }
                if piece.type not in piece_type_to_color:
                    piece_type_to_color[piece.type] = piece_colors[len(piece_type_to_color) % len(piece_colors)]

    # Calcular utilização total para relatar no PDF
    total_shelf_area = sum(shelf.width * furnace.length for shelf in furnace.shelves)
    total_used_area = sum(sum(piece.length * piece.width for piece in shelf.pieces) for shelf in furnace.shelves)
    total_utilization = (total_used_area / total_shelf_area * 100) if total_shelf_area > 0 else 0

    c.drawString(margin_left, debug_y, f"Utilização total do espaço: {total_utilization:.2f}%")
    debug_y -= 0.5 * cm

    # Desenhar cada prateleira
    for i, shelf in enumerate(furnace.shelves):
        # Posição e dimensões da prateleira
        shelf_y = height - margin_top - (i + 1) * 3 * cm
        shelf_height = 2 * cm  # Altura fixa da representação da prateleira
        shelf_width = furnace.length * scale_factor * cm

        # Desenhar a prateleira (fundo cinza)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFillColorRGB(0.8, 0.8, 0.8)
        c.rect(margin_left, shelf_y, shelf_width, shelf_height, stroke=1, fill=1)

        # Adicionar texto da prateleira e informações de utilização
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0, 0, 0)

        # Calcular a utilização da prateleira
        shelf_area = shelf.width * furnace.length
        used_area = sum(piece.length * piece.width for piece in shelf.pieces)
        utilization = (used_area / shelf_area * 100) if shelf_area > 0 else 0

        c.drawString(margin_left, shelf_y - 0.7 * cm,
                     f"Prateleira {i + 1} (Altura: {shelf.height}, Largura: {shelf.width}, Utilização: {utilization:.2f}%)")

        # Desenhar uma grade de referência (opcional - comentar se não quiser)
        grid_step = 10
        c.setStrokeColorRGB(0.9, 0.9, 0.9)
        for x in range(0, furnace.length + 1, grid_step):
            c.line(margin_left + x * scale_factor * cm, shelf_y,
                   margin_left + x * scale_factor * cm, shelf_y + shelf_height)
        for y in range(0, shelf.width + 1, grid_step):
            c.line(margin_left, shelf_y + y * scale_factor * cm,
                   margin_left + shelf_width, shelf_y + y * scale_factor * cm)

        # Desenhar as peças na prateleira usando suas coordenadas exatas
        for piece in shelf.pieces:
            # Definir cor para o tipo de peça
            piece_color = piece_type_to_color[piece.type]

            # Posição e dimensões da peça no PDF
            piece_x = margin_left + piece.x * scale_factor * cm
            piece_y = shelf_y + piece.y * scale_factor * cm
            piece_width = piece.length * scale_factor * cm
            piece_height = piece.width * scale_factor * cm  # Largura da peça na vertical

            # Desenhar a peça
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(*piece_color)
            c.rect(piece_x, piece_y, piece_width, piece_height, stroke=1, fill=1)

            # Adicionar texto dentro da peça (se a peça for grande o suficiente)
            if piece_width > 1 * cm and piece_height > 0.5 * cm:
                c.setFont("Helvetica", 7)
                c.setFillColorRGB(0, 0, 0)
                text_y = piece_y + (piece_height / 2) - 0.1 * cm
                c.drawCentredString(piece_x + (piece_width / 2), text_y, f"{piece.type}")

                # Opcionalmente, adicionar coordenadas para debugging
                c.setFont("Helvetica", 6)
                c.drawString(piece_x + 0.1 * cm, piece_y + 0.1 * cm, f"({piece.x},{piece.y})")

    # Adicionar legenda de cores expandida com tipo, descrição e dimensões
    legend_y = height - margin_top - (len(furnace.shelves) + 1) * 3 * cm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(margin_left, legend_y, "Legenda:")

    # Cabeçalho da legenda
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin_left + 0.7 * cm, legend_y - 0.7 * cm, "Tipo")
    c.drawString(margin_left + 3 * cm, legend_y - 0.7 * cm, "Dimensões")

    # Adicionar linhas da legenda para cada tipo de peça
    for i, (piece_type, info) in enumerate(piece_type_info.items()):
        # Posição da legenda
        y_pos = legend_y - (i + 2) * 0.7 * cm

        # Desenhar quadrado colorido
        c.setFillColorRGB(*piece_type_to_color[piece_type])
        c.rect(margin_left, y_pos, 0.5 * cm, 0.5 * cm, stroke=1, fill=1)

        # Desenhar informações expandidas da legenda
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawString(margin_left + 0.7 * cm, y_pos + 0.1 * cm, f"{piece_type}")
        c.drawString(margin_left + 3 * cm, y_pos + 0.1 * cm, info['dimensions'])

    # Adicionar resumo de peças alocadas e não alocadas
    total_pieces = len([p for shelf in furnace.shelves for p in shelf.pieces]) + len(furnace.unallocated_pieces)
    allocated_pieces = len([p for shelf in furnace.shelves for p in shelf.pieces])
    allocation_rate = (allocated_pieces / total_pieces * 100) if total_pieces > 0 else 0

    summary_y = legend_y - (len(piece_type_info) + 3) * 0.7 * cm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(margin_left, summary_y, f"Resumo de Alocação:")
    c.setFont("Helvetica", 9)
    c.drawString(margin_left, summary_y - 0.7 * cm, f"Total de peças: {total_pieces}")
    c.drawString(margin_left, summary_y - 1.4 * cm, f"Peças alocadas: {allocated_pieces} ({allocation_rate:.2f}%)")
    c.drawString(margin_left, summary_y - 2.1 * cm,
                 f"Peças não alocadas: {len(furnace.unallocated_pieces)} ({100 - allocation_rate:.2f}%)")

    # Adicionar tabela de peças não alocadas
    unallocated_y = summary_y - 3 * cm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(margin_left, unallocated_y, f"Peças Não Alocadas: {len(furnace.unallocated_pieces)}")

    # Cabeçalho da tabela
    if furnace.unallocated_pieces:
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, unallocated_y - 0.7 * cm, "Tipo")
        c.drawString(margin_left + 2 * cm, unallocated_y - 0.7 * cm, "Dimensões")
        c.drawString(margin_left + 6 * cm, unallocated_y - 0.7 * cm, "Motivo da Falha")

        # Desenhar linhas para cada peça não alocada
        c.setFont("Helvetica", 8)
        for i, unallocated in enumerate(furnace.unallocated_pieces):
            row_y = unallocated_y - (i + 2) * 0.7 * cm
            piece = unallocated.piece
            c.drawString(margin_left, row_y, f"{piece.type}")
            c.drawString(margin_left + 2 * cm, row_y, f"{piece.length}x{piece.width}x{piece.height}")
            c.drawString(margin_left + 6 * cm, row_y, unallocated.reason_text)

    # Salvar o PDF
    c.save()

    print(f"PDF gerado com sucesso: {filename}")
    return filename