# Minimal v1.2

**Tweak para deixar sua Área de Trabalho do Windows minimalista.**
Renomeia atalhos (`.lnk`, `.url`, `.appref-ms`) para nomes invisíveis,
mantendo os ícones intactos.

> Sem dependências externas. Não requer administrador. Apenas Python 3.10+.

---

## ✨ Destaques desta versão

- **Sem mexer em ícones.** O script apenas renomeia o arquivo. Nada de
  reescrever `IconLocation` ou invalidar o cache do Explorer — o ícone
  exibido continua exatamente o mesmo.
- **Sem persistência.** Não escreve em `HKCU\...\Run`, não cria tarefa
  agendada e não fica em segundo plano. Você roda quando quiser.
  Entradas antigas de versões anteriores são removidas automaticamente.
- **Backup seguro e estável.** Cada atalho é salvo uma única vez com
  nome e extensão originais; novos atalhos são adicionados sem
  reescrever os antigos.
- **Log silencioso.** Por padrão tudo aparece só no terminal.
  O arquivo `minimal_<uid>.log` é criado **somente** se ocorrer
  erro ou conflito, e é apagado automaticamente quando passa de 20 KB.
- **Caracteres invisíveis seguros.** Usa `U+2800`, `U+3164`, `U+FFA0` —
  evita ZWSP/ZWJ que viravam `?` e causavam `WinError 123`.
- **Restauração robusta.** Localiza o atalho por caminho completo,
  nome atual ou nome invisível, e devolve a extensão original
  (`.lnk` continua `.lnk`, `.url` continua `.url`).

---

## 🚀 Uso

### Modo interativo

```bash
python minimal.py
```

Menu:

```
▶ 1 · Ativar     renomeia atalhos para invisível
■ 2 · Desativar  restaura nomes e limpa inicialização antiga
↶ 3 · Restaurar  restaura tudo com backup seguro
× 0 · Sair
```

### Linha de comando

```bash
python minimal.py --enable     # aplica
python minimal.py --disable    # restaura + limpa persistência antiga
python minimal.py --restore    # restaura
```

> `--watch` (de versões antigas) agora só remove a entrada antiga de
> inicialização e encerra.

---

## 📁 Arquivos gerados

Tudo fica na **mesma pasta do script**:

| Arquivo                | Quando aparece                                |
|------------------------|-----------------------------------------------|
| `backup.json`          | Sempre — guarda nome/extensão original        |
| `minimal_<uid>.log`    | Apenas em caso de erro ou conflito (≤ 20 KB)  |

Nada é gravado no registro do Windows, em `AppData`, na Startup ou no
Agendador de Tarefas.

---

## 🩹 Já tinha uma versão antiga com persistência?

Se uma versão anterior deixou algo iniciando com o Windows, limpe
manualmente (PowerShell):

```powershell
# Registry Run
Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'MinimalDesktopTweak' -ErrorAction SilentlyContinue
Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'Minimal' -ErrorAction SilentlyContinue

# Pasta Startup
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\minimal.lnk" -ErrorAction SilentlyContinue

# Tarefas agendadas
schtasks /Delete /TN "Minimal" /F 2>$null
schtasks /Delete /TN "MinimalRenamer" /F 2>$null
```

Em seguida rode `python minimal.py` → opção **3 (Restaurar)** para
voltar os nomes originais.

---

## ❓ FAQ

**O ícone vai sumir / virar branco?**
Não. Esta versão não toca em `IconLocation` nem dispara
`SHChangeNotify(ASSOCCHANGED)`. O `rename` preserva o file id NTFS, então
o Explorer mantém o ícone em cache.

**Atalhos novos no Desktop são renomeados sozinhos?**
Não. Rode `--enable` (ou opção **1**) quando quiser aplicar.

**Funciona em OneDrive / Public Desktop?**
Sim, os três caminhos padrão (`USERPROFILE\Desktop`, `PUBLIC\Desktop`,
`OneDrive\Desktop`) são varridos.

**Requer admin?**
Não.

---

## 🛡️ Segurança

- Sem rede, sem download, sem subprocess.
- Sem alterações no registro além de **remover** chaves antigas.
- `backup.json` é local e legível; pode inspecionar antes de restaurar.

---

## 📜 Licença

Uso pessoal. Sem garantias.
