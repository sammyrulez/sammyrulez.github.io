# Sorgenti Excalidraw dei diagrammi del blog

I `.excalidraw` stanno qui e **non** in `content/images/`, perché `STATIC_PATHS = ['images']`
copierebbe anche i sorgenti dentro `output/` pubblicandoli sul sito. Qui restano versionati
ma fuori dalla build.

I PNG esportati vivono in `content/images/`, con lo stesso nome base:

| Sorgente | PNG | Post |
|---|---|---|
| `baselining-tabular-2026.excalidraw` | `content/images/baselining-tabular-2026.png` | baselining tabular |
| `dirigista-decisions.excalidraw` | `content/images/dirigista-decisions.png` | dirigista |
| `dungeondraft-mcp-architecture.excalidraw` | `content/images/dungeondraft-mcp-architecture.png` | dungeondraft-mcp-bridge-fixes |
| `mlops.excalidraw` | `content/images/mlops.png` | — (non ancora usato) |

## Modificare ed esportare

Aprire il `.excalidraw` su https://excalidraw.com, editare, riesportare il PNG a 2x.

Da riga di comando (SVG intermedio, poi PNG con Chrome headless):

```bash
npx -y excalidraw_export nome.excalidraw
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --force-device-scale-factor=2 --default-background-color=00000000 \
  --window-size=<w>,<h> --screenshot=../content/images/nome.png "file://$PWD/nome.excalidraw.svg"
```

`--default-background-color=00000000` rende il PNG trasparente; serve anche
`"viewBackgroundColor": "transparent"` nell'`appState` del file `.excalidraw`.

Note:
- l'exporter SVG non gestisce il testo multi-riga dentro i contenitori: usare un elemento
  `text` per riga invece dei `label` sui contenitori;
- il tema del blog è solo chiaro (`--paper: #ffffff`), quindi palette Excalidraw standard
  con testo scuro.
