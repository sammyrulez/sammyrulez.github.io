# Design: skill `write-pelican-post`

## Contesto

Il blog `sammyrulez.github.io` (branch `main`) è un progetto **Pelican 4.11** con plugin
`pelican-yaml-metadata`, contenuti in `content/`, tema `chunk`. I post attuali hanno
metadati **incoerenti** tra loro: alcuni usano front matter YAML (`---`, chiavi minuscole),
altri i metadati classici Pelican (`Title:`, `Category:`, `Slug:`, `Summary:`). Valori
disallineati su categoria (`blog` vs `AI`), autore (`samreghenzi` vs `Sam Reghenzi`),
casing dei tag e presenza dello slug.

## Scopo

Una skill di Claude Code che aiuta a scrivere e scaffoldare **nuovi** post Pelican con
metadati coerenti e ottimizzati per la SEO.

Fuori scope: normalizzare i post esistenti; editing dello stile/prosa.

## Posizione e nome

- Nome: `write-pelican-post`
- Percorso: `.claude/skills/write-pelican-post/SKILL.md` nel repo del blog, da portare sul
  branch `main` (dove vive il progetto Pelican).

## Formato canonico dei metadati (front matter YAML)

```yaml
---
title: "…"
date: 2026-07-15 22:48        # ora corrente, formato YYYY-MM-DD HH:MM
tags:
- AI
- LLM
category: blog                # sempre "blog"
author: samreghenzi           # sempre
description: "…"              # meta description SEO ~150–160 caratteri
slug: …                       # sempre esplicito, kebab-case dal titolo
---
```

### Regole di normalizzazione fisse

- `category`: sempre `blog`.
- `author`: sempre `samreghenzi`.
- `slug`: sempre presente, kebab-case derivato dal titolo.
- `date`: ora corrente, formato `YYYY-MM-DD HH:MM`.
- `description`: un solo spazio dopo i due punti (no doppio spazio).
- Blocco delimitato da `---`, chiavi minuscole, `tags` come lista YAML.

### Regole tag

- 3–6 tag per post.
- Acronimi noti in MAIUSCOLO: `AI`, `LLM`, `MCP`, `ML`.
- Tutto il resto in minuscolo: `devops`, `terraform`, `security`, `python`, ecc.
- Preferire il vocabolario già usato nel blog prima di introdurre tag nuovi.

Vocabolario tag di riferimento (dai post esistenti): AI, LLM, MCP, ML, Python, devops,
terraform, secops, dataengineering, security, oauth, claude, tokens, skills, motorcycle,
lifestyle, personal.

## Flusso operativo della skill

1. Raccoglie argomento/titolo e il contenuto del post (fornito o incollato dall'utente).
2. Deriva lo `slug` (kebab-case) e il filename `content/<slug>.md`.
3. Assembla il front matter YAML canonico secondo le regole sopra.
4. SEO: propone un `title` efficace, una `description` di ~150–160 caratteri e 3–6 tag
   coerenti col vocabolario esistente.
5. Scrive il file in `content/`.

## Contenuto della skill (file)

- `SKILL.md`: frontmatter (name, description con trigger su "scrivere/creare un post per
  il blog Pelican"), spec del front matter canonico, regole di normalizzazione, regole e
  vocabolario tag, regole SEO, workflow passo-passo, un esempio completo di post.
- Nessun file extra salvo che il riferimento cresca: mantenere tutto in `SKILL.md`.

## Criteri di successo

- Dato un argomento e del testo, la skill produce un file `content/<slug>.md` con front
  matter YAML conforme al formato canonico (tutte le regole rispettate).
- I tag rispettano il casing e attingono al vocabolario esistente.
- `title` e `description` sono adatti alla SEO (description ~150–160 caratteri).
