#!/usr/bin/env python3
"""
Visualizador de Controle de Tabuleiro de Xadrez
Mostra em verde as casas controladas por você e em vermelho as controladas pelo adversário.
"""

import pygame
import chess
import chess.engine
import sys
import os

# Configurações
# Espaço reservado no topo para textos/informações (não sobreporá o tabuleiro)
TOP_MENU_HEIGHT = 40
# Espaço reservado na base para letras das colunas (a-h)
BOTTOM_LABEL_HEIGHT = 40
# Altura total da janela (inclui TOP_MENU_HEIGHT e BOTTOM_LABEL_HEIGHT)
HEIGHT = 800 + TOP_MENU_HEIGHT + BOTTOM_LABEL_HEIGHT
# Largura do menu lateral onde ficam os botões
SIDE_MENU_WIDTH = 200
# Espaço reservado à direita para números das linhas (1-8)
RIGHT_LABEL_WIDTH = 40
# Tamanho em pixels do tabuleiro (lado) - usamos a altura como referência
# O tabuleiro ocupa a área: entre TOP_MENU_HEIGHT e (HEIGHT - BOTTOM_LABEL_HEIGHT)
BOARD_SIZE = HEIGHT - TOP_MENU_HEIGHT - BOTTOM_LABEL_HEIGHT
# Largura total da janela = menu lateral + tabuleiro + números à direita
WIDTH = SIDE_MENU_WIDTH + BOARD_SIZE + RIGHT_LABEL_WIDTH
DIMENSION = 8
# Tamanho de cada casa
SQ_SIZE = BOARD_SIZE // DIMENSION
FPS = 60

# Caminho do Stockfish
STOCKFISH_PATH = "stockfish-windows-x86-64-avx2.exe" # "/nix/store/l4y0zjkvmnbqwz8grmb34d280n599i75-stockfish-17/bin/stockfish"
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = "stockfish"

# Cores
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
SELECTED = (246, 246, 130)
CHECK_COLOR = (255, 100, 100)  # Vermelho para aviso de check

# Cores para controle
GREEN_BASE = (0, 255, 0)
RED_BASE = (255, 0, 0)
NEUTRAL = (128, 128, 128)
NO_CONTROL = (60, 60, 60)  # Nenhum jogador ameaça
BALANCED_CONTROL = (150, 100, 150)  # Ambos ameaçam igualmente
WEAK_SQUARE_WHITE = (200, 150, 50)  # Amarelo/laranja escuro para fraqueza branca
WEAK_SQUARE_BLACK = (200, 100, 50)  # Laranja mais avermelhado para fraqueza preta

# Espessura do contorno das peças (em pixels)
OUTLINE_THICKNESS = 2

# Botões de voltar/avançar (posição e tamanho) - menu lateral à esquerda
BUTTON_HEIGHT = 40
BUTTON_WIDTH = SIDE_MENU_WIDTH - 2 * 10
BUTTON_MARGIN = 10
# Posição X fixa dentro o menu lateral
BUTTON_X = BUTTON_MARGIN
# Y iniciais (empilhados verticalmente) — deslocados pelo TOP_MENU_HEIGHT
BASE_BUTTON_Y = TOP_MENU_HEIGHT + 40
BACK_BUTTON_RECT = pygame.Rect(BUTTON_X, BASE_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
FORWARD_BUTTON_RECT = pygame.Rect(BUTTON_X, BASE_BUTTON_Y + (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
ENGINE_BUTTON_RECT = pygame.Rect(BUTTON_X, BASE_BUTTON_Y + 2 * (BUTTON_HEIGHT + 10), BUTTON_WIDTH, BUTTON_HEIGHT)
BUTTON_COLOR = (100, 100, 150)
BUTTON_HOVER_COLOR = (150, 150, 200)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_DISABLED_COLOR = (80, 80, 100)
BUTTON_DISABLED_HOVER_COLOR = (120, 120, 150)

# Símbolos Unicode para peças
PIECE_SYMBOLS = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

# Valores padrão das peças de xadrez (para cálculo de controle)
PIECE_VALUES = {
    chess.QUEEN: 9,
    chess.ROOK: 5,
    chess.BISHOP: 3.5,
    chess.KNIGHT: 3,
    chess.PAWN: 1,
    chess.KING: float('inf')
}

# Valores de defesa das peças de xadrez (10 - valor de ataque)
PIECE_DEFENSE_VALUES = {
    chess.QUEEN: 1,      # 10 - 9
    chess.ROOK: 5,       # 10 - 5
    chess.BISHOP: 6.5,   # 10 - 3.5
    chess.KNIGHT: 7,     # 10 - 3
    chess.PAWN: 9,       # 10 - 1
    chess.KING: 0.1        # Rei não defende casas da mesma forma
}

def show_menu():
    """Exibe menu inicial e retorna a escolha do jogador"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Xadrez - Menu Inicial")
    clock = pygame.time.Clock()
    
    title_font = pygame.font.SysFont("dejavusans", 48, bold=True)
    menu_font = pygame.font.SysFont("dejavusans", 28)
    info_font = pygame.font.SysFont("dejavusans", 16)
    
    menu_options = [
        ("1", "Jogador vs Jogador", "pvp", None),
        ("2", "Jogar com Brancas (vs Engine)", "pve", chess.BLACK),
        ("3", "Jogar com Pretas (vs Engine)", "pve", chess.WHITE),
        ("ESC", "Sair", "quit", None)
    ]
    
    selected = 0
    running = True
    
    while running:
        screen.fill((40, 40, 40))
        
        # Título
        title = title_font.render("Controle de Tabuleiro", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        
        subtitle = info_font.render("Visualizador de controle de casas do xadrez", True, (180, 180, 180))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 140))
        
        # Opções do menu
        y_offset = 220
        for i, (key, text, mode, side) in enumerate(menu_options):
            color = (255, 255, 100) if i == selected else (200, 200, 200)
            option_text = menu_font.render(f"{key}. {text}", True, color)
            screen.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, y_offset))
            y_offset += 60
        
        # Instruções
        instructions = [
            "Use as setas ↑↓ ou números para selecionar",
            "Pressione ENTER para confirmar",
            "",
            "Durante o jogo:",
            "C - Alternar visualização | Z - Desfazer | R - Reiniciar"
        ]
        
        y_offset = HEIGHT - 150
        for instruction in instructions:
            instr_text = info_font.render(instruction, True, (150, 150, 150))
            screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, y_offset))
            y_offset += 22
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit", None
                
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                
                elif event.key == pygame.K_RETURN:
                    _, _, mode, side = menu_options[selected]
                    return mode, side
                
                elif event.key == pygame.K_1:
                    return "pvp", None
                
                elif event.key == pygame.K_2:
                    return "pve", chess.BLACK
                
                elif event.key == pygame.K_3:
                    return "pve", chess.WHITE
        
        clock.tick(FPS)
    
    return "quit", None


class ChessGame:
    def __init__(self, mode="pvp", engine_side=chess.BLACK):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Controle de Tabuleiro - Xadrez")
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []
        # Último movimento (chess.Move) — usado para realce
        self.last_move = None
        # Histórico: último lance em notação algébrica (não é alterado ao desfazer)
        self.history_last_move_san = None
        # Histórico paralelo de SANs alinhado com board.move_stack
        self.san_history = []
        # Movimentos desfeitos — para implementar refazer
        self.redo_stack = []
        # Flag para bloquear engine após desfazer (permite humano jogar)
        self.allow_engine_move = True
        # Flag para habilitar/desabilitar engine
        self.engine_enabled = True
        
        # Modo de jogo: "pvp" (player vs player) ou "pve" (player vs engine)
        self.mode = mode
        self.engine_side = engine_side
        # Salvar o modo original para restaurar quando reabilitar engine
        self.original_mode = mode
        self.engine = None
        self.engine_thinking = False
        
        # Controle de visualização
        self.show_control = True
        self.show_weak_squares = True  # Mostrar casas fracas permanentes
        self.weak_squares = {chess.WHITE: [], chess.BLACK: []}
        
        # Inicializa engine se modo PvE
        if self.mode == "pve":
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                self.engine.configure({"Skill Level": 3})
            except Exception as e:
                print(f"Erro ao inicializar Stockfish: {e}")
                self.mode = "pvp"
        
        # Fonte para peças (DejaVu Sans suporta símbolos Unicode de xadrez)
        self.piece_font = pygame.font.SysFont("dejavusans", 64)
        self.info_font = pygame.font.SysFont("dejavusans", 16)
        self.menu_font = pygame.font.SysFont("dejavusans", 24)
        # Tenta carregar imagens das peças da pasta 'res' (fallback para desenho via fonte se não encontrar)
        self.piece_images = {}
        try:
            res_dir = os.path.join(os.path.dirname(__file__), 'res')
            for sym in PIECE_SYMBOLS.keys():
                # sym é 'P','N',... ou lowercase for black; filename uses lowercase piece letter + 'lt' (light) or 'dt' (dark)
                piece_letter = sym.lower()
                color_tag = 'lt' if sym.isupper() else 'dt'
                fname = f'Chess_{piece_letter}{color_tag}45.svg.png'
                fpath = os.path.join(res_dir, fname)
                if os.path.exists(fpath):
                    img = pygame.image.load(fpath).convert_alpha()
                    # escala para caber na casa (um pouco menor que SQ_SIZE para margem)
                    target = max(1, SQ_SIZE - 8)
                    img = pygame.transform.smoothscale(img, (target, target))
                    self.piece_images[sym] = img
        except Exception:
            # Se qualquer problema, não impedimos a inicialização — fallback será usado
            self.piece_images = {}
        
    def calculate_square_control(self):
        """
        Calcula o controle de cada casa do tabuleiro baseado no valor das peças.
        Retorna um dicionário com tupla (white_attack, white_defense, black_attack, black_defense)
        """
        control = {}
        
        for square in chess.SQUARES:
            white_attack = 0.0
            black_attack = 0.0
            white_defense = 0.0
            black_defense = 0.0
            
            # Soma o valor de ataque de todas as peças brancas que atacam esta casa
            for attacker_square in self.board.attackers(chess.WHITE, square):
                piece = self.board.piece_at(attacker_square)
                white_attack += PIECE_VALUES.get(piece.piece_type, 0)
                white_defense += PIECE_DEFENSE_VALUES.get(piece.piece_type, 0)
            
            # Soma o valor de ataque de todas as peças pretas que atacam esta casa
            for attacker_square in self.board.attackers(chess.BLACK, square):
                piece = self.board.piece_at(attacker_square)
                black_attack += PIECE_VALUES.get(piece.piece_type, 0)
                black_defense += PIECE_DEFENSE_VALUES.get(piece.piece_type, 0)
            
            # Armazena: (white_attack, white_defense, black_attack, black_defense)
            control[square] = (white_attack, white_defense, black_attack, black_defense)
            
        return control
    
    def calculate_square_mobility(self, square):
        """
        Calcula a mobilidade de uma casa: quantos movimentos uma rainha + cavalo teriam se estivessem ali.
        Conta movimentos em 8 direções de rainha (até peça bloquear) + 8 movimentos de cavalo.
        """
        mobility = 0
        col = chess.square_file(square)
        row = chess.square_rank(square)
        
        # Movimentos de rainha: 8 direções (linhas, colunas, diagonais)
        directions = [
            (0, 1),   # cima
            (0, -1),  # baixo
            (1, 0),   # direita
            (-1, 0),  # esquerda
            (1, 1),   # diagonal superior direita
            (1, -1),  # diagonal inferior direita
            (-1, 1),  # diagonal superior esquerda
            (-1, -1)  # diagonal inferior esquerda
        ]
        
        for dx, dy in directions:
            # Vai em cada direção até encontrar uma peça ou sair do tabuleiro
            x, y = col + dx, row + dy
            while 0 <= x < 8 and 0 <= y < 8:
                # Converte coordenadas de volta para square
                target_square = chess.square(x, y)
                # Se há peça, para de contar nesta direção
                if self.board.piece_at(target_square) is not None:
                    break
                # Senão, conta este movimento
                mobility += 1
                x += dx
                y += dy
        
        # Movimentos de cavalo: 8 possíveis (L-shape)
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        for dx, dy in knight_moves:
            x, y = col + dx, row + dy
            if 0 <= x < 8 and 0 <= y < 8:
                # Verifica se a casa destino está vazia
                target_square = chess.square(x, y)
                if self.board.piece_at(target_square) is None:
                    mobility += 1
        
        return mobility
    
    def get_square_color(self, white_attack, white_defense, black_attack, black_defense):
        """
        Retorna a cor da casa baseada no controle de valor das peças com considerar defesa.
        A intensidade é baseada na DEFESA (não no ataque).
        - Cinza escuro: ninguém controla
        - Verde: apenas brancas controlam (intensidade = defesa das peças brancas)
        - Vermelho: apenas pretas controlam (intensidade = defesa das peças pretas)
        - Roxo: ambos controlam (controle balanceado)
        """
        # Se ninguém controla
        if white_attack == 0 and black_attack == 0:
            return NO_CONTROL
        
        # Se ambos controlam (controle balanceado/dividido)
        if white_attack > 0 and black_attack > 0:
            return BALANCED_CONTROL
        
        # Se apenas brancas controlam - intensidade baseada na defesa branca
        if white_attack > 0:
            # Escala defesa de 0 a 255 (máximo defesa é ~9 para peão), com mínimo de 120 para claridade
            intensity = min(255, max(120, int(white_defense * 28)))
            return (0, intensity, 0)
        
        # Se apenas pretas controlam - intensidade baseada na defesa preta
        else:
            # Escala defesa de 0 a 255 (máximo defesa é ~9 para peão), com mínimo de 120 para claridade
            intensity = min(255, max(120, int(black_defense * 28)))
            return (intensity, 0, 0)
    
    def calculate_weak_squares(self):
        """
        Calcula casas fracas permanentes.
        Uma casa é fraca se nenhum peão aliado nas colunas adjacentes está em linhas atrás dela.
        
        Peões brancos:
        - Começam em rank 1, avançam para cima (rank aumenta)
        - Para defender uma casa em (file, rank), precisa haver peão branco em 
          coluna adjacente (file-1 ou file+1) E em rank < target_rank
        - Uma casa é fraca se não há peão em nenhuma coluna adjacente em rank menor
        
        Peões pretos:
        - Começam em rank 6, avançam para baixo (rank diminui)
        - Para defender uma casa em (file, rank), precisa haver peão preto em
          coluna adjacente (file-1 ou file+1) E em rank > target_rank
        - Uma casa é fraca se não há peão em nenhuma coluna adjacente em rank maior
        """
        weak_squares = {chess.WHITE: [], chess.BLACK: []}
        
        for square in chess.SQUARES:
            target_rank = chess.square_rank(square)
            target_file = chess.square_file(square)
            
            # Verifica se é fraca para brancas
            # Precisa verificar colunas adjacentes (file-1 e file+1)
            white_has_defender_behind = False
            
            # Coluna esquerda (file-1)
            if target_file > 0:
                for pawn_square in self.board.pieces(chess.PAWN, chess.WHITE):
                    pawn_file = chess.square_file(pawn_square)
                    pawn_rank = chess.square_rank(pawn_square)
                    # Peão pode defender se está em coluna adjacente esquerda E em rank menor (atrás)
                    if pawn_file == target_file - 1 and pawn_rank < target_rank:
                        white_has_defender_behind = True
                        break
            
            # Coluna direita (file+1)
            if target_file < 7 and not white_has_defender_behind:
                for pawn_square in self.board.pieces(chess.PAWN, chess.WHITE):
                    pawn_file = chess.square_file(pawn_square)
                    pawn_rank = chess.square_rank(pawn_square)
                    # Peão pode defender se está em coluna adjacente direita E em rank menor (atrás)
                    if pawn_file == target_file + 1 and pawn_rank < target_rank:
                        white_has_defender_behind = True
                        break
            
            if not white_has_defender_behind:
                weak_squares[chess.WHITE].append(square)
            
            # Verifica se é fraca para pretas
            # Precisa verificar colunas adjacentes (file-1 e file+1)
            black_has_defender_behind = False
            
            # Coluna esquerda (file-1)
            if target_file > 0:
                for pawn_square in self.board.pieces(chess.PAWN, chess.BLACK):
                    pawn_file = chess.square_file(pawn_square)
                    pawn_rank = chess.square_rank(pawn_square)
                    # Peão pode defender se está em coluna adjacente esquerda E em rank maior (atrás)
                    if pawn_file == target_file - 1 and pawn_rank > target_rank:
                        black_has_defender_behind = True
                        break
            
            # Coluna direita (file+1)
            if target_file < 7 and not black_has_defender_behind:
                for pawn_square in self.board.pieces(chess.PAWN, chess.BLACK):
                    pawn_file = chess.square_file(pawn_square)
                    pawn_rank = chess.square_rank(pawn_square)
                    # Peão pode defender se está em coluna adjacente direita E em rank maior (atrás)
                    if pawn_file == target_file + 1 and pawn_rank > target_rank:
                        black_has_defender_behind = True
                        break
            
            if not black_has_defender_behind:
                weak_squares[chess.BLACK].append(square)
        
        return weak_squares
    
    def draw_board(self):
        """Desenha o tabuleiro com ou sem visualização de controle e casas fracas"""
        control = {}
        weak_squares = {chess.WHITE: [], chess.BLACK: []}
        
        if self.show_control:
            control = self.calculate_square_control()
        
        if self.show_weak_squares:
            weak_squares = self.calculate_weak_squares()
        
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                square = chess.square(col, 7 - row)
                is_light = (row + col) % 2 == 0
                
                # Escolhe cor da casa (sem prioridade de fraqueza - usa controle ou normal)
                has_balanced_control = False
                if self.show_control:
                    # Cor de controle (verde/vermelho/roxo/cinza)
                    white_attack, white_defense, black_attack, black_defense = control[square]
                    
                    # Verifica se ambos têm controle para depois desenhar X roxo
                    if white_attack > 0 and black_attack > 0:
                        has_balanced_control = True
                        # Fundo: cores baseadas em quem tem MAIS defesa (PIECE_DEFENSE_VALUES)
                        # Intensidade é proporcional à diferença de defesa
                        if white_defense > black_defense:
                            # Brancas têm mais defesa
                            diff = white_defense - black_defense
                            # Escala a diferença para intensidade (0-135 para variar de 120 a 255)
                            intensity_offset = min(135, int(diff * 14))
                            intensity = 120 + intensity_offset
                            square_color = (0, intensity, 0)
                        elif black_defense > white_defense:
                            # Pretas têm mais defesa
                            diff = black_defense - white_defense
                            # Escala a diferença para intensidade (0-135 para variar de 120 a 255)
                            intensity_offset = min(135, int(diff * 14))
                            intensity = 120 + intensity_offset
                            square_color = (intensity, 0, 0)
                        else:
                            # Empate: fundo cinza (NO_CONTROL)
                            square_color = NO_CONTROL
                    else:
                        square_color = self.get_square_color(white_attack, white_defense, black_attack, black_defense)
                else:
                    # Cor tradicional de xadrez
                    square_color = WHITE if is_light else BLACK
                
                # Desenha a casa
                rect = pygame.Rect(SIDE_MENU_WIDTH + col * SQ_SIZE, TOP_MENU_HEIGHT + row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(self.screen, square_color, rect)
                
                # Desenha X roxo se ambos têm controle
                if has_balanced_control and self.show_control:
                    center_x = SIDE_MENU_WIDTH + col * SQ_SIZE + SQ_SIZE // 2
                    center_y = TOP_MENU_HEIGHT + row * SQ_SIZE + SQ_SIZE // 2
                    # Tamanho do X (diagonal da casa)
                    half_diag = int(SQ_SIZE * 0.35)
                    # Desenha as duas linhas do X
                    pygame.draw.line(self.screen, BALANCED_CONTROL, 
                                   (center_x - half_diag, center_y - half_diag),
                                   (center_x + half_diag, center_y + half_diag), 4)
                    pygame.draw.line(self.screen, BALANCED_CONTROL,
                                   (center_x + half_diag, center_y - half_diag),
                                   (center_x - half_diag, center_y + half_diag), 4)
                
                # Adiciona borda para fraqueza permanente
                if self.show_weak_squares:
                    if square in weak_squares[chess.WHITE]:
                        pygame.draw.rect(self.screen, WEAK_SQUARE_WHITE, rect, 3)  # Borda amarela para Brancas
                    elif square in weak_squares[chess.BLACK]:
                        pygame.draw.rect(self.screen, WEAK_SQUARE_BLACK, rect, 3)  # Borda laranja para Pretas
                
                # Adiciona uma borda sutil normal
                if not self.show_control:
                    border_color = (200, 200, 200) if is_light else (100, 100, 100)
                    pygame.draw.rect(self.screen, border_color, rect, 1)
                else:
                    border_color = (100, 100, 100) if is_light else (80, 80, 80)
                    pygame.draw.rect(self.screen, border_color, rect, 1)
                
                # Destaca casa selecionada
                if self.selected_square == square:
                    pygame.draw.rect(self.screen, SELECTED, rect, 4)

                # Destaca movimentos válidos
                if square in [move.to_square for move in self.valid_moves]:
                    pygame.draw.circle(self.screen, HIGHLIGHT, 
                                     (SIDE_MENU_WIDTH + col * SQ_SIZE + SQ_SIZE // 2, 
                                      TOP_MENU_HEIGHT + row * SQ_SIZE + SQ_SIZE // 2), 
                                     SQ_SIZE // 6)
                
                # Exibe mobilidade da casa (canto inferior direito)
                mobility = self.calculate_square_mobility(square)
                mobility_text = self.info_font.render(str(mobility), True, (200, 200, 200))
                mobility_rect = mobility_text.get_rect(bottomright=(SIDE_MENU_WIDTH + col * SQ_SIZE + SQ_SIZE - 3, 
                                                                     TOP_MENU_HEIGHT + row * SQ_SIZE + SQ_SIZE - 3))
                self.screen.blit(mobility_text, mobility_rect)

        # Realça o último movimento (origem -> destino)
        if hasattr(self, 'last_move') and self.last_move is not None:
            try:
                from_sq = self.last_move.from_square
                to_sq = self.last_move.to_square

                from_col = chess.square_file(from_sq)
                from_row = 7 - chess.square_rank(from_sq)
                to_col = chess.square_file(to_sq)
                to_row = 7 - chess.square_rank(to_sq)

                from_center = (SIDE_MENU_WIDTH + from_col * SQ_SIZE + SQ_SIZE // 2, TOP_MENU_HEIGHT + from_row * SQ_SIZE + SQ_SIZE // 2)
                to_center = (SIDE_MENU_WIDTH + to_col * SQ_SIZE + SQ_SIZE // 2, TOP_MENU_HEIGHT + to_row * SQ_SIZE + SQ_SIZE // 2)

                # Overlay translúcido nas casas de origem e destino
                overlay_color = (*SELECTED, 100) if len(SELECTED) == 3 else SELECTED
                overlay_surf = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                overlay_surf.fill(overlay_color)
                self.screen.blit(overlay_surf, (SIDE_MENU_WIDTH + from_col * SQ_SIZE, TOP_MENU_HEIGHT + from_row * SQ_SIZE))
                self.screen.blit(overlay_surf, (SIDE_MENU_WIDTH + to_col * SQ_SIZE, TOP_MENU_HEIGHT + to_row * SQ_SIZE))

                # Linha que conecta origem -> destino
                pygame.draw.line(self.screen, SELECTED, from_center, to_center, 6)
                # Marca o destino com um círculo por cima
                pygame.draw.circle(self.screen, SELECTED, to_center, SQ_SIZE // 8)
            except Exception:
                # Segurança: se qualquer coisa falhar, não quebremos a renderização
                pass
        
        # Destaca o rei em xeque com borda vermelha
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            if king_square is not None:
                king_col = chess.square_file(king_square)
                king_row = 7 - chess.square_rank(king_square)
                king_rect = pygame.Rect(SIDE_MENU_WIDTH + king_col * SQ_SIZE, TOP_MENU_HEIGHT + king_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                # Desenha borda grossa vermelha
                pygame.draw.rect(self.screen, CHECK_COLOR, king_rect, 8)
        
        # Desenha bordas com coordenadas (números e letras)
        self.draw_board_labels()
    
    def draw_board_labels(self):
        """Desenha números das linhas (1-8) à direita e letras das colunas (a-h) abaixo do tabuleiro"""
        label_font = pygame.font.SysFont("dejavusans", 14)
        label_color = (200, 200, 200)
        
        # Coordenadas do tabuleiro
        board_left = SIDE_MENU_WIDTH
        board_top = TOP_MENU_HEIGHT
        board_right = SIDE_MENU_WIDTH + BOARD_SIZE
        board_bottom = TOP_MENU_HEIGHT + BOARD_SIZE
        
        # Desenha números das linhas (1-8) à DIREITA
        for row in range(DIMENSION):
            rank = 8 - row  # Rank 8 está no topo, rank 1 está no fundo
            y = board_top + row * SQ_SIZE + SQ_SIZE // 2
            x = board_right + RIGHT_LABEL_WIDTH // 2
            
            label_text = label_font.render(str(rank), True, label_color)
            label_rect = label_text.get_rect(center=(x, y))
            self.screen.blit(label_text, label_rect)
        
        # Desenha letras das colunas (a-h) ABAIXO
        for col in range(DIMENSION):
            file_letter = chr(ord('a') + col)
            x = board_left + col * SQ_SIZE + SQ_SIZE // 2
            y = board_bottom + BOTTOM_LABEL_HEIGHT // 2
            
            label_text = label_font.render(file_letter, True, label_color)
            label_rect = label_text.get_rect(center=(x, y))
            self.screen.blit(label_text, label_rect)
    
    
    def draw_pieces(self):
        """Desenha as peças no tabuleiro"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if not piece:
                continue
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            sym = piece.symbol()
            # Tenta desenhar imagem da peça se disponível
            img = self.piece_images.get(sym)
            center = (SIDE_MENU_WIDTH + col * SQ_SIZE + SQ_SIZE // 2,
                      TOP_MENU_HEIGHT + row * SQ_SIZE + SQ_SIZE // 2)
            if img:
                img_rect = img.get_rect(center=center)
                self.screen.blit(img, img_rect)
            else:
                # Fallback: desenha via fonte SEM contorno (removido por solicitação)
                symbol = PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())
                color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                text_surface = self.piece_font.render(symbol, True, color)
                text_rect = text_surface.get_rect(center=center)
                self.screen.blit(text_surface, text_rect)
    
    def draw_info(self):
        """Desenha informações do jogo"""
        turn = "Brancas" if self.board.turn == chess.WHITE else "Pretas"
        control_status = "ON" if self.show_control else "OFF"
        weak_status = "ON" if self.show_weak_squares else "OFF"
        info_text = f"Turno: {turn} | Movimento: {self.board.fullmove_number} | Controle: {control_status} (C) | Fraquezas: {weak_status} (W)"
        
        # Fundo para o texto (usa TOP_MENU_HEIGHT)
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, WIDTH, TOP_MENU_HEIGHT))
        
        text_surface = self.info_font.render(info_text, True, (255, 255, 255))
        text_y = (TOP_MENU_HEIGHT - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (10, text_y))
        # Mostra o último lance histórico (notação algébrica) no canto superior direito
        if hasattr(self, 'history_last_move_san') and self.history_last_move_san:
            last_move_surf = self.info_font.render(self.history_last_move_san, True, (200, 200, 200))
            lm_rect = last_move_surf.get_rect()
            self.screen.blit(last_move_surf, (WIDTH - lm_rect.width - 10, text_y))
        
        # Status do jogo
        if self.board.is_checkmate():
            winner = "Pretas" if self.board.turn == chess.WHITE else "Brancas"
            status = f"Xeque-mate! {winner} vencem!"
            status_surface = self.info_font.render(status, True, (255, 255, 0))
            status_rect = status_surface.get_rect()
            self.screen.blit(status_surface, (WIDTH // 2 - status_rect.width // 2, text_y))
        elif self.board.is_stalemate():
            status_surface = self.info_font.render("Empate por afogamento!", True, (255, 255, 0))
            status_rect = status_surface.get_rect()
            self.screen.blit(status_surface, (WIDTH // 2 - status_rect.width // 2, text_y))
        elif self.board.is_check():
            status_surface = self.info_font.render("Xeque!", True, (255, 0, 0))
            status_rect = status_surface.get_rect()
            self.screen.blit(status_surface, (WIDTH // 2 - status_rect.width // 2, text_y))
    
    def get_square_under_mouse(self):
        """Retorna a casa do tabuleiro sob o cursor do mouse"""
        mouse_pos = pygame.mouse.get_pos()
        # Ajusta pela largura do menu lateral
        x = mouse_pos[0] - SIDE_MENU_WIDTH
        y = mouse_pos[1] - TOP_MENU_HEIGHT
        # Se o mouse está sobre o menu lateral ou sobre o topo, não é uma casa do tabuleiro
        if x < 0 or y < 0:
            return None
        col = x // SQ_SIZE
        row = y // SQ_SIZE
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, 7 - row)
        return None
    
    def draw_buttons(self, mouse_pos):
        """Desenha botões de voltar/avançar/engine na parte inferior"""
        # Verifica se mouse está sobre cada botão para hover effect
        back_hover = BACK_BUTTON_RECT.collidepoint(mouse_pos)
        forward_hover = FORWARD_BUTTON_RECT.collidepoint(mouse_pos)
        # Botão de engine aparece se foi originalmente PvE (mesmo que agora seja PvP)
        engine_hover = ENGINE_BUTTON_RECT.collidepoint(mouse_pos) if self.original_mode == "pve" else False
        
        # Desenha botão voltar
        back_color = BUTTON_HOVER_COLOR if back_hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, back_color, BACK_BUTTON_RECT)
        pygame.draw.rect(self.screen, (255, 255, 255), BACK_BUTTON_RECT, 2)
        back_text = self.info_font.render("◄ Voltar", True, BUTTON_TEXT_COLOR)
        back_rect = back_text.get_rect(center=BACK_BUTTON_RECT.center)
        self.screen.blit(back_text, back_rect)
        
        # Desenha botão avançar
        forward_color = BUTTON_HOVER_COLOR if forward_hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, forward_color, FORWARD_BUTTON_RECT)
        pygame.draw.rect(self.screen, (255, 255, 255), FORWARD_BUTTON_RECT, 2)
        forward_text = self.info_font.render("Avançar ►", True, BUTTON_TEXT_COLOR)
        forward_rect = forward_text.get_rect(center=FORWARD_BUTTON_RECT.center)
        self.screen.blit(forward_text, forward_rect)
        
        # Desenha botão de engine (se foi originalmente PvE, mesmo em PvP agora)
        if self.original_mode == "pve":
            # Cor varia se engine está habilitada ou desabilitada
            if self.engine_enabled:
                engine_color = BUTTON_HOVER_COLOR if engine_hover else BUTTON_COLOR
                engine_label = "Engine ✓"
            else:
                engine_color = BUTTON_DISABLED_HOVER_COLOR if engine_hover else BUTTON_DISABLED_COLOR
                engine_label = "Engine ✗"
            
            pygame.draw.rect(self.screen, engine_color, ENGINE_BUTTON_RECT)
            pygame.draw.rect(self.screen, (255, 255, 255), ENGINE_BUTTON_RECT, 2)
            engine_text = self.info_font.render(engine_label, True, BUTTON_TEXT_COLOR)
            engine_rect = engine_text.get_rect(center=ENGINE_BUTTON_RECT.center)
            self.screen.blit(engine_text, engine_rect)
    
    def handle_button_click(self, mouse_pos):
        """Processa clique em botões"""
        if BACK_BUTTON_RECT.collidepoint(mouse_pos):
            # Voltar apenas um movimento
            self.undo_move()
            self.selected_square = None
            self.valid_moves = []
        elif FORWARD_BUTTON_RECT.collidepoint(mouse_pos):
            self.redo_move()
            self.selected_square = None
            self.valid_moves = []
        elif ENGINE_BUTTON_RECT.collidepoint(mouse_pos) and self.original_mode == "pve":
            # Toggle engine on/off
            self.engine_enabled = not self.engine_enabled
            # Se desabilitar engine, muda para PvP
            if not self.engine_enabled:
                self.mode = "pvp"
                self.allow_engine_move = False
            else:
                # Se reabilitar engine, volta ao modo original (PvE)
                self.mode = self.original_mode
                # Se for seu turno, permite jogar imediatamente
                self.allow_engine_move = True
    
    def make_engine_move(self):
        """Faz a engine jogar"""
        if self.engine and not self.board.is_game_over():
            self.engine_thinking = True
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            if result.move:
                # Calcula SAN antes de aplicar o movimento
                try:
                    san = self.board.san(result.move)
                except Exception:
                    san = None
                self.board.push(result.move)
                # Atualiza o último movimento
                self.last_move = result.move
                # Atualiza histórico do último lance em notação algébrica e lista de SANs
                if san:
                    self.history_last_move_san = san
                    self.san_history.append(san)
                # Limpa redo_stack quando novo movimento é feito
                self.redo_stack = []
            self.engine_thinking = False
    
    def undo_move(self):
        """Desfaz um movimento e salva em redo_stack"""
        if len(self.board.move_stack) > 0:
            # Pop SAN from history (if available) and store with the popped move
            san = self.san_history.pop() if len(self.san_history) > 0 else None
            move = self.board.pop()
            self.redo_stack.append((move, san))
            # Atualiza last_move e histórico SAN com base na posição atual
            if len(self.board.move_stack) > 0:
                self.last_move = self.board.move_stack[-1]
                self.history_last_move_san = self.san_history[-1] if len(self.san_history) > 0 else None
            else:
                self.last_move = None
                self.history_last_move_san = None
    
    def redo_move(self):
        """Refaz um movimento da redo_stack"""
        if len(self.redo_stack) > 0:
            item = self.redo_stack.pop()
            # item is (move, san)
            if isinstance(item, tuple) and len(item) == 2:
                move, san = item
            else:
                move = item
                san = None
            self.board.push(move)
            # Atualiza last_move e histórico SAN
            self.last_move = move
            if san:
                self.history_last_move_san = san
                self.san_history.append(san)
    
    def undo_to_human_turn(self):
        """Volta até o turno humano anterior (em modo PvE)"""
        if self.mode != "pve" or len(self.board.move_stack) == 0:
            # Se não for PvE ou não houver movimentos, apenas desfaz um
            self.undo_move()
            return
        
        # Se é o turno da engine agora, significa que humano já jogou
        # Desfaz 2 movimentos (último do humano + último da engine)
        if self.board.turn == self.engine_side and len(self.board.move_stack) >= 2:
            # Desfaz engine + humano (mantendo SANs)
            san1 = self.san_history.pop() if len(self.san_history) > 0 else None
            move1 = self.board.pop()
            self.redo_stack.insert(0, (move1, san1))
            san2 = self.san_history.pop() if len(self.san_history) > 0 else None
            move2 = self.board.pop()
            self.redo_stack.insert(0, (move2, san2))
        elif len(self.board.move_stack) >= 1:
            # É o turno do humano (engine ainda não jogou), desfaz apenas o lance do humano
            san = self.san_history.pop() if len(self.san_history) > 0 else None
            move = self.board.pop()
            self.redo_stack.append((move, san))
        
        # Atualiza last_move
        if len(self.board.move_stack) > 0:
            self.last_move = self.board.move_stack[-1]
            # Atualiza histórico SAN para o último SAN disponível
            self.history_last_move_san = self.san_history[-1] if len(self.san_history) > 0 else None
        else:
            self.last_move = None
            self.history_last_move_san = None
        
        # Bloqueia engine para permitir humano jogar
        self.allow_engine_move = False
    
    def handle_click(self, square):
        """Processa clique em uma casa do tabuleiro"""
        if square is None:
            return
        
        # No modo PvE, só permite jogar se não for a vez da engine
        if self.mode == "pve" and self.board.turn == self.engine_side:
            return
        
        piece = self.board.piece_at(square)
        
        # Se já há uma casa selecionada
        if self.selected_square is not None:
            # Verifica se é promoção de peão ANTES de criar o movimento
            selected_piece = self.board.piece_at(self.selected_square)
            if selected_piece and selected_piece.piece_type == chess.PAWN:
                if chess.square_rank(square) in [0, 7]:
                    # Cria movimento com promoção
                    move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                else:
                    move = chess.Move(self.selected_square, square)
            else:
                move = chess.Move(self.selected_square, square)
            
            # Tenta fazer o movimento
            if move in self.board.legal_moves:
                # Calcula SAN antes de aplicar o movimento (board.san requer o estado anterior)
                try:
                    san = self.board.san(move)
                except Exception:
                    san = None
                self.board.push(move)
                # Armazena o último movimento para realce
                self.last_move = move
                # Atualiza histórico do último lance em notação algébrica e lista de SANs
                if san:
                    self.history_last_move_san = san
                    self.san_history.append(san)
                # Limpa redo_stack quando novo movimento é feito
                self.redo_stack = []
                # Permite engine jogar após humano fazer movimento
                self.allow_engine_move = True
                self.selected_square = None
                self.valid_moves = []
            else:
                # Se clicou em outra peça própria, seleciona ela
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                    self.valid_moves = [m for m in self.board.legal_moves 
                                      if m.from_square == square]
                else:
                    self.selected_square = None
                    self.valid_moves = []
        else:
            # Seleciona a peça se for da vez do jogador atual
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.valid_moves = [m for m in self.board.legal_moves 
                                  if m.from_square == square]
    
    def run(self):
        """Loop principal do jogo"""
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Verifica clique em botões primeiro
                    if (BACK_BUTTON_RECT.collidepoint(mouse_pos) or FORWARD_BUTTON_RECT.collidepoint(mouse_pos) or
                        ENGINE_BUTTON_RECT.collidepoint(mouse_pos)):
                        self.handle_button_click(mouse_pos)
                    else:
                        # Clique no tabuleiro
                        square = self.get_square_under_mouse()
                        self.handle_click(square)
                
                elif event.type == pygame.KEYDOWN:
                    # Desfazer movimento com 'Z'
                    if event.key == pygame.K_z and len(self.board.move_stack) > 0:
                        # Utilize as funções já existentes para manter SANs e redo_stack consistentes
                        if self.mode == "pve" and len(self.board.move_stack) >= 2:
                            # Volta até o turno humano anterior (desfaz 2 lances)
                            self.undo_to_human_turn()
                        else:
                            # Desfaz apenas um lance
                            self.undo_move()
                        self.selected_square = None
                        self.valid_moves = []

                    # Reiniciar com 'R'
                    elif event.key == pygame.K_r:
                        self.board.reset()
                        self.selected_square = None
                        self.valid_moves = []
                        # Limpa realce do último movimento
                        self.last_move = None
                        # Limpa redo_stack e SAN history
                        self.redo_stack = []
                        self.san_history = []
                        self.history_last_move_san = None
                        # Permite engine jogar novamente
                        self.allow_engine_move = True

                    # Alternar visualização de controle com 'C'
                    elif event.key == pygame.K_c:
                        self.show_control = not self.show_control

                    # Alternar visualização de casas fracas com 'W'
                    elif event.key == pygame.K_w:
                        self.show_weak_squares = not self.show_weak_squares
            
            # Engine joga automaticamente quando é a vez dela (respeitando allow_engine_move e engine_enabled)
            if (self.mode == "pve" and self.board.turn == self.engine_side and 
                not self.board.is_game_over() and self.allow_engine_move and self.engine_enabled):
                if not self.engine_thinking:
                    self.make_engine_move()
            
            # Desenha tudo
            self.draw_board()
            self.draw_pieces()
            self.draw_info()
            self.draw_buttons(mouse_pos)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        # Cleanup da engine
        if self.engine:
            self.engine.quit()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    mode, engine_side = show_menu()
    
    if mode != "quit":
        game = ChessGame(mode=mode, engine_side=engine_side if engine_side else chess.BLACK)
        game.run()
