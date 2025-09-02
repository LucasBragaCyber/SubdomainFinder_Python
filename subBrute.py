#!/usr/bin/env python3

import argparse
import dns.resolver
import queue
import threading
import sys
import time

def worker(target_domain, record_type, work_queue, found_subdomains, shutdown_event):
    """
    Função worker que pega subdomínios da fila, resolve o DNS e armazena os resultados.
    Verifica o evento de desligamento para uma saída graciosa.
    """
    resolver = dns.resolver.Resolver()
    
    # --- OTIMIZAÇÃO DE PERFORMANCE ---
    # Define um tempo de espera curto para cada consulta DNS.
    # Se a consulta demorar mais que 2 segundos, ela será cancelada.
    resolver.timeout = 2
    resolver.lifetime = 2
    
    # Usa servidores DNS públicos e rápidos para evitar bloqueios ou lentidão do provedor.
    resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']

    while not work_queue.empty() and not shutdown_event.is_set():
        try:
            if shutdown_event.is_set():
                break

            subdomain = work_queue.get_nowait()
            full_domain = f"{subdomain}.{target_domain}"
            
            answers = resolver.resolve(full_domain, record_type)
            
            ips = ', '.join([str(answer) for answer in answers])
            print(f"\033[94m\033[1m[+] {full_domain} -> {ips}\033[m")
            found_subdomains.append(full_domain)

        except queue.Empty:
            continue
        except dns.resolver.NXDOMAIN:
            pass # Domínio não existe (normal)
        except dns.resolver.NoAnswer:
            pass # Existe, mas não para este tipo de registro
        except dns.resolver.Timeout:
            pass # A consulta expirou (agora bem mais rápido)
        except Exception as e:
            pass # Captura outras exceções raras
        finally:
            work_queue.task_done()

def main():
     # Helper class para traduzir o prefixo "usage:" para "Uso:"
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = '\033[1mUso:\033[m '
            return super().add_usage(usage, actions, groups, prefix)

     # --- Configuração do argparse para uma melhor interface ---
    parser = argparse.ArgumentParser(
        description="Descobridor de subdomínios rápido e multithread.",
        epilog="Exemplo de uso: python3 SubBrute.py -d google.com -w subdominios.txt -t 50",
        formatter_class=CustomHelpFormatter,
        add_help=False
    )
    
    def custom_error_handler(message):
        print(f"\033[91m[!] Erro: Argumentos ausentes ou inválidos.\033[m\n")
        parser.print_help()
        sys.exit(2)

     # --- Substituição do método de erro padrão pelo customizado ---
    parser.error = custom_error_handler
    
    # --- Tradução dos títulos dos grupos de argumentos ---
    parser._positionals.title = 'Argumentos posicionais'
    parser._optionals.title = 'Argumentos opcionais'

    # -- Argumentos obrigatórios --
    required_args = parser.add_argument_group('Argumentos obrigatórios')
    required_args.add_argument("-d", "--dominio", required=True, help="O domínio alvo para a busca.")
    required_args.add_argument("-w", "--wordlist", required=True, help="Caminho para o arquivo da wordlist.")
    
    # -- Argumentos opcionais --
    optional_args = parser.add_argument_group('Argumentos opcionais')
    optional_args.add_argument("-t", "--threads", type=int, default=20, help="Número de threads para usar (padrão: 20).")
    optional_args.add_argument("-r", "--record", type=str, default="A", help="Tipo de registro DNS para consultar (padrão: A).")
    optional_args.add_argument("-h", "--help", action="help", help="Mostra esta mensagem de ajuda e sai.")

    args = parser.parse_args()

    # --- Banner e informações iniciais ---
    print('\033[93m' + "\n------------------------------------------------------------" + '\033[m')
    print('\033[93m\033[22m' + "[+] Descobridor de subdomínios em Python (Multithread) [+]" + '\033[m')
    print('\033[93m' + "------------------------------------------------------------\n" + '\033[m')
    print(f"\033[92mALVO: \033[m{args.dominio}")
    print(f"\033[92mWORDLIST: \033[m{args.wordlist}")
    print(f"\033[92mTHREADS: \033[m{args.threads}\n")
    print('\033[93m\033[1m' + "Subdomínios encontrados: (Domínio -> IP)" + '\033[m')
    print('\033[93m' + "-----------------------------------------\n" + '\033[m')
    
    start_time = time.time()

    # --- Leitura da Wordlist e Preparação da Fila ---
    try:
        with open(args.wordlist, "r", encoding='utf-8') as f:
            subdomains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"\033[91m[!] Erro: Arquivo de wordlist não encontrado em '{args.wordlist}'\033[m", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\033[91m[!] Erro ao ler o arquivo: {e}\033[m", file=sys.stderr)
        sys.exit(1)

    work_queue = queue.Queue()
    for sub in subdomains:
        work_queue.put(sub)
        
    found_subdomains = []
    threads = []
    
    shutdown_event = threading.Event()

    # --- Criação e Inicialização das Threads ---
    for _ in range(args.threads):
        thread = threading.Thread(target=worker, args=(args.dominio, args.record, work_queue, found_subdomains, shutdown_event))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    try:
        # Enquanto houver threads vivas e a interrupção (Ctrl+C) não for chamada
        while any(t.is_alive() for t in threads):
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\033[93m[!] Interrupção detectada. Sinalizando para as threads pararem...\033[m")
        shutdown_event.set()

    # Espera final pelas threads terminarem
    for thread in threads:
        thread.join()

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