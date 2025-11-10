# Visualizador de Controle de Tabuleiro de Xadrez

## Visão Geral
Programa de xadrez interativo em Python que visualiza o controle territorial do tabuleiro. As casas são coloridas em tons de verde quando controladas pelas peças brancas e em tons de vermelho quando controladas pelas peças pretas. A intensidade da cor indica o nível de controle (quantas peças atacam aquela casa).

## Objetivo
Ajudar jogadores a entender o conceito de controle de casas no xadrez - um aspecto fundamental da estratégia posicional. A cada lance, você pode ver visualmente quais áreas do tabuleiro você domina e quais o adversário controla.

## Funcionalidades
- **Menu inicial**: Escolha entre Jogador vs Jogador ou Jogador vs Engine (Stockfish)
- **Jogar contra o computador**: Engine Stockfish configurável com diferentes níveis
- **Escolha de cor**: Jogue com brancas ou pretas contra a engine
- **Visualização de controle**: Casas em verde (você) e vermelho (adversário)
- **Intensidade gradual**: Cor mais intensa = maior controle
- **Jogo interativo**: Clique nas peças para movê-las
- **Indicadores visuais**: Destaque de movimentos válidos
- **Desfazer movimento**: Pressione 'Z' para voltar (desfaz jogador + engine no modo PvE)
- **Reiniciar jogo**: Pressione 'R' para recomeçar
- **Informações do jogo**: Turno atual, número do movimento, status (xeque, xeque-mate)

## Como Usar
1. Execute o programa
2. Clique em uma peça para selecioná-la (só pode mover peças da sua vez)
3. Clique na casa de destino para mover
4. Observe como as cores do tabuleiro mudam a cada movimento
5. Use 'Z' para desfazer e 'R' para reiniciar

## Tecnologias
- **Python 3.11**: Linguagem principal
- **python-chess**: Motor de xadrez e regras do jogo
- **pygame**: Interface gráfica e renderização
- **Stockfish 17**: Engine de xadrez para modo PvE

## Estrutura do Projeto
```
.
├── main.py           # Arquivo principal do programa
├── requirements.txt  # Dependências Python
├── pyproject.toml    # Configuração do projeto
└── replit.md        # Esta documentação
```

## Como Funciona o Cálculo de Controle
Para cada casa do tabuleiro:
1. Conta quantas peças brancas podem atacá-la
2. Conta quantas peças pretas podem atacá-la
3. Calcula a diferença (brancas - pretas)
4. Normaliza e aplica gradiente de cor:
   - Verde: Brancas controlam mais
   - Vermelho: Pretas controlam mais
   - Cinza escuro: Controle neutro/empatado

## Mudanças Recentes
- **2025-11-10**: Versão inicial criada
  - Sistema de cálculo de controle de casas
  - Interface gráfica com pygame
  - Movimentação por clique
  - Visualização com gradiente de cores
  - Menu inicial para escolha de modo
  - Integração com engine Stockfish
  - Modo Player vs Engine (PvE) com escolha de cor
  - Ajuste automático de desfazer no modo PvE
