# Raio-X Interativo do SO

Demonstração prática da disciplina **Arquitetura e Organização de Computadores** — tema **Componentes de um Sistema Operacional** (Grupo 1 - Tema 10).

## Como executar

1. Instale o Python 3.10+ (marque **"Add Python to PATH"** no instalador do Windows).
2. Instale a única dependência externa:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o programa:
   ```bash
   python raio_x_so.py
   ```

## O que cada botão faz por baixo dos panos


1. Botão 1 — Alocar / Liberar 200 MB na RAM Slide 6 · Memória
• Aloca um bloco de 200 MB (bytearray) e escreve 1 byte a cada 4096 bytes (tamanho de 1 página — ~51.200 páginas).
• Tocar cada página evita a alocação preguiçosa (lazy allocation) e obriga o SO e a MMU a reservarem quadros reais na RAM
física, fazendo o RSS saltar ~200 MB na hora.
• Clicar novamente descarta a referência e devolve as páginas ao gerenciador de memória do SO.

2. Botão 2 — Salvar Arquivo 20 MB Slides 5, 7 e 9 · E/S
• Executa diretamente chamadas de sistema de baixo nível: os.open() (o kernel devolve um File Descriptor, FD), os.write()
(grava 20 MB), os.fsync() (força o driver a gravar no disco), os.read() (lê de volta) e os.close().
• Os contadores do card de E/S sobem imediatamente e o Log registra toda a sequência e o tempo em milissegundos.

3. Botão 3 — Criar Processo Filho Slides 4 e 11 · Kernel
• Chama multiprocessing.Process para criar um novo processo isolado, com PID próprio, executando carga de CPU por 2,5
segundos.
• Enquanto roda, o card de Processos mostra o PID filho ativo, a barra de CPU sobe e as trocas de contexto aumentam
conforme o escalonador alterna entre os processos.
