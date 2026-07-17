# Cross-posting automatico Pelican → Substack

**Data:** 2026-07-17
**Stato:** approvato (design)

## Obiettivo

Pubblicare automaticamente su Substack ogni nuovo articolo del blog Pelican,
senza intervento umano, riusando la pipeline GitHub Actions esistente.

## Vincolo fondamentale

Substack **non offre un'API pubblica ufficiale** per pubblicare. L'automazione
usa la libreria non ufficiale [`python-substack`](https://pypi.org/project/python-substack/),
che si autentica con le credenziali/token di sessione dell'account. Trade-off
accettato: gli endpoint interni possono cambiare senza preavviso e vanno
manutenuti.

## Decisioni di design

| Aspetto | Scelta |
|---|---|
| Trigger | GitHub Actions, al push su `main`, dopo il deploy Pelican |
| Contenuto | Articolo completo + link canonical al post originale |
| Pubblicazione | `published` **senza** invio email agli iscritti |
| Rilevamento nuovi post | Diff del push (`git diff --diff-filter=A ... -- content/*.md`) + guardia idempotente |
| Sorgente del corpo | HTML già renderizzato da Pelican in `output/` (SITEURL assoluto) |

## Architettura

Un nuovo step nel workflow `.github/workflows/pelican.yaml`, eseguito **dopo**
il build Pelican e **dopo** il deploy su GitHub Pages (se il deploy fallisce,
non si pubblica su Substack). Lo step:

1. Calcola i file `.md` **aggiunti** nel push:
   `git diff --name-only --diff-filter=A <before> <after> -- content/*.md`
2. Passa la lista allo script `tools/substack_crosspost.py`.
3. Lo script, per ogni post: legge il front matter, recupera l'HTML renderizzato
   corrispondente in `output/`, e pubblica su Substack come `published` senza
   email, con link canonical.

```
push su main
  └─ build Pelican (output/ con SITEURL assoluto)
  └─ deploy GitHub Pages
  └─ crosspost step (continue-on-error):
       git diff --diff-filter=A → [content/foo.md, ...]
       per ogni file:
         front_matter(foo.md) → {title, summary, slug, tags}
         extract_body(output/foo.html) → body_html
         SubstackClient.exists(title)?  → sì: skip
                                        → no: post(..., canonical=SITEURL/foo.html,
                                                    publish=True, send_email=False)
```

## Componenti

### `tools/substack_crosspost.py` (orchestratore)
Riceve la lista di file `.md` nuovi (argomenti CLI o stdin). Per ciascuno
costruisce il payload e chiama il client Substack. Idempotente: prima di
pubblicare interroga Substack per un post con lo stesso titolo e salta se
esiste già (guardia contro i ri-run del workflow, che compensa la fragilità
del solo diff del push).

### `front_matter(md_path) -> dict` (interna)
Estrae `Title`, `Summary`, `Slug`, `Tags`, `Author` dal front matter YAML del
Markdown (coerente con il plugin `pelican.plugins.yaml_metadata` in uso). Se lo
`Slug` manca, lo deriva dal nome file.

### `extract_body(html_path) -> str` (interna)
Legge `output/<slug>.html` e isola il corpo dell'articolo dal template del tema
(selettore CSS sul contenuto dell'`<article>`), producendo HTML pulito da dare a
Substack. Le immagini e i link sono già assoluti perché `output/` è generato con
`publishconf.py` (`SITEURL = https://sammyrulez.github.io`).

### `SubstackClient` (wrapper sottile su `python-substack`)
- `__init__` — legge credenziali/token da env, esegue login.
- `exists(title) -> bool` — verifica se esiste già un post con quel titolo.
- `post(title, subtitle, body_html, canonical_url, publish=True, send_email=False)`
  — crea e pubblica il post.

Mappatura campi: `Title` → titolo, `Summary` → sottotitolo, corpo HTML → body,
`SITEURL/<slug>.html` → canonical URL.

## Autenticazione e segreti

Lo script legge esclusivamente da variabili d'ambiente; nessun segreto nel repo.
GitHub Secrets previsti (token di sessione preferito perché più stabile in CI):

- `SUBSTACK_TOKEN` — token di sessione, **oppure**
- `SUBSTACK_EMAIL` + `SUBSTACK_PASSWORD`
- `SUBSTACK_PUBLICATION_URL` — URL della publication di destinazione.

Se le variabili mancano (es. fork/PR), lo script esce con **successo silenzioso**
per non rompere il deploy.

## Gestione errori

- Errore su un singolo post → logga e continua con gli altri.
- Exit code ≠ 0 solo a fine ciclo se almeno un post è fallito (visibile nei log
  Actions).
- HTML mancante in `output/` per uno slug → warning e skip.
- Fallimento login Substack → errore chiaro, exit non-zero.
- Lo step del workflow usa `continue-on-error: true` così un problema di
  cross-posting non marca rosso l'intero deploy (già avvenuto).

## Testing

- Unit test su `front_matter` e `extract_body` con fixture (un `.md` e il
  relativo `.html`) — nessuna rete.
- `SubstackClient` isolato dietro interfaccia e mockato nei test
  dell'orchestratore: verifica skip-se-esiste, publish con parametri corretti,
  continua-su-errore.
- Nessun test che colpisca Substack reale in CI.

## Fuori scope (YAGNI)

- Sincronizzazione di modifiche a post già pubblicati (solo articoli nuovi).
- Import bulk dello storico esistente.
- Invio email agli iscritti.
- Cross-posting verso altre piattaforme.
