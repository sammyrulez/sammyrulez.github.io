# Immagini per il deck ontology-bounded-context

## Foto e diagrammi esterni

- `cover.jpg` — copertina, background a tutto schermo. Dettaglio centrale della *Scuola di Atene* di Raffaello (1511): Platone indica l'alto (le Idee, il modello universale), Aristotele indica avanti (le sostanze concrete, il particolare) — la tensione fra ontologia globale e contesto locale. Ritaglio 16:9 a 2560x1440 da [File:The School of Athens by Raffaello Sanzio da Urbino in Vatican.jpg](https://commons.wikimedia.org/wiki/File:The_School_of_Athens_by_Raffaello_Sanzio_da_Urbino_in_Vatican.jpg), pubblico dominio.
- Scartata ma valida come alternativa: l'*arbor porphyriana* (III sec., nelle traduzioni di Boezio), la prima ontologia formale della storia — adatta a una slide interna più che alla copertina, perché monocroma e densa di latino. [File su Commons](https://commons.wikimedia.org/wiki/File:Arbor_porphyrii_(probably_from_one_of_Boethius%27_translations).png).
- `park-agents.jpg` — slide della barzelletta, background. Due persone sedute su una panchina di spalle. Unsplash, foto di Stephanie Barbour.

## Diagrammi Excalidraw

Sorgenti editabili + PNG esportati, referenziati con `![inline]` nelle slide:

- `events-as-facts.excalidraw` / `.png` — un fatto, tre interpretazioni (event bus verso Billing / Warehouse / Analytics).
- `ontology-refinement-loop.excalidraw` / `.png` — il loop di model refinement (drift → patch → review umana → merge).
- `semantic-web-layer-cake.excalidraw` / `.png` — lo stack del Semantic Web ridisegnato a mano: URI/Unicode → XML → RDF → RDFS → SPARQL/OWL/RIF → Unifying Logic → Proof → Trust, con la colonna Crypto di lato. Ricalca il [layer cake del W3C](https://www.w3.org/2007/03/layerCake.png) con la didascalia del talk ("non è la sintassi ad aver fallito").

I PNG hanno **sfondo trasparente** e palette per **fondo scuro**: fill desaturati scuri, bordi accesi,
testo chiaro (`#e8e8e8`). Se il tema del deck passa a uno sfondo chiaro vanno rigenerati invertendo la palette.

Per modificarli: aprire il `.excalidraw` su https://excalidraw.com, editare, riesportare il PNG con
"Background" disattivato. Rigenerazione da riga di comando (SVG intermedio, poi PNG con Chrome headless):

```bash
npx -y excalidraw_export nome.excalidraw
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --force-device-scale-factor=2 --default-background-color=00000000 \
  --window-size=<w>,<h> --screenshot=nome.png "file://$PWD/nome.excalidraw.svg"
```

`--default-background-color=00000000` è ciò che rende trasparente il PNG; serve anche
`"viewBackgroundColor": "transparent"` nell'`appState` del file `.excalidraw`.

Nota: l'exporter SVG non gestisce il testo multi-riga dentro i contenitori — usare una riga di testo per elemento.

## Note Deckset

I background con testo sopra vengono automaticamente scuriti/filtrati; `![right]` mette l'immagine nella metà destra con il testo a sinistra.
