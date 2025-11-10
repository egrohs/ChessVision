# ChessVision

Visualizador de controle de casas do xadrez com contorno nas peças.

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

Parâmetros visuais
- `OUTLINE_THICKNESS` em `main.py`: controla a espessura do contorno (padrão 2).
- Para aumentar ou suavizar o contorno, aumente `OUTLINE_THICKNESS` ou substitua a técnica por imagens com antialias/blur.

Observações
- `requirements.txt` foi adicionado com `pygame` e `python-chess`.
