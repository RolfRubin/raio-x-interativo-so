"""
Raio-X Interativo do SO
Demonstração prática — Componentes de um Sistema Operacional
Arquitetura e Organização de Computadores (Grupo 10)

Dependências:
    pip install psutil
    (tkinter já vem incluído na instalação padrão do Python)
"""

from __future__ import annotations

import multiprocessing
import os
import platform
import tempfile
import time
import tkinter as tk
from tkinter import ttk

import psutil


def _worker_cpu(duracao: float = 2.5) -> None:
    """Processo filho que executa carga de CPU por alguns segundos."""
    fim = time.perf_counter() + duracao
    acc = 0
    while time.perf_counter() < fim:
        acc += 1


class RaioXSOApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Raio-X Interativo do SO — Grupo 10")
        self.root.geometry("1280x820")
        self.root.minsize(1024, 700)
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass
        self.root.configure(bg="#0F172A")

        self.proc = psutil.Process(os.getpid())
        self.bloco_memoria: bytearray | None = None
        self.filhos_ativos: list[multiprocessing.Process] = []
        self.temp_file = os.path.join(tempfile.gettempdir(), "raio_x_so_demo.bin")

        # Inicializa leitura de CPU (a primeira chamada sempre retorna 0.0)
        psutil.cpu_percent(interval=None)
        self.proc.cpu_percent(interval=None)

        self._configurar_estilos()
        self._montar_interface()
        self._registrar_log(
            f"Sistema iniciado | SO: {platform.system()} {platform.release()} | "
            f"PID do processo: {os.getpid()} | Núcleos lógicos: {os.cpu_count()}"
        )

        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)
        self._atualizar_metricas()

    def _configurar_estilos(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Blue.Horizontal.TProgressbar",
            troughcolor="#1E293B",
            background="#2563EB",
            bordercolor="#1E293B",
            lightcolor="#3B82F6",
            darkcolor="#1D4ED8",
            thickness=26,
        )
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#1E293B",
            background="#10B981",
            bordercolor="#1E293B",
            lightcolor="#34D399",
            darkcolor="#059669",
            thickness=26,
        )

    def _montar_interface(self) -> None:
        # Cabeçalho
        header = tk.Frame(self.root, bg="#1E293B", padx=24, pady=12)
        header.pack(fill="x")

        tk.Label(
            header,
            text="RAIO-X INTERATIVO DO SISTEMA OPERACIONAL",
            font=("Segoe UI", 28, "bold"),
            fg="#F8FAFC",
            bg="#1E293B",
        ).pack(anchor="w")

        info_so = (
            f"SO / Kernel: {platform.system()} {platform.release()} ({platform.machine()})   •   "
            f"PID Atual: {os.getpid()}   •   CPUs: {os.cpu_count()}"
        )
        tk.Label(
            header,
            text=info_so,
            font=("Segoe UI", 17, "bold"),
            fg="#93C5FD",
            bg="#1E293B",
        ).pack(anchor="w", pady=(2, 0))

        # Container principal
        body = tk.Frame(self.root, bg="#0F172A", padx=24, pady=14)
        body.pack(fill="both", expand=True)

        # Grade de cards (2x2)
        cards_frame = tk.Frame(body, bg="#0F172A")
        cards_frame.pack(fill="x")
        cards_frame.columnconfigure(0, weight=1, uniform="col")
        cards_frame.columnconfigure(1, weight=1, uniform="col")

        # Card 1: CPU e Modos (Usuário vs Kernel)
        c1 = self._criar_card(cards_frame, "CPU  •  Modo Usuário vs. Modo Kernel", 0, 0)
        self.lbl_cpu = tk.Label(c1, text="0.0%", font=("Segoe UI", 42, "bold"), fg="#60A5FA", bg="#1E293B")
        self.lbl_cpu.pack(anchor="w")
        self.bar_cpu = ttk.Progressbar(c1, maximum=100, style="Blue.Horizontal.TProgressbar")
        self.bar_cpu.pack(fill="x", pady=(6, 8))
        self.lbl_modos = tk.Label(
            c1,
            text="Tempo Usuário: 0.00 s   |   Tempo Kernel: 0.00 s",
            font=("Segoe UI", 17),
            fg="#CBD5E1",
            bg="#1E293B",
        )
        self.lbl_modos.pack(anchor="w")

        # Card 2: Gerenciamento de Memória (RAM)
        c2 = self._criar_card(cards_frame, "Memória (RAM)  •  Processo (RSS) e Sistema", 0, 1)
        self.lbl_ram_proc = tk.Label(c2, text="0.0 MB", font=("Segoe UI", 42, "bold"), fg="#34D399", bg="#1E293B")
        self.lbl_ram_proc.pack(anchor="w")
        self.bar_ram = ttk.Progressbar(c2, maximum=100, style="Green.Horizontal.TProgressbar")
        self.bar_ram.pack(fill="x", pady=(6, 8))
        self.lbl_ram_sys = tk.Label(
            c2,
            text="RAM do Sistema: 0.0 / 0.0 GB (0%)",
            font=("Segoe UI", 17),
            fg="#CBD5E1",
            bg="#1E293B",
        )
        self.lbl_ram_sys.pack(anchor="w")

        # Card 3: Dispositivos de E/S e System Calls
        c3 = self._criar_card(cards_frame, "Entrada e Saída (E/S)  •  Disco do Processo", 1, 0)
        self.lbl_io_write = tk.Label(
            c3, text="Escrito: 0.0 MB", font=("Segoe UI", 30, "bold"), fg="#FBBF24", bg="#1E293B"
        )
        self.lbl_io_write.pack(anchor="w")
        self.lbl_io_read = tk.Label(
            c3, text="Lido: 0.0 MB   |   Operações E/S: 0", font=("Segoe UI", 17), fg="#CBD5E1", bg="#1E293B"
        )
        self.lbl_io_read.pack(anchor="w", pady=(6, 0))

        # Card 4: Processos e Trocas de Contexto
        c4 = self._criar_card(cards_frame, "Processos  •  Escalonamento e Contexto", 1, 1)
        self.lbl_ctx = tk.Label(
            c4, text="Trocas de contexto: 0", font=("Segoe UI", 30, "bold"), fg="#C084FC", bg="#1E293B"
        )
        self.lbl_ctx.pack(anchor="w")
        self.lbl_filhos = tk.Label(
            c4, text="Processos filhos ativos: nenhum", font=("Segoe UI", 17), fg="#CBD5E1", bg="#1E293B"
        )
        self.lbl_filhos.pack(anchor="w", pady=(6, 0))

        # Botões de demonstração
        btns_frame = tk.Frame(body, bg="#0F172A", pady=14)
        btns_frame.pack(fill="x")
        btns_frame.columnconfigure(0, weight=1, uniform="btn")
        btns_frame.columnconfigure(1, weight=1, uniform="btn")
        btns_frame.columnconfigure(2, weight=1, uniform="btn")

        self.btn_mem = tk.Button(
            btns_frame,
            text="1. Alocar 200 MB na RAM\n(Gerenciamento de Memória)",
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg="#059669",
            activebackground="#047857",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=14,
            cursor="hand2",
            command=self._acao_memoria,
        )
        self.btn_mem.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_io = tk.Button(
            btns_frame,
            text="2. Salvar Arquivo 20 MB\n(System Calls + Driver E/S)",
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg="#D97706",
            activebackground="#B45309",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=14,
            cursor="hand2",
            command=self._acao_io,
        )
        self.btn_io.grid(row=0, column=1, sticky="ew", padx=4)

        self.btn_proc = tk.Button(
            btns_frame,
            text="3. Criar Processo Filho\n(Multitarefa + Troca de Contexto)",
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg="#2563EB",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=14,
            cursor="hand2",
            command=self._acao_processo_filho,
        )
        self.btn_proc.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        # Log de eventos
        tk.Label(
            body,
            text="Log de Eventos e Chamadas ao SO",
            font=("Segoe UI", 18, "bold"),
            fg="#94A3B8",
            bg="#0F172A",
        ).pack(anchor="w", pady=(2, 4))

        self.txt_log = tk.Text(
            body,
            height=5,
            font=("Consolas", 21),
            bg="#020617",
            fg="#E2E8F0",
            insertbackground="#E2E8F0",
            relief="flat",
            wrap="word",
            padx=14,
            pady=10,
            state="disabled",
        )
        self.txt_log.pack(fill="both", expand=True)

    def _criar_card(self, parent: tk.Frame, titulo: str, row: int, col: int) -> tk.Frame:
        card = tk.Frame(parent, bg="#1E293B", padx=18, pady=10)
        padx = (0, 8) if col == 0 else (8, 0)
        pady = (0, 10) if row == 0 else (0, 0)
        card.grid(row=row, column=col, sticky="nsew", padx=padx, pady=pady)

        tk.Label(
            card,
            text=titulo,
            font=("Segoe UI", 17, "bold"),
            fg="#94A3B8",
            bg="#1E293B",
        ).pack(anchor="w", pady=(0, 4))
        return card

    def _registrar_log(self, mensagem: str) -> None:
        hora = time.strftime("%H:%M:%S")
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{hora}] {mensagem}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def _acao_memoria(self) -> None:
        if self.bloco_memoria is None:
            tamanho_mb = 200
            tamanho_bytes = tamanho_mb * 1024 * 1024
            buf = bytearray(tamanho_bytes)
            # Toca 1 byte por página (4 KB) para o SO realmente alocar quadros físicos na RAM
            passo = 4096
            buf[::passo] = b"\x01" * (tamanho_bytes // passo)
            self.bloco_memoria = buf

            self.btn_mem.configure(
                text="1. Liberar 200 MB da RAM\n(Devolver páginas ao SO)",
                bg="#DC2626",
                activebackground="#B91C1C",
            )
            self._registrar_log(
                f"[MEMÓRIA] Alocados {tamanho_mb} MB (~{tamanho_bytes // 4096:,} páginas de 4 KB). "
                "Observe o RSS subir no painel!"
            )
        else:
            self.bloco_memoria = None
            self.btn_mem.configure(
                text="1. Alocar 200 MB na RAM\n(Gerenciamento de Memória)",
                bg="#059669",
                activebackground="#047857",
            )
            self._registrar_log("[MEMÓRIA] Bloco de 200 MB liberado e devolvido ao gerenciador de memória.")

    def _acao_io(self) -> None:
        tamanho_mb = 20
        dados = b"A" * (tamanho_mb * 1024 * 1024)
        flags_escrita = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_BINARY", 0)
        flags_leitura = os.O_RDONLY | getattr(os, "O_BINARY", 0)

        inicio = time.perf_counter()
        # Escrita via chamadas de baixo nível (System Calls: open -> write -> fsync -> close)
        fd = os.open(self.temp_file, flags_escrita, 0o600)
        escritos = os.write(fd, dados)
        os.fsync(fd)
        os.close(fd)

        # Leitura de volta do disco (open -> read -> close)
        fd_r = os.open(self.temp_file, flags_leitura)
        lidos = len(os.read(fd_r, escritos))
        os.close(fd_r)
        duracao_ms = (time.perf_counter() - inicio) * 1000

        self._registrar_log(
            f"[SYSTEM CALLS / E/S] os.open() -> FD={fd} | os.write({escritos // (1024 * 1024)} MB) "
            f"-> os.fsync() -> os.read({lidos // (1024 * 1024)} MB) -> os.close() em {duracao_ms:.1f} ms"
        )

    def _acao_processo_filho(self) -> None:
        p = multiprocessing.Process(target=_worker_cpu, args=(2.5,))
        p.start()
        self.filhos_ativos.append(p)
        self._registrar_log(
            f"[PROCESSO / KERNEL] Processo filho criado (PID={p.pid}, Pai={os.getpid()}). "
            "Executando carga de CPU por 2,5 s..."
        )

    def _atualizar_metricas(self) -> None:
        # Limpa filhos finalizados
        vivos: list[multiprocessing.Process] = []
        for p in self.filhos_ativos:
            if p.is_alive():
                vivos.append(p)
            else:
                p.join(timeout=0)
                self._registrar_log(f"[PROCESSO] Processo filho PID={p.pid} finalizado.")
        self.filhos_ativos = vivos

        # CPU + Modos Usuário / Kernel
        cpu_sys = psutil.cpu_percent(interval=None)
        tempos = self.proc.cpu_times()
        self.lbl_cpu.configure(text=f"{cpu_sys:.1f}%")
        self.bar_cpu["value"] = cpu_sys
        self.lbl_modos.configure(
            text=f"Tempo Usuário: {tempos.user:.2f} s   |   Tempo Kernel: {tempos.system:.2f} s"
        )

        # Memória RAM
        rss_mb = self.proc.memory_info().rss / (1024 * 1024)
        vm = psutil.virtual_memory()
        self.lbl_ram_proc.configure(text=f"{rss_mb:.1f} MB")
        self.bar_ram["value"] = vm.percent
        self.lbl_ram_sys.configure(
            text=(
                f"RAM do Sistema: {vm.used / (1024**3):.1f} / "
                f"{vm.total / (1024**3):.1f} GB ({vm.percent:.0f}%)"
            )
        )

        # E/S (Disco)
        try:
            io = self.proc.io_counters()
            escrito_mb = io.write_bytes / (1024 * 1024)
            lido_mb = io.read_bytes / (1024 * 1024)
            ops = io.read_count + io.write_count
            self.lbl_io_write.configure(text=f"Escrito: {escrito_mb:.1f} MB")
            self.lbl_io_read.configure(text=f"Lido: {lido_mb:.1f} MB   |   Operações E/S: {ops:,}")
        except (AttributeError, psutil.AccessDenied):
            self.lbl_io_write.configure(text="E/S indisponível neste SO")

        # Trocas de contexto e filhos
        ctx = self.proc.num_ctx_switches()
        total_ctx = ctx.voluntary + ctx.involuntary
        self.lbl_ctx.configure(text=f"Trocas de contexto: {total_ctx:,}")
        if self.filhos_ativos:
            pids = ", ".join(str(p.pid) for p in self.filhos_ativos)
            self.lbl_filhos.configure(text=f"Processos filhos ativos ({len(self.filhos_ativos)}): PID {pids}")
        else:
            self.lbl_filhos.configure(text="Processos filhos ativos: nenhum")

        self.root.after(500, self._atualizar_metricas)

    def _ao_fechar(self) -> None:
        for p in self.filhos_ativos:
            if p.is_alive():
                p.terminate()
                p.join(timeout=1)
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except OSError:
                pass
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    RaioXSOApp(root)
    root.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
