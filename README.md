# Minimal

Invisible Desktop Tweak for Windows. Renames Desktop shortcuts to zero-width invisible names without moving icons.

---

## PT-BR

Renomeia os atalhos da Área de Trabalho com caracteres invisíveis, sem mover os ícones.

### Requisitos
- Windows 10 ou 11
- Python 3.10+
- Sem dependências externas
- Não requer administrador

### Uso

```powershell
py -3 .\minimal.py             # menu interativo
py -3 .\minimal.py --enable    # aplica + ativa persistência
py -3 .\minimal.py --disable   # restaura + remove persistência
py -3 .\minimal.py --restore   # restaura + remove persistência
```

### Menu
- `1` Ativar — aplica nomes invisíveis e liga persistência
- `2` Desativar — remove persistência e restaura nomes
- `3` Restaurar — restaura tudo e remove persistência
- `0` Sair

### Como funciona
- Usa `U+200B`, `U+200C` e `U+200D` (zero-width) em combinações únicas por atalho.
- Suporta `.lnk`, `.url`, `.appref-ms` em Desktop do usuário, Public Desktop e OneDrive Desktop.
- Backup obrigatório em `backup.json`; se falhar, nada é aplicado.
- Preserva o ícone original: ao renomear `.lnk`, reescreve `IconLocation` apontando para o executável-alvo via `IShellLinkW` (corrige ícone branco). Operação silenciosa.
- Persistência: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` → executa `--watch` via `pythonw.exe`.
- Watcher: verifica novos atalhos a cada 30s e aplica automaticamente. Consumo de RAM mínimo.

### Arquivos gerados (mesma pasta do script)
```
minimal.py
backup.json
minimal_<id>.log
```
`<id>` = hash de 8 caracteres de `USERNAME@COMPUTERNAME`.

### Segurança
- Não altera o alvo dos atalhos.
- Restauração limpa o backup.
- Sem privilégios de administrador.

---

## EN-US

Renames Windows Desktop shortcuts using zero-width invisible characters, without moving icons.

### Requirements
- Windows 10 or 11
- Python 3.10+
- No external dependencies
- No administrator required

### Usage

```powershell
py -3 .\minimal.py             # interactive menu
py -3 .\minimal.py --enable    # apply + enable persistence
py -3 .\minimal.py --disable   # restore + remove persistence
py -3 .\minimal.py --restore   # restore + remove persistence
```

### Menu
- `1` Enable — apply invisible names and enable persistence
- `2` Disable — remove persistence and restore names
- `3` Restore — restore all and remove persistence
- `0` Exit

### How it works
- Uses `U+200B`, `U+200C`, `U+200D` (zero-width) in unique combinations per shortcut.
- Supports `.lnk`, `.url`, `.appref-ms` in user Desktop, Public Desktop and OneDrive Desktop.
- Mandatory backup at `backup.json`; if it fails, nothing is applied.
- Preserves original icon: when renaming `.lnk`, rewrites `IconLocation` to point at the target executable via `IShellLinkW` (fixes white/blank icons). Silent operation.
- Persistence: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` → runs `--watch` through `pythonw.exe`.
- Watcher: scans for new shortcuts every 30s and applies automatically. Minimal RAM usage.

### Generated files (same folder as the script)
```
minimal.py
backup.json
minimal_<id>.log
```
`<id>` = 8-char hash of `USERNAME@COMPUTERNAME`.

### Safety
- Does not change shortcut targets.
- Restore clears the backup.
- No admin privileges required.

---

## License
Free use on your own machine. Review the code before running.
