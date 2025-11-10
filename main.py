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
WIDTH = HEIGHT = 800
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
FPS = 60

# Caminho do Stockfish
STOCKFISH_PATH = "/nix/store/l4y0zjkvmnbqwz8grmb34d280n599i75-stockfish-17/bin/stockfish"
if not os.path.exists(STOCKFISH_PATH):
    STOCKFISH_PATH = "stockfish"

# Cores
WHITE = (240, 217, 181)
BLACK = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
SELECTED = (246, 246, 130)

# Cores para controle
GREEN_BASE = (0, 255, 0)
RED_BASE = (255, 0, 0)
NEUTRAL = (128, 128, 128)

# Símbolos Unicode para peças
PIECE_SYMBOLS = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
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
            "Z - Desfazer movimento | R - Reiniciar"
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
        
        # Modo de jogo: "pvp" (player vs player) ou "pve" (player vs engine)
        self.mode = mode
        self.engine_side = engine_side
        self.engine = None
        self.engine_thinking = False
        
        # Inicializa engine se modo PvE
        if self.mode == "pve":
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
                self.engine.configure({"Skill Level": 5})
            except Exception as e:
                print(f"Erro ao inicializar Stockfish: {e}")
                self.mode = "pvp"
        
        # Fonte para peças (DejaVu Sans suporta símbolos Unicode de xadrez)
        self.piece_font = pygame.font.SysFont("dejavusans", 64)
        self.info_font = pygame.font.SysFont("dejavusans", 16)
        self.menu_font = pygame.font.SysFont("dejavusans", 24)
        
    def calculate_square_control(self):
        """
        Calcula o controle de cada casa do tabuleiro.
        Retorna um dicionário com a diferença de controle (positivo = brancas, negativo = pretas)
        """
        control = {}
        
        for square in chess.SQUARES:
            white_attackers = 0
            black_attackers = 0
            
            # Conta quantas peças brancas atacam esta casa
            white_attackers = len(self.board.attackers(chess.WHITE, square))
            
            # Conta quantas peças pretas atacam esta casa
            black_attackers = len(self.board.attackers(chess.BLACK, square))
            
            # Diferença de controle (positivo = brancas controlam mais, negativo = pretas)
            control[square] = white_attackers - black_attackers
            
        return control
    
    def get_square_color(self, control_value, max_control):
        """
        Retorna a cor da casa baseada no controle.
        Verde para controle das brancas, vermelho para controle das pretas.
        """
        if max_control == 0:
            return NEUTRAL
        
        if control_value > 0:
            # Brancas controlam - tons de verde
            intensity = min(255, int(255 * (control_value / max_control)))
            return (0, intensity, 0)
        elif control_value < 0:
            # Pretas controlam - tons de vermelho
            intensity = min(255, int(255 * (abs(control_value) / max_control)))
            return (intensity, 0, 0)
        else:
            # Controle neutro
            return (50, 50, 50)
    
    def draw_board(self):
        """Desenha o tabuleiro com visualização de controle"""
        control = self.calculate_square_control()
        
        # Encontra o valor máximo de controle para normalização
        max_control = max(abs(v) for v in control.values()) if control.values() else 1
        
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                square = chess.square(col, 7 - row)
                
                # Cor de controle
                control_color = self.get_square_color(control[square], max_control)
                
                # Desenha a casa com cor de controle
                rect = pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                pygame.draw.rect(self.screen, control_color, rect)
                
                # Adiciona uma borda para distinguir as casas
                border_color = (100, 100, 100) if (row + col) % 2 == 0 else (80, 80, 80)
                pygame.draw.rect(self.screen, border_color, rect, 1)
                
                # Destaca casa selecionada
                if self.selected_square == square:
                    pygame.draw.rect(self.screen, SELECTED, rect, 4)
                
                # Destaca movimentos válidos
                if square in [move.to_square for move in self.valid_moves]:
                    pygame.draw.circle(self.screen, HIGHLIGHT, 
                                     (col * SQ_SIZE + SQ_SIZE // 2, 
                                      row * SQ_SIZE + SQ_SIZE // 2), 
                                     SQ_SIZE // 6)
    
    def draw_pieces(self):
        """Desenha as peças no tabuleiro"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                
                symbol = PIECE_SYMBOLS.get(piece.symbol(), piece.symbol())
                color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                
                text_surface = self.piece_font.render(symbol, True, color)
                text_rect = text_surface.get_rect()
                text_rect.center = (col * SQ_SIZE + SQ_SIZE // 2, 
                                  row * SQ_SIZE + SQ_SIZE // 2)
                
                self.screen.blit(text_surface, text_rect)
    
    def draw_info(self):
        """Desenha informações do jogo"""
        turn = "Brancas" if self.board.turn == chess.WHITE else "Pretas"
        info_text = f"Turno: {turn} | Movimento: {self.board.fullmove_number}"
        
        # Fundo para o texto
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, WIDTH, 25))
        
        text_surface = self.info_font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 5))
        
        # Status do jogo
        if self.board.is_checkmate():
            winner = "Pretas" if self.board.turn == chess.WHITE else "Brancas"
            status = f"Xeque-mate! {winner} vencem!"
            status_surface = self.info_font.render(status, True, (255, 255, 0))
            self.screen.blit(status_surface, (WIDTH // 2 - 80, 5))
        elif self.board.is_stalemate():
            status_surface = self.info_font.render("Empate por afogamento!", True, (255, 255, 0))
            self.screen.blit(status_surface, (WIDTH // 2 - 80, 5))
        elif self.board.is_check():
            status_surface = self.info_font.render("Xeque!", True, (255, 0, 0))
            self.screen.blit(status_surface, (WIDTH // 2 - 30, 5))
    
    def get_square_under_mouse(self):
        """Retorna a casa do tabuleiro sob o cursor do mouse"""
        mouse_pos = pygame.mouse.get_pos()
        col = mouse_pos[0] // SQ_SIZE
        row = mouse_pos[1] // SQ_SIZE
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, 7 - row)
        return None
    
    def make_engine_move(self):
        """Faz a engine jogar"""
        if self.engine and not self.board.is_game_over():
            self.engine_thinking = True
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            if result.move:
                self.board.push(result.move)
            self.engine_thinking = False
    
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
                self.board.push(move)
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    square = self.get_square_under_mouse()
                    self.handle_click(square)
                
                elif event.type == pygame.KEYDOWN:
                    # Desfazer movimento com 'Z'
                    if event.key == pygame.K_z and len(self.board.move_stack) > 0:
                        # No modo PvE, desfaz 2 movimentos (jogador + engine)
                        if self.mode == "pve" and len(self.board.move_stack) >= 2:
                            self.board.pop()
                            self.board.pop()
                        else:
                            self.board.pop()
                        self.selected_square = None
                        self.valid_moves = []
                    
                    # Reiniciar com 'R'
                    elif event.key == pygame.K_r:
                        self.board.reset()
                        self.selected_square = None
                        self.valid_moves = []
            
            # Engine joga automaticamente quando é a vez dela
            if self.mode == "pve" and self.board.turn == self.engine_side and not self.board.is_game_over():
                if not self.engine_thinking:
                    self.make_engine_move()
            
            # Desenha tudo
            self.draw_board()
            self.draw_pieces()
            self.draw_info()
            
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
