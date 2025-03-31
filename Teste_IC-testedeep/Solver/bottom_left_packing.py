class Piece:
    def __init__(self, type, length, width, height, quantity):
        """
        Classe que representa uma peça.
        :param type: Tipo da peça
        :param length: Comprimento da peça
        :param width: Largura da peça
        :param height: Altura da peça
        :param quantity: Quantidade de peças desse tipo
        """
        self.type = type
        self.length = length
        self.width = width
        self.height = height
        self.quantity = quantity
        self.x = 0  # Posição x da peça na prateleira
        self.y = 0  # Posição y da peça na prateleira


class Position:
    def __init__(self, x, y):
        """
        Classe que representa uma posição disponível na prateleira.
        :param x: Coordenada x (comprimento)
        :param y: Coordenada y (largura)
        """
        self.x = x
        self.y = y


class Shelf:
    def __init__(self, height, width):
        """
        Classe que representa uma prateleira no forno.
        :param height: Altura da prateleira
        :param width: Largura da prateleira
        """
        self.height = height
        self.width = width
        self.pieces = []  # Lista de peças colocadas na prateleira
        self.available_positions = [Position(0, 0)]  # Inicialmente, só o canto inferior esquerdo está disponível
        # Matriz para representar o espaço ocupado na prateleira (True = ocupado, False = livre)
        self.occupied_space = {}  # Dicionário com chaves (x, y) para pontos ocupados

    def can_place_piece(self, piece, position, max_length):
        """
        Verifica se uma peça pode ser colocada na posição dada sem ultrapassar os limites.
        :param piece: Peça a ser colocada
        :param position: Posição onde colocar a peça
        :param max_length: Comprimento máximo da prateleira
        :return: True se a peça pode ser colocada, False caso contrário
        """
        # Verificar altura da peça
        if piece.height > self.height:
            return False

        # Verificar limites de comprimento
        if position.x + piece.length > max_length:
            return False

        # Verificar limites de largura
        if position.y + piece.width > self.width:
            return False

        # Verificar se a área já está ocupada por outra peça
        for x in range(position.x, position.x + piece.length):
            for y in range(position.y, position.y + piece.width):
                if (x, y) in self.occupied_space:
                    return False

        return True

    def place_piece(self, piece, position, max_length):
        """
        Coloca uma peça na posição especificada e atualiza as posições disponíveis.
        :param piece: Peça a ser colocada
        :param position: Posição onde colocar a peça
        :param max_length: Comprimento máximo da prateleira
        """
        # Atualizar a posição da peça
        piece_copy = Piece(piece.type, piece.length, piece.width, piece.height, 1)
        piece_copy.x = position.x
        piece_copy.y = position.y
        self.pieces.append(piece_copy)

        # Marcar espaço como ocupado
        for x in range(position.x, position.x + piece.length):
            for y in range(position.y, position.y + piece.width):
                self.occupied_space[(x, y)] = True

        # Remover a posição atual da lista de posições disponíveis
        self.available_positions.remove(position)

        # Adicionar novas posições disponíveis
        # 1. Posição à direita da peça
        right_pos = Position(position.x + piece.length, position.y)
        if right_pos.x < max_length and right_pos not in self.available_positions:
            if not any((right_pos.x, y) in self.occupied_space for y in range(right_pos.y, right_pos.y + 1)):
                self.available_positions.append(right_pos)

        # 2. Posição acima da peça
        top_pos = Position(position.x, position.y + piece.width)
        if top_pos.y < self.width and top_pos not in self.available_positions:
            if not any((x, top_pos.y) in self.occupied_space for x in range(top_pos.x, top_pos.x + 1)):
                self.available_positions.append(top_pos)

        # Ordenar posições disponíveis pela lógica "Bottom-Left" (primeiro Y menor, depois X menor)
        self.available_positions.sort(key=lambda p: (p.y, p.x))

    def get_best_position(self, piece, max_length):
        """
        Encontra a melhor posição para uma peça na prateleira.
        :param piece: Peça a ser colocada
        :param max_length: Comprimento máximo da prateleira
        :return: A melhor posição ou None se não for possível colocar a peça
        """
        # Verificar cada posição disponível
        for position in self.available_positions:
            if self.can_place_piece(piece, position, max_length):
                return position
        return None

    def get_utilization(self):
        """
        Calcula a utilização do espaço da prateleira.
        :return: Porcentagem de utilização (área ocupada / área total)
        """
        # Calcular a área total da prateleira
        total_area = self.width * self.get_max_x()

        # Calcular a área ocupada pelas peças
        occupied_area = sum(piece.length * piece.width for piece in self.pieces)

        # Retornar a porcentagem de utilização
        if total_area > 0:
            return (occupied_area / total_area) * 100
        return 0

    def get_max_x(self):
        """
        Retorna o maior valor de x utilizado na prateleira.
        :return: Valor máximo de x
        """
        if not self.pieces:
            return 0
        return max(piece.x + piece.length for piece in self.pieces)


class Furnace:
    def __init__(self, length, width, height, shelves):
        """
        Classe que representa o forno.
        :param length: Comprimento do forno
        :param width: Largura do forno
        :param height: Altura do forno
        :param shelves: Lista de alturas das prateleiras
        """
        self.length = length
        self.width = width
        self.height = height
        self.shelves = [Shelf(h, width) for h in shelves]  # Cria as prateleiras com as alturas e larguras fornecidas
        self.unallocated_pieces = []  # Lista para armazenar peças não alocadas e seus motivos


class UnallocatedPiece:
    def __init__(self, piece, reason):
        """
        Classe para representar uma peça não alocada e o motivo.
        :param piece: O objeto Piece que não pôde ser alocado
        :param reason: Motivo da falha (1: falta de altura, 2: falta de largura, 3: falta de comprimento)
        """
        self.piece = piece
        self.reason = reason
        self.reason_text = {
            1: "Falta de altura",
            2: "Falta de largura",
            3: "Falta de comprimento",
            4: "Sobreposição com outras peças"
        }.get(reason, "Motivo desconhecido")


def bottom_left_packing(furnace, pieces):
    """
    Função que implementa uma versão melhorada do algoritmo de empacotamento "Bottom-Left".
    :param furnace: Objeto Furnace que representa o forno
    :param pieces: Lista de objetos Piece que representam as peças
    :return: Retorna o forno com as peças alocadas e informações sobre peças não alocadas
    """
    # Ordenar as peças por múltiplos critérios:
    # 1. Primeiro por altura (decrescente)
    # 2. Depois por área (largura x comprimento) em ordem decrescente
    pieces.sort(key=lambda x: (x.height, x.width * x.length), reverse=True)

    # Contador para acompanhar quantas peças foram alocadas
    allocated_pieces = 0
    unallocated_pieces = 0
    total_pieces = sum(piece.quantity for piece in pieces)

    for piece in pieces:
        for _ in range(piece.quantity):  # Para cada peça, tente alocar a quantidade especificada
            placed = False
            reason = 0  # 0 significa que não tentamos alocar ainda

            # Ordenar prateleiras por taxa de utilização (primeiro as mais utilizadas)
            # Isso ajuda a concentrar peças em menos prateleiras
            shelf_utilization = [(i, shelf.get_utilization()) for i, shelf in enumerate(furnace.shelves)]
            shelf_utilization.sort(key=lambda x: x[1], reverse=True)

            # Tente colocar a peça em uma prateleira existente
            for shelf_idx, _ in shelf_utilization:
                shelf = furnace.shelves[shelf_idx]

                # Verifica se a prateleira tem altura suficiente para a peça
                if shelf.height >= piece.height:
                    # Encontrar a melhor posição na prateleira
                    best_position = shelf.get_best_position(piece, furnace.length)

                    if best_position:
                        # Adiciona a peça na prateleira na melhor posição
                        shelf.place_piece(piece, best_position, furnace.length)
                        placed = True
                        allocated_pieces += 1
                        break
                    else:
                        reason = 4  # Sobreposição ou falta de espaço
                else:
                    reason = 1  # Falta de altura

            if not placed:
                # Cria uma cópia da peça que não pôde ser alocada (para manter a quantidade correta)
                unallocated_piece = Piece(piece.type, piece.length, piece.width, piece.height, 1)
                # Adiciona à lista de peças não alocadas com o motivo
                furnace.unallocated_pieces.append(UnallocatedPiece(unallocated_piece, reason))
                unallocated_pieces += 1
                print(
                    f"Não foi possível alocar peça tipo {piece.type} de dimensões {piece.length}x{piece.width}x{piece.height}. Motivo: {reason}")

    # Calcular e imprimir estatísticas
    print(f"Alocadas {allocated_pieces} de {total_pieces} peças ({allocated_pieces / total_pieces * 100:.2f}%).")
    print(f"Não alocadas: {unallocated_pieces} peças ({unallocated_pieces / total_pieces * 100:.2f}%).")

    # Imprimir informações de utilização das prateleiras
    for i, shelf in enumerate(furnace.shelves):
        utilization = shelf.get_utilization()
        print(f"Prateleira {i + 1}: {len(shelf.pieces)} peças, utilização: {utilization:.2f}%")

    return furnace  # Retorna o forno com as peças alocadas e informações sobre peças não alocadas