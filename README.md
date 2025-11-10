# ChessVision

Visualizador de controle de casas do xadrez com contorno nas peças e navegação de movimentos.

Como instalar (Windows / PowerShell):

1. Criar e ativar um venv (recomendado):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:
```
python -m pip install -r requirements.txt
```

3. Rodar:
```
python main.py
```

Controles do jogo
- **Clique no tabuleiro**: selecionar e mover peças
- **Z**: desfazer movimento (tecla)
- **R**: reiniciar jogo
- **C**: alternar visualização de controle
- **Botão ◄ Voltar**: voltar um movimento
- **Botão Avançar ►**: avançar um movimento (se houver movimentos desfeitos)

Parâmetros visuais
- `OUTLINE_THICKNESS` em `main.py`: controla a espessura do contorno das peças (padrão 2).
- `BUTTON_COLOR`, `BUTTON_HOVER_COLOR`: cores dos botões

Observações
- `requirements.txt` contém `pygame` e `python-chess`.
- O realce do último movimento mostra origem->destino com overlay e linha conectada.
- Navegação de movimentos (voltar/avançar) funciona tanto via botões quanto via teclado.

