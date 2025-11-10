#!/usr/bin/env python3
"""
Visualizador de Controle de Tabuleiro de Xadrez
Mostra em verde as casas controladas por você e em vermelho as controladas pelo adversário.
"""

import pygame
import chess
import sys

# Configurações
WIDTH = HEIGHT = 800
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
FPS = 60

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


class ChessGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Controle de Tabuleiro - Xadrez")
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []
        
        # Fonte para peças (DejaVu Sans suporta símbolos Unicode de xadrez)
        self.piece_font = pygame.font.SysFont("dejavusans", 64)
        self.info_font = pygame.font.SysFont("dejavusans", 16)
        
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
    
    def handle_click(self, square):
        """Processa clique em uma casa do tabuleiro"""
        if square is None:
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
                        self.board.pop()
                        self.selected_square = None
                        self.valid_moves = []
                    
                    # Reiniciar com 'R'
                    elif event.key == pygame.K_r:
                        self.board.reset()
                        self.selected_square = None
                        self.valid_moves = []
            
            # Desenha tudo
            self.draw_board()
            self.draw_pieces()
            self.draw_info()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ChessGame()
    game.run()
