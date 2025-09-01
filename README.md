# SubBrute.py: Descobridor de Subdomínios Multithread

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

Uma ferramenta de linha de comando em Python, rápida e eficiente, para descobrir subdomínios existentes de um domínio alvo. Utiliza um ataque de força bruta com uma wordlist e o poder do multithreading para acelerar drasticamente o processo de busca.

## Principais Funcionalidades

-   🚀 **Alta Performance**: Utiliza um sistema de fila e múltiplos threads para realizar dezenas de consultas DNS simultaneamente.
-   ⚙️ **Flexível**: Suporte para consulta de diferentes tipos de registros DNS (A, AAAA, MX, CNAME, etc.).
-   🎨 **Interface Clara**: Saída nítida e colorida, com uma interface de ajuda e tratamento de erros em português.
-   🔧 **Customizável**: Permite ao usuário definir facilmente o número de threads para otimizar a performance de acordo com sua conexão.
-   🛡️ **Robusto**: Tratamento de erros inteligente que distingue subdomínios não existentes de timeouts ou outras falhas de DNS.

## Instalação

Você precisará do Python 3.7 ou superior instalado.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/LucasBragaCyber/SubdomainFinder_Python.git
    ```

2.  **Navegue até o diretório do projeto:**
    ```bash
    cd SubdomainFinder_Python
    ```

3.  **Instale as dependências:**
    A única dependência externa é a biblioteca `dnspython`.

    *Você pode instalar rodando o comando `pip install -r requirements.txt` no diretório do script.*

    Ou a instalação pode ser feita manualmente rodando no terminal o comando:
    ```bash
    pip install dnspython
    ```

## Modo de Uso

A sintaxe básica para executar o script é:

```bash
python3 SubBrute.py -d <domínio> -w <wordlist> [opções]
```

### Argumentos

Abaixo estão todos os argumentos disponíveis, que podem ser visualizados com `python3 SubBrute.py -h`:

```
Uso: SubBrute.py -d DOMINIO -w WORDLIST [-t THREADS] [-r RECORD] [-h]

Descobridor de subdomínios rápido e multithread.

Argumentos obrigatórios:
  -d DOMINIO, --dominio DOMINIO
                        O domínio alvo para a busca.
  -w WORDLIST, --wordlist WORDLIST
                        Caminho para o arquivo da wordlist.

Argumentos opcionais:
  -h, --help            Mostra esta mensagem de ajuda e sai.
  -t THREADS, --threads THREADS
                        Número de threads para usar (padrão: 10).
  -r RECORD, --record RECORD
                        Tipo de registro DNS para consultar (padrão: A).

Exemplo de uso: python3 SubBrute.py -d google.com -w subdominios.txt -t 20
```

## Exemplos de Uso

**1. Busca Básica**

Realiza uma busca por registros `A` (IPv4) no domínio `example.com.br` usando 10 threads (padrão).

```bash
python3 SubBrute.py --dominio example.com.br --wordlist subdominios.txt
```

**2. Busca Agressiva com Mais Threads**

Aumenta o número de threads para 50 para uma varredura mais rápida (requer uma boa conexão com a internet).

```bash
python3 SubBrute.py -d example.com.br -w subdominios.txt -t 50
```

**3. Buscando por Servidores de E-mail (Registro MX)**

Altera o tipo de registro para `MX` para descobrir os servidores de e-mail do domínio.

```bash
python3 SubBrute.py -d example.com.br -w mail_servers.txt -r MX
```
*(Nota: a wordlist `mail_servers.txt` poderia conter nomes como `mail`, `smtp`, `webmail`, `mx1`, etc.)*

## Como Funciona

O script utiliza um modelo de fila de trabalho para gerenciar as tarefas. A thread principal lê todos os subdomínios da wordlist e os adiciona a uma fila segura (`queue.Queue`). Em seguida, ela inicia um número configurável de "workers" (threads). Cada worker, de forma independente e simultânea, retira um item da fila, realiza a consulta DNS e registra o resultado se for bem-sucedido. Este paralelismo evita que o script fique ocioso esperando a resposta de uma única consulta, resultando em uma performance muito superior a uma abordagem sequencial.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

🛡️ Utilize com responsabilidade e sabedoria :)

- Feito por **[Lucas Braga](https://github.com/LucasBragaCyber)** 🛡️
