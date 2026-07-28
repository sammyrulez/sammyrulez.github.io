# Design: output ElevenLabs v3 per la skill `write-podcast-script`

Data: 2026-07-28

## Contesto

La skill `write-podcast-script` converte un post del blog (`content/<file>.md`) in un
monologo parlato a voce singola, oggi salvato in `podcast/<slug>.md` con un header di
metadati e marker di sezione fra parentesi quadre (`[COLD OPEN]`, `[INTRO]`, `[CORPO]`,
`[OUTRO]`) e pause occasionali `[pausa]`.

Problema: quel formato non è adatto a essere mandato a ElevenLabs. Il modello **v3**
interpreta le parentesi quadre come **audio tag** (es. `[excited]`, `[whispers]`), quindi
i marker di sezione verrebbero letti come istruzioni inesistenti; inoltre header e
metadati verrebbero pronunciati ad alta voce.

## Obiettivo

L'output della skill diventa **uno o più file di testo puro, pronti da incollare in
ElevenLabs v3**, con audio tag espressivi al posto dei marker attuali. Il resto del
comportamento della skill (adattamento completo del post, voce singola, regole per
l'orecchio) resta invariato.

## Decisioni prese

1. **Modalità:** con audio tag v3 (non testo TTS "neutro").
2. **Output:** sostituisce l'attuale `.md` con marker (non lo affianca).
3. **Struttura file:** file 100% pulito — nessun header, nessun marker di sezione,
   nessun Markdown. Solo testo parlato + audio tag v3 + tag di pausa.
4. **Estensione:** `.txt`.
5. **Limite caratteri:** la skill spezza l'episodio in più file numerati.

## Specifica dell'output

### Percorso e file

- L'episodio viene spezzato in file numerati: `podcast/<slug>-01.txt`,
  `podcast/<slug>-02.txt`, …, con numerazione a due cifre zero-padded.
- Se l'episodio sta comodamente sotto il limite, si produce comunque `podcast/<slug>-01.txt`
  (numerazione coerente, un solo file).
- La cartella `podcast/` viene creata se assente.
- Se esistono già file `podcast/<slug>-*.txt`, chiedere conferma prima di
  sovrascrivere/rigenerare.

### Contenuto di ogni file

- **Solo** testo parlato + audio tag v3 + tag di pausa. Niente titolo, niente riga
  `Fonte:`, niente `# ...`, niente marker di sezione, niente Markdown. L'utente incolla
  il contenuto del file in ElevenLabs senza dover tagliare nulla.

### Regola di split

- Ogni file resta **sotto ~3.000 caratteri**.
- Il taglio avviene solo su **confini naturali**: fine di frase o di paragrafo,
  preferendo i confini fra le ex sezioni (cold open → intro → corpo → outro).
- **Mai** tagliare all'interno di un audio tag o di un tag `<break>`.
- Evitare code troppo corte: v3 rende male sotto ~250 caratteri; se l'ultimo pezzo
  risulterebbe minuscolo, riequilibrare accorpando col precedente.

## Audio tag v3

Il cambiamento sostanziale rispetto ai marker attuali.

- **Pause brevi:** `[pausa]` → `[pause]` (tag nativo v3).
- **Confini di sezione:** i passaggi cold open → intro → corpo → outro, non essendoci
  più marker testuali, sono resi con una pausa più marcata — un tag `<break time="1.0s"/>`
  (o simile) — per dare respiro, senza scrivere il nome della sezione.
- **Espressività:** uso **parsimonioso** di tag emozionali/di tono coerenti con la voce
  dell'autore. Il tag si usa solo quando cambia genuinamente l'intenzione della frase,
  mai su ogni frase.
- **Palette chiusa e documentata** nella skill (vocabolario ristretto), così l'output
  resta prevedibile: tag fuori vocabolario v3 vengono ignorati o, peggio, pronunciati.
  Palette iniziale proposta: `[pause]`, `[thoughtful]`, `[curious]`, `[serious]`,
  `[excited]`, `[laughs]`, `[sighs]`, `[sarcastic]`, `[whispers]`.
- **Lingua dei tag:** gli audio tag sono **in inglese** anche quando il parlato è in
  un'altra lingua — è così che ElevenLabs li riconosce. Il testo parlato resta nella
  lingua del post.

## Regole di stile (invariate)

Restano tutte le regole "per l'orecchio" già presenti nella skill:

- Prima persona, frasi brevi, transizioni orali.
- Nessun riferimento visivo ("come mostrato sopra", "nella tabella", "vedi figura").
- Acronimi espansi al primo uso.
- Numeri, simboli e percentuali scritti come si pronunciano.
- Nessun Markdown nel testo parlato.
- Stessa lingua del post (non tradurre).
- Codice/comandi spiegati per significato, mai letti alla lettera; tabelle riassunte a
  parole; immagini descritte come concetto; link → "trovi il riferimento nelle note
  dell'episodio".
- Adattamento **completo**: ogni punto del post, nell'ordine del post.

## Self-check aggiornato (sostituisce quello sui 4 marker)

- Ogni sezione e argomento del post è rappresentato, nell'ordine del post.
- Nessun riferimento visivo e nessun codice/sintassi letto alla lettera.
- Acronimi espansi al primo uso; numeri e simboli scritti come si pronunciano.
- File 100% puliti: nessun header, nessun Markdown, nessun marker di sezione testuale.
- Solo audio tag della palette v3 consentita; pause come `[pause]` / `<break>`.
- Ogni file sotto ~3.000 caratteri, tagliato su confini naturali, mai dentro un tag,
  niente code sotto ~250 caratteri.
- Output in `podcast/<slug>-NN.txt`; cartella creata; file esistenti confermati.

## Fuori scope

- Generazione dell'audio vero e proprio (la skill produce solo testo).
- Automazione dell'invio all'API ElevenLabs.
- Modifica del post sorgente.
