import os
import json
import unicodedata
import locale

# ----------------------------- configuracoes -----------------------------
NOME_APP = "Minimal"
VERSAO = "1.5"
PASTA_APP = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_BACKUP = os.path.join(PASTA_APP, "backup.json")
CARACTERES_INVISIVEIS = ["\u2800", "\u3164", "\uFFA0"]
EXTENSOES_ATALHO = [".lnk", ".url", ".appref-ms"]
INDICE_INVISIVEL = 1

# ----------------------------- cores -----------------------------
COR_RESET = "\033[0m"
COR_DIM = "\033[2m"
COR_NEGRITO = "\033[1m"
COR_CIANO = "\033[36m"
COR_MAGENTA = "\033[35m"
COR_VERDE = "\033[32m"
COR_AMARELO = "\033[33m"
COR_VERMELHO = "\033[31m"
COR_AZUL = "\033[34m"
COR_BRANCO = "\033[97m"
COR_CINZA = "\033[90m"

# ----------------------------- idioma -----------------------------
def detectar_idioma():
    try:
        idioma = locale.getdefaultlocale()[0]
        if idioma and idioma.startswith("pt"):
            return "pt"
    except:
        pass
    return "en"

TRADUCOES = {
    "pt": {
        "titulo": "Tweak para Tornar sua Area de Trabalho Minimalista",
        "menu_1": "Aplicar    renomeia atalhos para invisivel",
        "menu_2": "Restaurar  restaura nomes originais",
        "menu_0": "Sair",
        "escolha": "Selecione",
        "invalido": "Opcao invalida.",
        "ate_logo": "Ate logo.",
        "varrendo": "Varrendo atalhos da Area de Trabalho",
        "ok": "ok",
        "erro": "erro",
        "sem_backup": "Nenhum backup encontrado.",
        "backup_salvo": "Backup salvo em",
        "backup_falhou": "Falha ao criar backup.",
        "concluido": "Concluido.",
        "pressione_enter": "Pressione ENTER para continuar...",
        "sem_atalhos": "Nenhum atalho encontrado.",
    },
    "en": {
        "titulo": "A tweak to make your homescreen minimalist",
        "menu_1": "Apply     rename shortcuts to invisible",
        "menu_2": "Restore   restore original names",
        "menu_0": "Exit",
        "escolha": "Select",
        "invalido": "Invalid option.",
        "ate_logo": "Goodbye.",
        "varrendo": "Scanning desktop shortcuts",
        "ok": "ok",
        "erro": "error",
        "sem_backup": "No backup found.",
        "backup_salvo": "Backup saved at",
        "backup_falhou": "Backup failed.",
        "concluido": "Done.",
        "pressione_enter": "Press ENTER to continue...",
        "sem_atalhos": "No shortcuts found.",
    }
}

IDIOMA_ATUAL = detectar_idioma()
T = TRADUCOES[IDIOMA_ATUAL]

# ----------------------------- limpar terminal -----------------------------
def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")

# ----------------------------- logo -----------------------------
def logo():
    print("    ███╗   ███╗ ██╗ ███╗   ██╗ ██╗ ███╗   ███╗  █████╗  ██╗     ")
    print("    ████╗ ████║ ██║ ████╗  ██║ ██║ ████╗ ████║ ██╔══██╗ ██║     ")
    print("    ██╔████╔██║ ██║ ██╔██╗ ██║ ██║ ██╔████╔██║ ███████║ ██║     ")
    print("    ██║╚██╔╝██║ ██║ ██║╚██╗██║ ██║ ██║╚██╔╝██║ ██╔══██║ ██║     ")
    print("    ██║ ╚═╝ ██║ ██║ ██║ ╚████║ ██║ ██║ ╚═╝ ██║ ██║  ██║ ███████╗")
    print("    ╚═╝     ╚═╝ ╚═╝ ╚═╝  ╚═══╝ ╚═╝ ╚═╝     ╚═╝ ╚═╝  ╚═╝ ╚══════╝")
# ----------------------------- cabecalho -----------------------------
def mostrar_cabecalho():
    limpar_terminal()
    print()
    logo()
    print(f"    {COR_DIM}{COR_MAGENTA}{T['titulo']}{COR_RESET}")
    print(f"    {COR_CINZA}{'─' * 62}{COR_RESET}")
    print(f"    {COR_DIM}v{VERSAO}  ·  {IDIOMA_ATUAL}{COR_RESET}")
    print()

# ----------------------------- menu -----------------------------
def mostrar_menu():
    mostrar_cabecalho()
    print(f"    {COR_CINZA}┃{COR_RESET} {COR_VERDE}▶{COR_RESET} {COR_NEGRITO}{COR_VERDE}1{COR_RESET} {COR_CINZA}·{COR_RESET} {T['menu_1']}")
    print(f"    {COR_CINZA}┃{COR_RESET} {COR_AZUL}↶{COR_RESET} {COR_NEGRITO}{COR_AZUL}2{COR_RESET} {COR_CINZA}·{COR_RESET} {T['menu_2']}")
    print(f"    {COR_CINZA}┃{COR_RESET} {COR_VERMELHO}×{COR_RESET} {COR_NEGRITO}{COR_VERMELHO}0{COR_RESET} {COR_CINZA}·{COR_RESET} {T['menu_0']}")
    print(f"    {COR_CINZA}{'─' * 62}{COR_RESET}")
    try:
        return input(f"    {COR_MAGENTA}❯{COR_RESET} {COR_NEGRITO}{T['escolha']}{COR_RESET} {COR_CINZA}›{COR_RESET} ").strip()
    except:
        return "0"

def linha_ok(nome, rotulo=None):
    print(f"   {COR_VERDE}✓{COR_RESET}  {nome:<36} {COR_DIM}{rotulo or T['ok']}{COR_RESET}")

def linha_restaurado(nome):
    print(f"   {COR_VERDE}↶{COR_RESET}  {nome:<36} {COR_DIM}{T['ok']}{COR_RESET}")

def linha_erro(mensagem):
    print(f"   {COR_VERMELHO}✗{COR_RESET}  {mensagem}")

def linha_info(mensagem):
    print(f"   {COR_CIANO}»{COR_RESET}  {mensagem}")

# ----------------------------- pastas da area de trabalho -----------------------------
def pegar_pastas_area_de_trabalho():
    pastas = []
    perfil_usuario = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    publico = os.environ.get("PUBLIC", r"C:\Users\Public")
    onedrive = os.environ.get("OneDrive")
    
    pastas.append(os.path.join(perfil_usuario, "Desktop"))
    pastas.append(os.path.join(publico, "Desktop"))
    if onedrive:
        pastas.append(os.path.join(onedrive, "Desktop"))
        
    return [p for p in pastas if os.path.exists(p)]

# ----------------------------- listar atalhos -----------------------------
def listar_atalhos():
    atalhos = []
    for pasta in pegar_pastas_area_de_trabalho():
        try:
            for arquivo in os.listdir(pasta):
                caminho = os.path.join(pasta, arquivo)
                if os.path.isfile(caminho):
                    extensao = os.path.splitext(arquivo)[1].lower()
                    if extensao in EXTENSOES_ATALHO:
                        atalhos.append(caminho)
        except:
            pass
    return atalhos

# ----------------------------- nomes invisiveis -----------------------------
def eh_nome_invisivel(nome):
    if not nome:
        return False
    for caractere in nome:
        if caractere not in CARACTERES_INVISIVEIS:
            return False
    return True

def criar_nome_invisivel():
    global INDICE_INVISIVEL
    base = len(CARACTERES_INVISIVEIS)
    n = max(1, INDICE_INVISIVEL)
    resultado = []
    while n > 0:
        n -= 1
        resultado.append(CARACTERES_INVISIVEIS[n % base])
        n //= base
    resultado.reverse()
    INDICE_INVISIVEL += 1
    return "".join(resultado)

def nome_seguro_para_restaurar(nome, fallback="Atalho Minimal"):
    if not nome or nome == "?" or eh_nome_invisivel(nome):
        return fallback
    caracteres_invalidos = '<>:"/\\|?*'
    resultado = ""
    for c in nome:
        if c in caracteres_invalidos or unicodedata.category(c)[0] == 'C':
            resultado += "_"
        else:
            resultado += c
    resultado = resultado.strip(" ._")
    if not resultado or eh_nome_invisivel(resultado):
        resultado = fallback
    return resultado[:180]

# ----------------------------- backup -----------------------------
def carregar_backup():
    if os.path.exists(ARQUIVO_BACKUP):
        try:
            with open(ARQUIVO_BACKUP, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if "itens" not in dados:
                    dados["itens"] = {}
                return dados
        except:
            pass
    return {"itens": {}}

def salvar_backup(dados):
    try:
        with open(ARQUIVO_BACKUP, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def garantir_backup(atalhos):
    dados = carregar_backup()
    itens = dados["itens"]
    
    for caminho in atalhos:
        pasta = os.path.dirname(caminho)
        nome_arquivo = os.path.basename(caminho)
        nome_base, extensao = os.path.splitext(nome_arquivo)
        chave = caminho.lower()
        
        if chave in itens:
            itens[chave]["nome_atual"] = nome_arquivo
            continue
            
        if eh_nome_invisivel(nome_base):
            continue
            
        itens[chave] = {
            "nome_original": nome_seguro_para_restaurar(nome_base),
            "extensao_original": extensao,
            "pasta": pasta,
            "nome_atual": nome_arquivo,
        }
        
    if not salvar_backup(dados):
        linha_erro(T["backup_falhou"])
        return None
        
    linha_info(f"{T['backup_salvo']} {ARQUIVO_BACKUP}")
    return dados

# ----------------------------- aplicar -----------------------------
def aplicar_tweak():
    atalhos = listar_atalhos()
    dados = garantir_backup(atalhos)
    if not dados:
        return
        
    itens = dados["itens"]
    linha_info(T["varrendo"])
    print()
    
    if not atalhos:
        linha_erro(T["sem_atalhos"])
        return
        
    nomes_ocupados = {}
    for caminho in atalhos:
        pasta = os.path.dirname(caminho)
        if pasta not in nomes_ocupados:
            nomes_ocupados[pasta] = set()
        nomes_ocupados[pasta].add(os.path.basename(caminho).lower())
        
    for caminho in atalhos:
        try:
            pasta = os.path.dirname(caminho)
            nome_arquivo = os.path.basename(caminho)
            nome_base, extensao = os.path.splitext(nome_arquivo)
            chave = caminho.lower()
            
            if chave not in itens:
                continue
                
            entrada = itens[chave]
            
            if eh_nome_invisivel(nome_base):
                linha_ok(entrada.get("nome_original", nome_base), "reaplicado")
                continue
                
            nome_original = nome_seguro_para_restaurar(entrada.get("nome_original"), nome_base)
            
            while True:
                nome_invisivel = criar_nome_invisivel()
                novo_nome = nome_invisivel + extensao
                if novo_nome.lower() not in nomes_ocupados.get(pasta, set()):
                    break
                    
            novo_caminho = os.path.join(pasta, novo_nome)
            
            if novo_caminho == caminho:
                linha_ok(nome_original, T["ok"])
                continue
                
            os.rename(caminho, novo_caminho)
            
            entrada["nome_original"] = nome_original
            entrada["nome_atual"] = novo_nome
            nomes_ocupados.setdefault(pasta, set()).add(novo_nome.lower())
            
            linha_ok(nome_original, T["ok"])
            
        except Exception as e:
            linha_erro(f"{nome_arquivo}: {e}")
            
    salvar_backup(dados)
    print()
    linha_info(T["concluido"])

# ----------------------------- restaurar ----------------------------- 
def restaurar_tweak():
    dados = carregar_backup()
    itens = dados.get("itens", {})
    
    if not itens:
        linha_erro(T["sem_backup"])
        return
        
    linha_info(T["varrendo"])
    print()
    
    atalhos = listar_atalhos()
    caminhos_atuais = {c.lower(): c for c in atalhos}
    
    for chave, entrada in itens.items():
        try:
            pasta = entrada.get("pasta", "")
            nome_atual = entrada.get("nome_atual", "")
            caminho_atual = os.path.join(pasta, nome_atual).lower()
            
            if caminho_atual not in caminhos_atuais:
                continue
                
            caminho_real = caminhos_atuais[caminho_atual]
            nome_original = nome_seguro_para_restaurar(entrada.get("nome_original"), "Atalho")
            extensao = entrada.get("extensao_original", os.path.splitext(caminho_real)[1])
            
            novo_caminho = os.path.join(pasta, nome_original + extensao)
            
            if novo_caminho == caminho_real:
                continue
                
            if os.path.exists(novo_caminho):
                i = 2
                while os.path.exists(novo_caminho):
                    novo_caminho = os.path.join(pasta, f"{nome_original} ({i}){extensao}")
                    i += 1
                    
            os.rename(caminho_real, novo_caminho)
            linha_restaurado(nome_original)
            
        except Exception as e:
            linha_erro(f"{entrada.get('nome_original', chave)}: {e}")
            
    salvar_backup({"itens": {}})
    print()
    linha_info(T["concluido"])

# ----------------------------- principal -----------------------------
def principal():
    if os.name != "nt":
        print("Apenas para Windows.")
        return
        
    while True:
        escolha = mostrar_menu()
        print()
        
        if escolha == "1":
            aplicar_tweak()
        elif escolha == "2":
            restaurar_tweak()
        elif escolha == "0":
            print(f"   {COR_CIANO}{T['ate_logo']}{COR_RESET}")
            break
        else:
            linha_erro(T["invalido"])
            
        print()
        try:
            input(f"   {COR_DIM}{T['pressione_enter']}{COR_RESET}")
        except:
            print()
            break

if __name__ == "__main__":
    try:
        principal()
    except KeyboardInterrupt:
        print(f"\n   {COR_CIANO}{T['ate_logo']}{COR_RESET}")

