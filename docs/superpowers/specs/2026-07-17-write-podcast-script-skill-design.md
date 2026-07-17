# Skill `write-podcast-script` — Design

**Data:** 2026-07-17
**Stato:** approvato (design)

## Obiettivo

Una skill/command per Claude Code che converte un post del blog Pelican nello
script di un episodio di podcast in **stile parlato**, scrivendo il risultato in
un file. Lo scopo è avere, da un articolo scritto, un testo pronto da leggere ad
alta voce (o da dare in pasto a una TTS).

## Natura e collocazione

- È una **skill di istruzioni** (come `write-pelican-post`), non codice: un
  singolo file `.claude/skills/write-podcast-script/SKILL.md` con front matter
  (`name`, `description`) + corpo.
- Va creata sul branch **`main`**, indipendente dal lavoro Substack.
- Nessun test automatico: la verifica è lanciarla su un post reale e rileggere
  l'output. La skill include una checklist di auto-verifica e una tabella
  "Common Mistakes", nello stile della skill esistente.

## Decisioni di design

| Aspetto | Scelta |
|---|---|
| Formato | Monologo a voce singola (narratore = l'autore, prima persona) |
| Fedeltà/lunghezza | Adattamento integrale (copre tutti i punti del post, riscritti per il parlato) |
| Codice e tecnica | Spiegati **solo nel significato**, mai letti nella sintassi |
| Input | Path di un post `content/<file>.md` |
| Output | `podcast/<slug>.md` (cartella creata se assente) |

## Input / Output

- **Trigger:** "converti questo post in podcast", "script podcast da
  `content/foo.md`", "episodio dal post X".
- **Input:** il path di un post Markdown in `content/`. Se manca, la skill lo
  chiede.
- **Slug:** derivato dal front matter del post, gestendo **entrambi** i formati
  presenti nel blog (blocco YAML `---` e classico `Key: value`); fallback dal
  nome file.
- **Output:** scrive `podcast/<slug>.md`, creando la cartella `podcast/` se
  assente. `podcast/` sta fuori da `content/`, quindi Pelican non lo include
  nella build. Se il file esiste già, la skill chiede conferma prima di
  sovrascrivere.

## Struttura dello script generato

Un header di metadati leggero, poi il parlato con marcatori di servizio:

```
# Podcast — <titolo>
Fonte: content/<slug>.md · Durata stimata: ~N min · Voce: singola

[COLD OPEN] gancio di 2-3 frasi che cattura.
[INTRO] saluto + inquadramento dell'episodio.
[CORPO] adattamento integrale, in ordine, riscritto per il parlato.
[OUTRO] sintesi + invito a leggere il post / iscriversi.
```

I marcatori `[COLD OPEN]` / `[INTRO]` / `[CORPO]` / `[OUTRO]` sono di servizio
(per l'autore o la TTS) e vanno tenuti su righe separate dal testo parlato.

## Regole di stile parlato (il cuore della skill)

- Prima persona, frasi corte, transizioni orali ("ora, la parte interessante
  è…"), niente riferimenti visivi ("come sopra", "nella tabella qui accanto").
- Acronimi espansi alla prima occorrenza ("MCP, il Model Context Protocol").
- Numeri, simboli e percentuali scritti come si pronunciano.
- `[pausa]` opzionale e con parsimonia per gli stacchi. Nessun markdown dentro
  le battute parlate.

## Gestione di codice, tabelle, link, immagini

- **Codice/comandi:** descritti per cosa fanno, **mai** letti nella sintassi
  ("in pratica gli passi il contenuto e la cartella di output" invece di leggere
  `pelican content -o output`). Niente lettura di simboli o flag.
- **Tabelle/dati:** riassunti a parole nel loro senso ("i margini scendono dal
  90% al 60% circa").
- **Immagini/diagrammi:** descritto solo il concetto che illustrano.
- **Link:** "trovi il riferimento nelle note dell'episodio".

## Contenuto del file SKILL.md

Sezioni, sul modello di `write-pelican-post`:

1. **Overview** — cosa fa e per cosa.
2. **When to Use** — frasi trigger.
3. **Workflow** — passi: ricevi il path → deriva lo slug dal front matter →
   genera lo script monologo → scrivi `podcast/<slug>.md` (conferma se esiste).
4. **Regole di stile parlato.**
5. **Gestione codice / tabelle / link / immagini.**
6. **Struttura dello script.**
7. **Checklist di auto-verifica.**
8. **Common Mistakes.**
9. **Esempio completo** — un estratto di post → il relativo estratto di script.

## Fuori scope (YAGNI)

- Generazione audio / TTS (lo script è solo testo; eventualmente si passa a una
  skill come `save-to-spotify` a valle).
- Formato a due voci / dialogo.
- Episodi condensati o riassunti (solo adattamento integrale).
- Conversione batch di più post in un colpo solo.
- Modifica dei post esistenti.
