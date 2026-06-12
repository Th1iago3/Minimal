# Minimal v1.5

Invisible Desktop Tweak for Windows. Renames Desktop shortcuts to invisible
names while protecting `.lnk` icons and preserving the current Desktop icon
positions as much as Windows allows. No persistence, no admin privileges, no
external dependencies.

---

## PT-BR

Minimal deixa sua Area de Trabalho mais limpa renomeando atalhos para nomes
invisiveis. A versao v1.5 salva a posicao atual de cada atalho no backup antes
de aplicar e usa essa posicao original para restaurar o layout depois.

### Requisitos

- Windows 10 ou 11
- Python 3.10+
- Sem dependencias externas
- Nao requer administrador

### Uso

```powershell
py -3 .\minimal.py             # menu interativo
py -3 .\minimal.py --enable    # aplicar nomes invisiveis
py -3 .\minimal.py --restore   # restaurar nomes originais
```

### Menu

- `1` Aplicar: renomeia atalhos para nomes invisiveis
- `2` Restaurar: restaura nomes originais usando o backup
- `0` Sair

### Como funciona

- Encontra atalhos na Area de Trabalho do usuario, Area de Trabalho Publica e
  Area de Trabalho do OneDrive.
- Suporta `.lnk`, `.url` e `.appref-ms`.
- Usa apenas caracteres invisiveis aceitos pelo Windows:
  - `U+2800`
  - `U+3164`
  - `U+FFA0`
- Gera combinacoes unicas para evitar conflito de nomes.
- Cria `backup.json` antes de aplicar alteracoes.
- Se o backup falhar, a operacao e cancelada.
- Nao cria persistencia. Nada e adicionado em `Run`, Startup ou Tarefas
  Agendadas.
- O modo antigo `--watch` apenas remove inicializacao antiga e encerra.

### Desktop Position Guard

Quando um arquivo da Area de Trabalho e renomeado, o Explorer pode tratar o item
como novo e jogar o icone para outra posicao. Para evitar isso, o Minimal v1.4
usa o Desktop Position Guard.

O metodo v1.5:

1. Localiza a lista real de icones do Desktop no Explorer (`SysListView32`).
2. Le o texto e as coordenadas atuais de cada icone.
3. Salva a coordenada de cada atalho em `backup.json` junto com o nome original.
3. Renomeia ou restaura os atalhos.
4. Procura os novos nomes na mesma lista do Explorer.
5. Reaplica as coordenadas salvas com `LVM_SETITEMPOSITION32`.

Isso nao cria arquivos extras, nao altera resolucao, nao mexe no registro para
layout e nao reinicia o Explorer. O script usa a posicao atual que voce organizou
como fonte da verdade.

Observacao: se o Explorer estiver com organizacao automatica ativa, alinhamento
forcado, Desktop travado por politica, ou se o item ainda nao apareceu na lista
do Explorer, o Windows pode impedir a restauracao exata. Nesses casos o script
continua sem quebrar nada e mostra que as posicoes foram mantidas pelo Explorer.

### LNK Icon Guard

O LNK Icon Guard atua somente em atalhos `.lnk`.

Antes de renomear um `.lnk`, o script abre o atalho pela interface nativa do
Windows (`IShellLinkW` e `IPersistFile`). Se o atalho nao tiver um icone
explicito configurado, o script grava no proprio `.lnk` o caminho do executavel
alvo como `IconLocation`.

Isso significa:

- Nao cria arquivo de icone.
- Nao guarda cache de icone no `backup.json`.
- Nao injeta imagem dentro do atalho.
- Nao limpa o cache global do Explorer.
- Nao altera o alvo do atalho.
- Apenas fixa uma referencia nativa de icone que o proprio Windows entende.

Atalhos `.url` e `.appref-ms` nao usam o mesmo formato COM de `.lnk`; nesses
casos o Windows continua responsavel pelo icone.

### Se algum icone ficar branco

Mesmo com o LNK Icon Guard, o Explorer pode falhar por cache corrompido, atalho
quebrado, alvo removido ou permissao bloqueada. Por isso, ao final o script
mostra uma dica no idioma do sistema:

> Clique com o botao direito no atalho, abra Propriedades, clique em Alterar
> icone, selecione o icone original e clique em Aplicar.

Isso forca o Windows a salvar novamente a referencia de icone daquele atalho.

### Logs

Por padrao, o script mostra informacoes apenas no terminal.

Um arquivo `.log` so e criado em caso de aviso, erro, excecao ou conflito real.
Execucoes normais nao geram log em arquivo.

Arquivos gerados na pasta do script:

```text
minimal.py
backup.json
minimal_<id>.log   somente se houver erro ou conflito
```

### Restauracao

`--restore` restaura os nomes originais usando `backup.json`. Se houver conflito
com um arquivo existente, o script cria um nome alternativo seguro, como
`Nome (2).lnk`.

A restauracao tambem remove qualquer entrada antiga de inicializacao criada por
versoes anteriores.

### Seguranca

- Sem rede.
- Sem telemetria.
- Sem dependencias externas.
- Sem privilegios de administrador.
- Nao altera o destino dos atalhos.
- Nao move arquivos para fora da Area de Trabalho.
- Nao limpa cache global de icones.
- Nao cria persistencia.

---

## EN-US

Minimal makes your Windows Desktop cleaner by renaming shortcuts to invisible
names. Version v1.5 saves each shortcut's current position in the backup before
apply and uses that original position to restore the layout later.

### Requirements

- Windows 10 or 11
- Python 3.10+
- No external dependencies
- No admin privileges required

### Usage

```powershell
py -3 .\minimal.py             # interactive menu
py -3 .\minimal.py --enable    # apply invisible names
py -3 .\minimal.py --restore   # restore original names
```

### Menu

- `1` Apply: renames shortcuts to invisible names
- `2` Restore: restores original names using the backup
- `0` Exit

### How it works

- Finds shortcuts on the user Desktop, Public Desktop, and OneDrive Desktop.
- Supports `.lnk`, `.url`, and `.appref-ms`.
- Uses only Windows-safe invisible characters:
  - `U+2800`
  - `U+3164`
  - `U+FFA0`
- Generates unique combinations to avoid name conflicts.
- Creates `backup.json` before applying changes.
- If backup creation fails, the operation is cancelled.
- No persistence. Nothing is added to `Run`, Startup, or Scheduled Tasks.
- The old `--watch` mode only removes legacy startup entries and exits.

### Desktop Position Guard

When a Desktop file is renamed, Explorer may treat it as a new item and move the
icon somewhere else. Minimal v1.4 uses Desktop Position Guard to reduce that.

The v1.5 method:

1. Finds the real Desktop icon list inside Explorer (`SysListView32`).
2. Reads the current text and coordinates of each icon.
3. Stores each shortcut coordinate in `backup.json` together with its original name.
3. Renames or restores the shortcuts.
4. Finds the new names in Explorer's same icon list.
5. Reapplies the saved coordinates with `LVM_SETITEMPOSITION32`.

It does not create extra files, does not change display resolution, does not use
the registry for layout, and does not restart Explorer. The script treats your
current manually arranged layout as the source of truth.

Note: if Explorer has auto-arrange enabled, forced alignment, policy locks, or
if the item has not appeared in Explorer's list yet, Windows may prevent exact
position restoration. In that case the script continues safely and reports that
positions were kept by Explorer.

### LNK Icon Guard

LNK Icon Guard only affects `.lnk` shortcuts.

Before renaming a `.lnk`, the script opens the shortcut through the native
Windows interfaces (`IShellLinkW` and `IPersistFile`). If the shortcut does not
already have an explicit icon configured, the script writes the target executable
path into the shortcut as its `IconLocation`.

This means:

- It does not create icon files.
- It does not store icon cache in `backup.json`.
- It does not inject image data into the shortcut.
- It does not clear the global Explorer icon cache.
- It does not change the shortcut target.
- It only stores a native icon reference that Windows already understands.

`.url` and `.appref-ms` shortcuts do not use the same COM format as `.lnk`; in
those cases Windows remains responsible for icon handling.

### If an icon turns white

Even with LNK Icon Guard, Explorer can still fail because of a corrupted cache,
broken shortcut, removed target, or permission issue. For that reason, the
script prints a system-language hint at the end:

> Right-click the shortcut, open Properties, click Change Icon, pick the
> original icon, and click Apply.

This forces Windows to save that shortcut's icon reference again.

### Logs

By default, the script prints information only to the terminal.

A `.log` file is created only when a warning, error, exception, or real conflict
occurs. Normal runs do not create a file log.

Generated files in the script folder:

```text
minimal.py
backup.json
minimal_<id>.log   only if an error or conflict occurs
```

### Restore

`--restore` restores original names using `backup.json`. If the original name
conflicts with an existing file, the script creates a safe alternative such as
`Name (2).lnk`.

Restore also removes any old startup entry created by previous versions.

### Safety

- No network.
- No telemetry.
- No external dependencies.
- No admin privileges.
- Does not change shortcut targets.
- Does not move files outside the Desktop.
- Does not clear the global icon cache.
- Does not create persistence.

---

## License

Free use on your own machine. Review the code before running.
