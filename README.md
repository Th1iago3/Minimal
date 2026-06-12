# 🖥️ Minimal

> **Invisible Desktop Tweak** — deixa os nomes dos atalhos da Área de Trabalho completamente invisíveis, sem mover os ícones de lugar.

![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Free-green)
![Dependencies](https://img.shields.io/badge/Dependencies-None-brightgreen)

---

## ✨ Recursos

- 🚫 **Zero dependências externas** — apenas Python 3.10+ padrão
- 🔒 **Não requer administrador** — roda com permissões normais do usuário
- 🎨 **Menu interativo** com ASCII art colorida (ANSI)
- 💾 **Backup obrigatório** — cria `backup.json` antes de qualquer alteração; se falhar, nada é aplicado
- 🌐 **Detecção de idioma** automática (PT-BR / EN)
- 📁 **Suporta** `.lnk`, `.url` e `.appref-ms` no Desktop do usuário, Public e OneDrive
- 👻 **Caracteres verdadeiramente invisíveis** — usa apenas ZWJ, ZWNJ e ZWSP (sem pontos/dots no Explorer)
- 🔄 **Sempre reaplica** — não pula atalhos já invisíveis, renomeia todos com nomes únicos
- 🪵 **Log com ID único** por máquina — `minimal_<hash>.log` na mesma pasta do script
- ⚡ **Persistência inteligente** — ao ativar, registra no Windows para iniciar automaticamente
- 👁️ **Watcher em background** — monitora novos atalhos a cada 30s e aplica automaticamente, sem consumir quase nada de RAM (usa `pythonw` sem janela)
- 🖼️ **Preservação de ícones** — salva `IconLocation` no backup e reaplica após o rename, evitando ícones brancos (silencioso, sem logs nem saída no terminal)

---

## 📋 Requisitos

| Requisito | Versão |
|-----------|--------|
| Windows   | 10 ou 11 |
| Python    | 3.10+  |

---

## 🚀 Como usar

### Download

Baixe o arquivo `minimal.py` e coloque em qualquer pasta.

### Execução

```powershell
py -3 .\minimal.py
```

### Menu interativo

```
┌──────────────────────────────────────────────┐
│  [1]  Ativar     aplica e liga persistência   │
│  [2]  Desativar  remove persistência e restaura│
│  [3]  Restaurar  restaura tudo e remove persist│
│  [0]  Sair                                    │
└──────────────────────────────────────────────┘
```

| Opção | O que faz |
|-------|-----------|
| **1 — Ativar** | Renomeia todos os atalhos com nomes invisíveis + ativa persistência (inicia com o Windows e monitora novos atalhos automaticamente) |
| **2 — Desativar** | Remove a persistência do registro do Windows e restaura todos os nomes originais |
| **3 — Restaurar** | Igual ao Desativar — restaura tudo e remove persistência |

### Linha de comando (sem menu)

```powershell
py -3 .\minimal.py --enable     # ativa + persistência
py -3 .\minimal.py --disable    # desativa + restaura
py -3 .\minimal.py --restore    # restaura + remove persistência
```

---

## 📂 Arquivos criados

Todos os arquivos são salvos **na mesma pasta** do `minimal.py`:

```
📁 pasta-do-script/
├── minimal.py              ← script principal
├── backup.json             ← backup dos nomes originais
└── minimal_<id>.log        ← log detalhado (ID único por máquina)
```

> O `<id>` no nome do log é um hash curto de 8 caracteres baseado no nome de usuário e hostname, garantindo um log único por máquina.

---

## ⚡ Persistência

Ao escolher **Ativar**, o script:

1. Aplica nomes invisíveis em todos os atalhos
2. Registra-se no `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
3. Na próxima inicialização do Windows, executa em modo **watcher** (`--watch`)
4. O watcher roda em background via `pythonw.exe` (sem janela visível)
5. A cada 30 segundos verifica se há atalhos novos e aplica automaticamente
6. Consome **quase zero RAM** — apenas um loop com `time.sleep(30)`

Ao **Desativar** ou **Restaurar**, a entrada do registro é removida e o watcher não inicia mais.

---

## 🔐 Segurança

- ✅ Backup obrigatório antes de aplicar — sem backup, sem alteração
- ✅ Não apaga atalhos, não altera o alvo dos atalhos
- ✅ Restauração limpa o backup ao final
- ✅ Não requer privilégios de administrador
- ✅ Código aberto — revise antes de executar

---

## 🧪 Como funciona

O script renomeia os atalhos usando combinações de 3 caracteres Unicode de largura zero:

| Caractere | Unicode | Nome |
|-----------|---------|------|
| ​ | `U+200B` | Zero Width Space |
| ‌ | `U+200C` | Zero Width Non-Joiner |
| ‍ | `U+200D` | Zero Width Joiner |

Cada atalho recebe uma combinação única (base-3), garantindo que nenhum nome se repita. Esses caracteres não renderizam glifos no Windows Explorer (Segoe UI), então os ícones ficam sem texto visível.

---

## 📝 Licença

Uso livre no seu próprio computador. Revise o código antes de executar.
