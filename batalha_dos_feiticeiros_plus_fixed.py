# Batalha dos Feiticeiros — Edição Polida (Tkinter)
# Correções e melhorias estáveis
# - Dificuldade padrão "Normal" (100/100 para ambos)
# - Estado da dificuldade consistente (StringVar única)
# - Tooltip ipady corrigido
# - Contador de turnos consistente
# - Pequenos polimentos de UI/UX e atalhos
#
# Execução:
#   python batalha_dos_feiticeiros_plus_fixed.py

import random
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Utilidades de Som (opcionais) ----------
def _beep_ok(enabled=True):
    if not enabled:
        return
    try:
        import winsound
        winsound.Beep(880, 100)
    except Exception:
        try:
            root = tk._default_root
            if root: root.bell()
        except Exception:
            pass

def _beep_fail(enabled=True):
    if not enabled:
        return
    try:
        import winsound
        winsound.Beep(220, 140)
    except Exception:
        try:
            root = tk._default_root
            if root: root.bell()
        except Exception:
            pass

# ---------- Tooltip simples ----------
class Tooltip:
    def __init__(self, widget, text, bg="#111428", fg="#EAF0FF"):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.bg = bg
        self.fg = fg
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left", bg=self.bg, fg=self.fg,
                         relief="solid", borderwidth=1, font=("Segoe UI", 9))
        label.pack(ipadx=6, ipady=4)  # fix: ipady correto

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# ---------- App ----------
class BatalhaFeiticeirosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Batalha dos Feiticeiros — Edição Polida")
        self.root.geometry("880x660")
        self.root.minsize(760, 560)

        # Paleta
        self.bg = "#0f1226"
        self.fg = "#EAF0FF"
        self.accent = "#6C7CFF"
        self.danger = "#FF5C80"
        self.safe = "#30D158"
        self.panel = "#0a0d20"
        self.panel2 = "#101436"

        self.root.configure(bg=self.bg)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TProgressbar", troughcolor="#1a1f3d", background=self.accent, thickness=18)
        style.configure("HP.Horizontal.TProgressbar", troughcolor="#1a1f3d", background=self.safe, thickness=18)
        style.configure("Mana.Horizontal.TProgressbar", troughcolor="#1a1f3d", background="#7b9bff", thickness=12)

        style.configure("Status.TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 11))
        style.configure("Title.TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 20, "bold"))
        style.configure("Body.TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 10))
        style.configure("Small.TLabel", background=self.bg, foreground=self.fg, font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 11, "bold"))

        # Opções / Estado
        self.sound_enabled = True
        self.anim_speed_ms = 12  # menor = mais rápido
        self.dificuldade = "Normal"  # padrão
        self.var_dificuldade = tk.StringVar(value=self.dificuldade)  # variável única

        # Monta UI
        self._build_menu()
        self._build_ui()
        self._novo_jogo(first=True)

        # Atalhos
        self.root.bind("f", lambda e: self.turno_jogador("fogo"))
        self.root.bind("c", lambda e: self.turno_jogador("raio"))
        self.root.bind("m", lambda e: self.turno_jogador("meteoros"))
        self.root.bind("p", lambda e: self.usar_pocao())
        self.root.bind("d", lambda e: self.defender())
        self.root.bind("<Control-n>", lambda e: self._novo_jogo())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    # ---------- Menu ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        jogo = tk.Menu(menubar, tearoff=0)
        jogo.add_command(label="Novo Jogo (Ctrl+N)", command=self._novo_jogo)
        jogo.add_separator()
        jogo.add_command(label="Sair (Esc)", command=self.root.destroy)
        menubar.add_cascade(label="Jogo", menu=jogo)

        op = tk.Menu(menubar, tearoff=0)

        # Dificuldade com uma única StringVar
        dif = tk.Menu(op, tearoff=0)
        for d in ("Fácil", "Normal", "Difícil"):
            dif.add_radiobutton(
                label=d,
                value=d,
                variable=self.var_dificuldade,
                command=lambda dd=d: self._set_dificuldade(dd)
            )
        op.add_cascade(label="Dificuldade", menu=dif)

        # Velocidade
        vel = tk.Menu(op, tearoff=0)
        vel.add_radiobutton(label="Animação: Lenta", command=lambda: self._set_anim_speed(18))
        vel.add_radiobutton(label="Animação: Padrão", command=lambda: self._set_anim_speed(12))
        vel.add_radiobutton(label="Animação: Rápida", command=lambda: self._set_anim_speed(7))
        op.add_cascade(label="Velocidade", menu=vel)

        som_label = "Desativar Som" if self.sound_enabled else "Ativar Som"
        op.add_command(label=som_label, command=self._toggle_sound)
        menubar.add_cascade(label="Opções", menu=op)

        ajuda = tk.Menu(menubar, tearoff=0)
        ajuda.add_command(label="Atalhos e Dicas", command=self._mostrar_ajuda)
        ajuda.add_command(label="Sobre", command=lambda: messagebox.showinfo(
            "Sobre",
            "Batalha dos Feiticeiros — Edição Polida\n"
            "UI melhorada + correções (mana, defesa, status, dificuldade).\nFeito em Tkinter."
        ))
        menubar.add_cascade(label="Ajuda", menu=ajuda)

        self.root.config(menu=menubar)

    def _toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        _beep_ok(self.sound_enabled)
        # atualiza rótulo do menu reconstruindo-o
        self._build_menu()

    def _set_anim_speed(self, ms):
        self.anim_speed_ms = ms

    def _set_dificuldade(self, d):
        self.var_dificuldade.set(d)
        self.dificuldade = d
        messagebox.showinfo("Dificuldade", f"Dificuldade definida como: {d}\nEntrará em vigor em um novo jogo.")
        _beep_ok(self.sound_enabled)

    def _mostrar_ajuda(self):
        msg = (
            "Atalhos:\n"
            "F = Bola de Fogo | C = Raio Congelante | M = Chuva de Meteoros\n"
            "P = Poção de Cura | D = Defender | Ctrl+N = Novo Jogo | Esc = Sair\n\n"
            "Dicas:\n"
            "- Meteoros causa muito dano, mas tem menos precisão e custa mais mana.\n"
            "- Defender reduz o próximo dano recebido e pode salvar sua rodada.\n"
            "- Raio pode Congelar (chance) e fazer o inimigo perder a vez.\n"
            "- Fogo pode aplicar Queimadura (dano por turno).\n"
            "- Use as poções com sabedoria — elas passam a vez."
        )
        messagebox.showinfo("Atalhos e Dicas", msg)

    # ---------- UI principal ----------
    def _build_ui(self):
        header = ttk.Label(self.root, text="Batalha dos Feiticeiros", style="Title.TLabel")
        header.pack(pady=(16, 6))

        sub = ttk.Label(self.root, text="⚔️ Escolha feitiços, gerencie mana/poções, defenda e vença!", style="Body.TLabel")
        sub.pack(pady=(0, 10))

        status_frame = tk.Frame(self.root, bg=self.bg)
        status_frame.pack(fill="x", padx=16, pady=6)

        # Player
        player_frame = tk.Frame(status_frame, bg=self.panel2, highlightthickness=1, highlightbackground="#222742")
        player_frame.pack(side="left", expand=True, fill="x", padx=(0,8), ipady=4, ipadx=4)

        self.lbl_player = ttk.Label(player_frame, text="Você", style="Status.TLabel")
        self.lbl_player.pack(anchor="w", padx=6, pady=(6,0))

        self.pb_player = ttk.Progressbar(player_frame, maximum=100, value=100, mode="determinate", style="HP.Horizontal.TProgressbar")
        self.pb_player.pack(fill="x", padx=6, pady=(6,2))
        self.lbl_player_hp = ttk.Label(player_frame, text="Vida: 100/100", style="Small.TLabel")
        self.lbl_player_hp.pack(anchor="w", padx=6)

        self.pb_player_mana = ttk.Progressbar(player_frame, maximum=100, value=100, mode="determinate", style="Mana.Horizontal.TProgressbar")
        self.pb_player_mana.pack(fill="x", padx=6, pady=(6,2))
        self.lbl_player_mana = ttk.Label(player_frame, text="Mana: 100/100", style="Small.TLabel")
        self.lbl_player_mana.pack(anchor="w", padx=6)

        self.lbl_pocoes = ttk.Label(player_frame, text="Poções: 3", style="Small.TLabel")
        self.lbl_pocoes.pack(anchor="w", padx=6, pady=(2,6))

        # Enemy
        enemy_frame = tk.Frame(status_frame, bg=self.panel2, highlightthickness=1, highlightbackground="#222742")
        enemy_frame.pack(side="left", expand=True, fill="x", padx=(8,0), ipady=4, ipadx=4)

        self.lbl_enemy = ttk.Label(enemy_frame, text="Inimigo", style="Status.TLabel")
        self.lbl_enemy.pack(anchor="w", padx=6, pady=(6,0))

        self.pb_enemy = ttk.Progressbar(enemy_frame, maximum=100, value=100, mode="determinate", style="HP.Horizontal.TProgressbar")
        self.pb_enemy.pack(fill="x", padx=6, pady=(6,2))
        self.lbl_enemy_hp = ttk.Label(enemy_frame, text="Vida: 100/100", style="Small.TLabel")
        self.lbl_enemy_hp.pack(anchor="w", padx=6)

        self.pb_enemy_mana = ttk.Progressbar(enemy_frame, maximum=100, value=100, mode="determinate", style="Mana.Horizontal.TProgressbar")
        self.pb_enemy_mana.pack(fill="x", padx=6, pady=(6,2))
        self.lbl_enemy_mana = ttk.Label(enemy_frame, text="Mana: 100/100", style="Small.TLabel")
        self.lbl_enemy_mana.pack(anchor="w", padx=6, pady=(0,6))

        # Arena
        arena = tk.Frame(self.root, bg=self.bg)
        arena.pack(fill="x", padx=16)
        self.canvas = tk.Canvas(arena, height=160, bg=self.panel, highlightthickness=0)
        self.canvas.pack(fill="x")
        self.sprite_player = self.canvas.create_rectangle(80, 60, 130, 120, fill="#6C7CFF", outline="")
        self.sprite_enemy  = self.canvas.create_rectangle(720, 60, 770, 120, fill="#FF6C93", outline="")
        self.particle = self.canvas.create_oval(-10, -10, -10, -10, fill="#ffffff", outline="")
        self.float_texts = []

        # Botões
        actions = tk.Frame(self.root, bg=self.bg)
        actions.pack(fill="x", padx=16, pady=10)

        self.btn_fogo = ttk.Button(actions, text="🔥 Fogo\n(30 dano, 60% acerto, 25 mana)", command=lambda: self.turno_jogador("fogo"))
        self.btn_raio = ttk.Button(actions, text="❄️ Raio\n(20 dano, 80% acerto, 20 mana)", command=lambda: self.turno_jogador("raio"))
        self.btn_meteoros = ttk.Button(actions, text="☄️ Meteoros\n(50 dano, 30% acerto, 40 mana)", command=lambda: self.turno_jogador("meteoros"))
        self.btn_defender = ttk.Button(actions, text="🛡️ Defender\n(-50% próximo dano)", command=self.defender)
        self.btn_pocao = ttk.Button(actions, text="🧪 Poção de Cura\n(+25 vida)", command=self.usar_pocao)

        for b in (self.btn_fogo, self.btn_raio, self.btn_meteoros, self.btn_defender, self.btn_pocao):
            b.pack(side="left", expand=True, fill="x", padx=6)

        Tooltip(self.btn_fogo, "Chance de aplicar Queimadura (5 de dano por 2 turnos).")
        Tooltip(self.btn_raio, "Pode Congelar (alvo perde a próxima ação, 30% de chance).")
        Tooltip(self.btn_meteoros, "Pequena chance de Atordoar (20%). Muito dano.")
        Tooltip(self.btn_defender, "Reduz pela metade o próximo dano que você receber.")
        Tooltip(self.btn_pocao, "Cura 25 de vida. Usa o turno.")

        # Log
        log_frame = tk.Frame(self.root, bg=self.bg)
        log_frame.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        self.txt_log = tk.Text(log_frame, height=9, wrap="word", bg=self.panel, fg=self.fg,
                               insertbackground=self.fg, relief="flat", padx=10, pady=10)
        self.txt_log.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.txt_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.txt_log.config(yscrollcommand=scrollbar.set)

        footer = tk.Frame(self.root, bg=self.bg)
        footer.pack(fill="x", padx=16, pady=(0, 14))
        self.btn_reiniciar = ttk.Button(footer, text="🔁 Reiniciar", command=self._novo_jogo)
        self.btn_reiniciar.pack(side="right")

    # ---------- Mecânicas ----------
    def _novo_jogo(self, first=False):
        # Dificuldade atual (ou "Normal" por padrão)
        self.dificuldade = self.var_dificuldade.get() or "Normal"

        # Ajuste por dificuldade
        if self.dificuldade == "Fácil":
            hp = 110; mana = 110; enemy_hp = 90; enemy_acc_mod = -5
        elif self.dificuldade == "Difícil":
            hp = 90; mana = 100; enemy_hp = 120; enemy_acc_mod = +8
        else:  # Normal
            hp = 100; mana = 100; enemy_hp = 100; enemy_acc_mod = 0
        self.enemy_acc_mod = enemy_acc_mod

        self.vida_jogador = hp
        self.vida_inimigo = enemy_hp
        self.mana_jogador = mana
        self.mana_inimigo = 100
        self.pocoes = 3
        self.defesa_ativa = False
        self.defesa_inimigo = False
        self.status_player = {"queimadura": 0, "congelado": 0, "atordoado": 0}
        self.status_enemy = {"queimadura": 0, "congelado": 0, "atordoado": 0}
        self.turnos = 0
        self.acertos_player = 0
        self.acertos_enemy = 0
        self.game_over = False

        self._atualizar_barras()
        self._set_botoes_state("normal")
        self._log_limpar()
        if not first:
            _beep_ok(self.sound_enabled)
        self._log(f"🧙‍♂️ Nova batalha começando em {self.dificuldade}!")
        self._log("Dica: Use DEFENDER para sobreviver a turnos críticos e gerencie sua MANA.")
        self._atualizar_textos()

    def _atualizar_barras(self):
        def clamp(v): return max(0, min(100, v))
        self.pb_player["value"] = clamp(self.vida_jogador)
        self.pb_enemy["value"] = clamp(self.vida_inimigo)
        self.lbl_player_hp.config(text=f"Vida: {self.vida_jogador}/100")
        self.lbl_enemy_hp.config(text=f"Vida: {self.vida_inimigo}/100")
        self.pb_player_mana["value"] = clamp(self.mana_jogador)
        self.pb_enemy_mana["value"] = clamp(self.mana_inimigo)
        self.lbl_player_mana.config(text=f"Mana: {self.mana_jogador}/100")
        self.lbl_enemy_mana.config(text=f"Mana: {self.mana_inimigo}/100")
        self.lbl_pocoes.config(text=f"Poções: {self.pocoes}")

    def _log(self, texto):
        self.txt_log.insert("end", texto + "\n")
        self.txt_log.see("end")

    def _log_limpar(self):
        self.txt_log.delete("1.0", "end")

    def _set_botoes_state(self, state):
        for b in (self.btn_fogo, self.btn_raio, self.btn_meteoros, self.btn_defender, self.btn_pocao):
            b.config(state=state)

    def _atualizar_textos(self):  # reservado para futuras labels dinâmicas
        pass

    # Dados de mágicas e custos
    def _dados_feitico(self, tipo):
        if tipo == "fogo":
            return {"nome": "Bola de Fogo", "dano": 30, "chance": 60, "emoji": "🔥", "mana": 25, "status": "queimadura", "status_chance": 40}
        if tipo == "raio":
            return {"nome": "Raio Congelante", "dano": 20, "chance": 80, "emoji": "❄️", "mana": 20, "status": "congelado", "status_chance": 30}
        if tipo == "meteoros":
            return {"nome": "Chuva de Meteoros", "dano": 50, "chance": 30, "emoji": "☄️", "mana": 40, "status": "atordoado", "status_chance": 20}
        return {"nome": "Feitiço", "dano": 0, "chance": 0, "emoji": "✨", "mana": 0, "status": None, "status_chance": 0}

    # ---------- Animações ----------
    def _animar_tiro(self, origem_x, origem_y, destino_x, destino_y, steps=20):
        self.canvas.coords(self.particle, origem_x-6, origem_y-6, origem_x+6, origem_y+6)
        dx = (destino_x - origem_x) / steps
        dy = (destino_y - origem_y) / steps

        def step(i=0):
            if i > steps:
                self.canvas.coords(self.particle, -10, -10, -10, -10)
                return
            self.canvas.move(self.particle, dx, dy)
            self.root.after(self.anim_speed_ms, lambda: step(i+1))

        step()

    def _flash_sprite(self, target, color_temp="#ffffff"):
        color = self.canvas.itemcget(target, "fill")
        def seq(times=3):
            if times == 0:
                self.canvas.itemconfig(target, fill=color)
                return
            self.canvas.itemconfig(target, fill=color_temp)
            self.root.after(60, lambda: (self.canvas.itemconfig(target, fill=color),
                                         self.root.after(60, lambda: seq(times-1))))
        seq()

    def _shake(self, target, distance=6, times=6):
        # Tremor lateral
        def go(i=0, dir=1):
            if i >= times:
                return
            self.canvas.move(target, distance*dir, 0)
            self.root.after(25, lambda: (self.canvas.move(target, -distance*dir, 0),
                                         self.root.after(25, lambda: go(i+1, -dir))))
        go()

    def _float_text(self, x, y, text, color="#EAF0FF"):
        t = self.canvas.create_text(x, y, text=text, fill=color, font=("Segoe UI", 12, "bold"))
        def step(i=0):
            if i > 18:
                self.canvas.delete(t)
                return
            self.canvas.move(t, 0, -2)
            self.root.after(30, lambda: step(i+1))
        step()

    # ---------- Turnos ----------
    def _aplicar_status(self, quem):
        # retorna True se ação deve ser pulada (congelado/atordoado)
        status = self.status_enemy if quem == "enemy" else self.status_player
        skip = False

        # Queimadura: 5 de dano por 2 turnos
        if status["queimadura"] > 0:
            if quem == "enemy":
                self.vida_inimigo -= 5
                self._float_text(745, 55, "-5 🔥", self.danger)
                self._flash_sprite(self.sprite_enemy)
            else:
                self.vida_jogador -= 5
                self._float_text(105, 55, "-5 🔥", self.danger)
                self._flash_sprite(self.sprite_player)
            status["queimadura"] -= 1

        # Congelado / Atordoado: perde a ação
        for k in ("congelado", "atordoado"):
            if status[k] > 0:
                skip = True
                status[k] -= 1

        self._atualizar_barras()
        return skip

    def _critico(self):
        # 12% de chance de crítico (x1.6)
        return random.random() < 0.12

    def _consumir_mana(self, de_quem, custo):
        if de_quem == "player":
            if self.mana_jogador < custo:
                return False
            self.mana_jogador -= custo
        else:
            if self.mana_inimigo < custo:
                return False
            self.mana_inimigo -= custo
        return True

    def _contabiliza_turno_player(self):
        # conta turno sempre que sua vez passa (ação ou impedimento)
        self.turnos += 1
        # Regeneração leve de mana no fim do turno do jogador
        self.mana_jogador = min(100, self.mana_jogador + 6)

    def turno_jogador(self, tipo):
        if self.game_over:
            return

        # Checa status no INÍCIO do turno do jogador
        if self._aplicar_status("player"):
            self._log("🧊 Você está impedido de agir neste turno!")
            self._contabiliza_turno_player()
            self._apos_acao_jogador(passou=True)
            return

        dados = self._dados_feitico(tipo)
        if not self._consumir_mana("player", dados["mana"]):
            self._log("⚠️ Mana insuficiente! Use uma poção ou DEFENDER enquanto regenera mana.")
            _beep_fail(self.sound_enabled)
            return

        self._log(f"Você lançou {dados['emoji']} {dados['nome']} ...")
        self._animar_tiro(130, 90, 720, 90)

        acerto = random.randint(1, 100)
        if acerto <= dados["chance"]:
            dano = dados["dano"]
            if self._critico():
                dano = int(dano * 1.6)
                self._log("💥 Acerto CRÍTICO!")
            if self.defesa_inimigo:
                dano = int(dano * 0.5)
                self.defesa_inimigo = False
                self._log("🛡️ O inimigo estava defendendo! Dano reduzido.")
            self.vida_inimigo -= dano
            self._float_text(745, 60, f"-{dano}", self.fg)
            self._shake(self.sprite_enemy)
            self._flash_sprite(self.sprite_enemy)
            self.acertos_player += 1
            _beep_ok(self.sound_enabled)

            # Aplica status
            if dados["status"] and random.randint(1,100) <= dados["status_chance"]:
                self.status_enemy[dados["status"]] += 1 if dados["status"] != "queimadura" else 2
                self._log(f"✨ Efeito aplicado: {dados['status'].capitalize()}!")

        else:
            self._log("❌ Você errou o feitiço!")
            _beep_fail(self.sound_enabled)

        self.vida_inimigo = max(0, self.vida_inimigo)
        self._atualizar_barras()

        if self._verifica_fim():
            return

        self._contabiliza_turno_player()
        self._apos_acao_jogador()

    def _apos_acao_jogador(self, passou=False):
        self._atualizar_barras()
        self._set_botoes_state("disabled")
        self.root.after(650, self.turno_inimigo)

    def defender(self):
        if self.game_over:
            return
        if self._aplicar_status("player"):
            self._log("🧊 Você não conseguiu se defender — status impeditivo.")
            self._contabiliza_turno_player()
            self._apos_acao_jogador(passou=True)
            return
        self.defesa_ativa = True
        self._log("🛡️ Você assume posição DEFENSIVA! (metade do dano no próximo golpe)")
        self._flash_sprite(self.sprite_player, color_temp="#7cff9d")
        self._contabiliza_turno_player()
        self._apos_acao_jogador()

    def usar_pocao(self):
        if self.game_over:
            return

        if self._aplicar_status("player"):
            self._log("🧊 Você perdeu a chance de usar a poção neste turno.")
            self._contabiliza_turno_player()
            self._apos_acao_jogador(passou=True)
            return

        if self.pocoes <= 0:
            self._log("⚠️ Você não tem mais poções! Perdeu a vez.")
            self._set_botoes_state("disabled")
            self._contabiliza_turno_player()
            self.root.after(650, self.turno_inimigo)
            return

        self.pocoes -= 1
        cura = 25
        vida_antes = self.vida_jogador
        self.vida_jogador = min(100, self.vida_jogador + cura)
        ganho = self.vida_jogador - vida_antes

        self._log(f"🧪 Você usou uma poção e recuperou {ganho} de vida!")
        self._flash_sprite(self.sprite_player, color_temp="#7cff9d")
        _beep_ok(self.sound_enabled)

        self._atualizar_barras()

        if self._verifica_fim():
            return

        self._contabiliza_turno_player()
        self._apos_acao_jogador(passou=True)

    def _escolha_ia(self):
        # IA simples com prioridade baseada em estado e mana
        options = ["fogo", "raio", "meteoros"]
        weights = [1, 1, 1]
        if self.vida_jogador < 35:
            weights = [1, 1, 2]
        if self.mana_inimigo < 25:
            weights = [1, 2, 0.5]
        if self.defesa_ativa:
            weights = [1, 2.5, 0.7]

        total = sum(weights)
        pick = random.uniform(0, total)
        upto = 0
        for opt, w in zip(options, weights):
            if upto + w >= pick:
                return opt
            upto += w
        return random.choice(options)

    def turno_inimigo(self):
        if self.game_over:
            return

        # Status do inimigo no INÍCIO do turno dele
        if self._aplicar_status("enemy"):
            self._log("🧊 Inimigo está impedido de agir neste turno!")
            self._final_turno_inimigo()
            return

        # Chance do inimigo se defender se estiver com pouca vida
        if self.vida_inimigo <= 25 and random.random() < 0.35:
            self.defesa_inimigo = True
            self._log("🛡️ Inimigo está DEFENDENDO!")
            self._flash_sprite(self.sprite_enemy, color_temp="#ffb4c7")
            self._final_turno_inimigo()
            return

        # Escolha e mana check
        tipo = self._escolha_ia()
        dados = self._dados_feitico(tipo)

        # Se sem mana, recupera mana e passa o turno
        if not self._consumir_mana("enemy", dados["mana"]):
            self._log("💤 Inimigo está canalizando mana... (+10)")
            self.mana_inimigo = min(100, self.mana_inimigo + 10)
            self._final_turno_inimigo()
            return

        self._log(f"Inimigo lançou {dados['emoji']} {dados['nome']} ...")
        self._animar_tiro(720, 90, 130, 90)

        acc_mod = self.enemy_acc_mod
        acerto = random.randint(1, 100)
        if acerto <= max(5, min(95, dados["chance"] + acc_mod)):
            dano = dados["dano"]
            if self._critico():
                dano = int(dano * 1.6)
                self._log("💥 Inimigo acertou um CRÍTICO!")
            if self.defesa_ativa:
                dano = int(dano * 0.5)
                self.defesa_ativa = False
                self._log("🛡️ Sua defesa reduziu o dano pela metade!")
            self.vida_jogador -= dano
            self._float_text(105, 60, f"-{dano}", self.fg)
            self._shake(self.sprite_player)
            self._flash_sprite(self.sprite_player)
            self.acertos_enemy += 1
            _beep_fail(self.sound_enabled)

            # Aplica status
            if dados["status"] and random.randint(1,100) <= dados["status_chance"]:
                self.status_player[dados["status"]] += 1 if dados["status"] != "queimadura" else 2
                self._log(f"✨ Efeito aplicado em você: {dados['status'].capitalize()}!")
        else:
            self._log("🙌 O inimigo errou o feitiço!")
            _beep_ok(self.sound_enabled)

        self.vida_jogador = max(0, self.vida_jogador)
        self._atualizar_barras()

        if self._verifica_fim():
            return

        self._final_turno_inimigo()

    def _final_turno_inimigo(self):
        # Regeneração leve de mana no fim do turno do inimigo
        self.mana_inimigo = min(100, self.mana_inimigo + 6)
        self._atualizar_barras()
        self._set_botoes_state("normal")

    def _verifica_fim(self):
        if self.vida_inimigo <= 0:
            self.vida_inimigo = 0
            self._atualizar_barras()
            self._log("\n🎉 Você venceu a batalha!")
            self._encerrar("Você venceu!")
            return True
        if self.vida_jogador <= 0:
            self.vida_jogador = 0
            self._atualizar_barras()
            self._log("\n💀 Você foi derrotado pelo inimigo!")
            self._encerrar("Você perdeu!")
            return True
        return False

    def _encerrar(self, titulo):
        self.game_over = True
        self._set_botoes_state("disabled")
        # Estatísticas básicas
        total_turnos = self.turnos
        try:
            acc = round((self.acertos_player / max(1, total_turnos)) * 100, 1)
        except Exception:
            acc = 0.0
        self.root.after(250, lambda: messagebox.showinfo(
            "Fim de Jogo",
            f"{titulo}\n\nTurnos (você): {total_turnos}\n"
            f"Acertos (você): {self.acertos_player}\n"
            f"Acertos (inimigo): {self.acertos_enemy}\n"
            f"Precisão estimada: {acc}%"
        ))

# ---------- Main ----------
def main():
    root = tk.Tk()
    app = BatalhaFeiticeirosApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
