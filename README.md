# Warp Cloudflare - GUI

Uma interface gráfica simples em PyQt5 para gerenciar a conexão com o Cloudflare Warp via `warp-cli` no Linux.

## Recursos

- Inicia e verifica o status do serviço `warp-svc`.
- Mostra o IP atual.
- Conecta e desconecta o Warp com um clique.
- Exibe logs em tempo real.
- Registra automaticamente o Warp, se necessário.

## Requisitos

- Python 3
- warp-cli e warp-svc instalados
- `systemd` e permissões para usar `sudo`

## Instalação

Instale as dependências do Python:

```bash
pip install -r requirements.txt
```

## Como usar

```bash
sudo python3 warp_gui.py
```

> **Dica:** Execute com permissões adequadas para evitar falhas ao controlar o serviço Warp.
