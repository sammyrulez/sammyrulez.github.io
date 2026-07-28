# CLAUDE.md

## ⚠️ Motore del blog: Pelican (non Jekyll)

Questo blog (**samreghenzi.it** / sammyrulez.github.io) è generato con **[Pelican](https://getpelican.com)** (Python), **non** Jekyll.

Attenzione: il branch `master` e alcuni worktree contengono ancora la **vecchia versione Jekyll** (template Indigo: `_config.yml`, `_layouts/`, `Gemfile`, `_posts/`). Quei file sono **legacy** e non producono più il sito live. Non lavorarci sopra.

## Struttura (branch `main`)

- `content/` — articoli in Markdown (front matter YAML, plugin `pelican-yaml-metadata`)
- `content/images/` — immagini dei post
- `pelicanconf.py` — config di sviluppo (`THEME = 'theme/chunk'`, `DEFAULT_LANG = 'en'`)
- `publishconf.py` — config di pubblicazione (`SITEURL = https://sammyrulez.github.io`)
- `theme/chunk/` — **tema custom locale** (quello da modificare per il look del sito)
  - `templates/*.html` — template Jinja2
  - `static/css/` — `style.css`, `pygment.css`, `rtl.css` (nessun JS)
- `output/` — sito generato (build locale, non committare)
- `requirements.txt` — dipendenze Python (Pelican 4.11)
- `venv/` — virtualenv locale

## Comandi

```bash
# setup
python -m venv venv && venv/bin/pip install -r requirements.txt

# build (sviluppo)
venv/bin/pelican content -o output -s pelicanconf.py

# server locale con auto-reload
venv/bin/pelican --listen -o output -s pelicanconf.py

# build di pubblicazione
venv/bin/pelican content -o output -s publishconf.py
```

## Deploy

Push su `main` → GitHub Action `Pelican site CI` (`.github/workflows/`): build con `publishconf.py` e deploy della cartella `output/` sul branch `gh-pages` via `peaceiris/actions-gh-pages`.
