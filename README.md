# Minimal v1.5

---

# 🇧🇷 Português

## O que é?

O Minimal deixa sua Área de Trabalho mais limpa ocultando os nomes dos atalhos através de caracteres invisíveis.

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
1 - Aplicar
2 - Restaurar
0 - Sair
```

## Recursos

* Suporte para `.lnk`, `.url` e `.appref-ms`
* Gera backup automático
* Não requer privilégios elevados

## Arquivos gerados

```text
minimal.py
backup.json
minimal_<id>.log   (em caso de erro)
```

## Restauração

Para voltar tudo ao normal:

```powershell
py -3 .\minimal.py --restore
```

Os nomes originais serão restaurados usando o backup salvo.

## Segurança

* Sem conexão com a internet
* Não faz injeção ALGUMA de nenhum programa internamente / kernel
* Simples e manutenção fácil.

---

# 🇺🇸 English

## What is it?

Minimal cleans up your Windows Desktop by replacing shortcut names with invisible characters.

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
1 - Apply
2 - Restore
0 - Exit
```

## Features

* Supports `.lnk`, `.url`, and `.appref-ms`
* Creates an automatic backup
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
* Does not inject ANY program internally / kernel
* Simple and easy maintenance.

---

## License

Free to use and modify. Review the source code before running.
