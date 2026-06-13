# Minimal v1.5

---

# 🇧🇷 Português

## O que é?

O Minimal deixa sua Área de Trabalho mais limpa ocultando os nomes dos atalhos através de caracteres invisíveis compatíveis com o Windows.

A versão **v1.5** também salva e restaura a posição dos ícones sempre que possível.

## Requisitos

* Windows 10 ou 11
* Python 3.10+
* Sem dependências externas
* Não requer administrador

## Uso

```powershell
py -3 .\minimal.py
```

Ou:

```powershell
py -3 .\minimal.py --enable
py -3 .\minimal.py --restore
```

## Menu

```text
1 - Aplicar nomes invisíveis
2 - Restaurar nomes originais
0 - Sair
```

## Recursos

* Suporte para `.lnk`, `.url` e `.appref-ms`
* Mantém os ícones originais dos atalhos
* Preserva a posição dos ícones quando possível
* Gera backup automático antes de qualquer alteração
* Não cria inicialização automática
* Não modifica o destino dos atalhos
* Não requer privilégios elevados

## Arquivos gerados

```text
minimal.py
backup.json
minimal_<id>.log   (somente em caso de erro)
```

## Restauração

Para voltar tudo ao normal:

```powershell
py -3 .\minimal.py --restore
```

Os nomes originais serão restaurados usando o backup salvo.

## Segurança

* Sem conexão com a internet
* Sem telemetria
* Sem persistência
* Sem alterações no Registro para layout
* Sem reiniciar o Explorer

---

# 🇺🇸 English

## What is it?

Minimal cleans up your Windows Desktop by replacing shortcut names with invisible characters supported by Windows.

Version **v1.5** also saves and restores icon positions whenever possible.

## Requirements

* Windows 10 or 11
* Python 3.10+
* No external dependencies
* No administrator privileges required

## Usage

```powershell
py -3 .\minimal.py
```

Or:

```powershell
py -3 .\minimal.py --enable
py -3 .\minimal.py --restore
```

## Menu

```text
1 - Apply invisible names
2 - Restore original names
0 - Exit
```

## Features

* Supports `.lnk`, `.url`, and `.appref-ms`
* Preserves shortcut icons
* Keeps desktop icon positions whenever possible
* Creates an automatic backup before changes
* No startup entries
* Does not modify shortcut targets
* No elevated privileges required

## Generated files

```text
minimal.py
backup.json
minimal_<id>.log   (only if an error occurs)
```

## Restore

To restore original names:

```powershell
py -3 .\minimal.py --restore
```

The original names will be recovered from the saved backup.

## Safety

* No network access
* No telemetry
* No persistence
* No registry-based layout modifications
* No Explorer restart required

---

## License

Free to use and modify. Review the source code before running.
