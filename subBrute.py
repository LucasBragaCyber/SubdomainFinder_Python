#!/usr/bin/env python3

import argparse
import dns.resolver
import queue
import threading
import sys
import time

# Função que será executada por cada thread
def worker(target_domain, record_type, work_queue, found_subdomains):
    """
    Função worker que pega subdomínios da fila, resolve o DNS e armazena os resultados.
    """
    # Cria uma instância do resolver para esta thread
    resolver = dns.resolver.Resolver()
    
    while not work_queue.empty():
        try:
            subdomain = work_queue.get_nowait()
            full_domain = f"{subdomain}.{target_domain}"
            
            # Tenta resolver o nome de domínio
            answers = resolver.resolve(full_domain, record_type)
            
            # Se encontrar, imprime e armazena os IPs
            ips = ', '.join([str(answer) for answer in answers])
            print(f"\033[94m\033[1m[+] {full_domain} -> {ips}\033[m")
            found_subdomains.append(full_domain)

        except dns.resolver.NXDOMAIN:
            # O subdomínio não existe, que é o esperado na maioria das vezes. Ignora.
            pass
        except dns.resolver.NoAnswer:
            # Existe o domínio, mas não para o tipo de registro (ex: 'A') solicitado.
            pass
        except dns.resolver.Timeout:
            # A consulta demorou demais para responder.
            print(f"\033[91m[!] Timeout ao consultar: {full_domain}\033[m", file=sys.stderr)
        except Exception as e:
            # Captura outras exceções de DNS ou da fila.
            # print(f"\033[91m[!] Ocorreu um erro: {e}\033[m", file=sys.stderr)
            pass
        finally:
            work_queue.task_done()

def main():

    # Helper class para traduzir o prefixo "usage:" para "Uso:"
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = '\033[1mUso:\033[m ' # Palavra "Uso:" em negrito
            return super().add_usage(usage, actions, groups, prefix)

    # --- Configuração do argparse para uma melhor interface ---
    parser = argparse.ArgumentParser(
        description="Descobridor de subdomínios com multithread.",
        epilog="Exemplo de uso: python3 DNSbrute.py -d google.com -w subdominios.txt -t 20",
        formatter_class=CustomHelpFormatter, # Usa a classe de formatação personalizada
        add_help=False # Desativa a ajuda padrão automática (-h, --help)
    )
    
    def custom_error_handler(message):
        """Função para lidar com erros de parsing de forma personalizada."""
        print(f"\033[91m[!] Erro: Argumentos ausentes ou inválidos.\033[m\n")
        parser.print_help() # Mostra a ajuda completa
        sys.exit(2) # Encerra o script com um código de erro

    # --- Substituímos o método de erro padrão pelo nosso ---
    parser.error = custom_error_handler
    
    # --- Tradução dos títulos dos grupos de argumentos ---
    # Grupo de argumentos obrigatórios (se houver, como -d e -w)
    parser._positionals.title = 'Argumentos posicionais'
    # Grupo de argumentos opcionais
    parser._optionals.title = 'Argumentos opcionais'

    # --- Criação manual do nosso grupo de argumentos ---
    # Argumentos obrigatórios
    required_args = parser.add_argument_group('Argumentos obrigatórios')
    required_args.add_argument("-d", "--dominio", required=True, help="O domínio alvo para a busca.")
    required_args.add_argument("-w", "--wordlist", required=True, help="Caminho para o arquivo da wordlist.")
    
    # Argumentos opcionais (aqui incluímos nossa ajuda personalizada)
    optional_args = parser.add_argument_group('Argumentos opcionais')
    optional_args.add_argument("-t", "--threads", type=int, default=10, help="Número de threads para usar (padrão: 10).")
    optional_args.add_argument("-r", "--record", type=str, default="A", help="Tipo de registro DNS para consultar (padrão: A).")
    optional_args.add_argument("-h", "--help", action="help", help="Mostra esta mensagem de ajuda e sai.") # Nossa ajuda em Português!

    args = parser.parse_args()

    # --- Banner e informações iniciais ---
    print('\033[93m' + "\n------------------------------------------------------------" + '\033[m')
    print('\033[93m\033[22m' + "[+] Descobridor de subdomínios em Python (Multithread) [+]" + '\033[m')
    print('\033[93m' + "------------------------------------------------------------\n" + '\033[m')
    print('\033[92m' + f"ALVO: {args.dominio}")
    print(f"WORDLIST: {args.wordlist}")
    print(f"THREADS: {args.threads}\n" + '\033[m')
    print('\033[93m\033[1m' + "Subdomínios encontrados: (Domínio -> IP)" + '\033[m')
    print('\033[93m' + "-----------------------------------------\n" + '\033[m')
    
    start_time = time.time()

    # --- Leitura da Wordlist e Preparação da Fila ---
    try:
        with open(args.wordlist, "r") as f:
            subdomains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"\033[91m[!] Erro: Arquivo de wordlist não encontrado em '{args.wordlist}'\033[m", file=sys.stderr)
        sys.exit(1)

    work_queue = queue.Queue()
    for sub in subdomains:
        work_queue.put(sub)
        
    found_subdomains = []
    threads = []

    # --- Criação e Inicialização das Threads ---
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(args.dominio, args.record, work_queue, found_subdomains))
        thread.daemon = True # Permite que o programa principal saia mesmo se as threads estiverem rodando
        thread.start()
        threads.append(thread)

    # Espera a fila esvaziar
    work_queue.join()

    # --- Finalização ---
    end_time = time.time()
    print("\n" + '\033[93m' + "-----------------------------------------" + '\033[m')
    print(f"\033[92mBusca finalizada em {end_time - start_time:.2f} segundos.\033[m")
    print(f"\033[92mTotal de {len(found_subdomains)} subdomínios encontrados.\033[m")


if __name__ == "__main__":
    # Garante que o dnspython está instalado
    try:
        import dns.resolver
    except ImportError:
        print("\033[91m[!] A biblioteca 'dnspython' não está instalada.\033[m", file=sys.stderr)
        print("\033[93mPor favor, instale usando: pip install dnspython\033[m", file=sys.stderr)
        sys.exit(1)
    main()