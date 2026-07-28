# Output ElevenLabs v3 per `write-podcast-script` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modificare la skill `write-podcast-script` perché produca file di testo puro pronti per ElevenLabs v3 (`podcast/<slug>-NN.txt`) invece dello script Markdown con marker di sezione.

**Architecture:** La skill è un singolo file di istruzioni in linguaggio naturale (`.claude/skills/write-podcast-script/SKILL.md`). L'implementazione consiste nel riscrivere le sezioni rilevanti del SKILL.md e poi verificare "eseguendo" la skill sul post d'esempio esistente (dogfooding) e controllando l'output contro il self-check aggiornato. Non esistono test automatici: la verifica è manuale contro criteri espliciti.

**Tech Stack:** Markdown (SKILL.md), convenzioni Pelican per lo slug, ElevenLabs v3 (audio tag).

## Global Constraints

- Output in `podcast/<slug>-NN.txt` (testo puro), numerazione a due cifre zero-padded, partendo da `-01`.
- Ogni file < ~3.000 caratteri; niente code sotto ~250 caratteri; taglio solo su confini naturali; mai dentro un audio tag o `<break>`.
- Contenuto dei file: solo testo parlato + audio tag v3 + tag di pausa. Nessun header, nessun Markdown, nessun marker di sezione testuale.
- Audio tag **in inglese**; testo parlato nella lingua del post.
- Palette audio tag chiusa: `[pause]`, `[thoughtful]`, `[curious]`, `[serious]`, `[excited]`, `[laughs]`, `[sighs]`, `[sarcastic]`, `[whispers]`.
- Regole di stile "per l'orecchio" invariate (prima persona, niente riferimenti visivi, acronimi espansi, numeri/simboli scritti come si pronunciano, adattamento completo, non tradurre).
- Non modificare il post sorgente.
- Spec di riferimento: `docs/superpowers/specs/2026-07-28-podcast-script-elevenlabs-output-design.md`.

---

### Task 1: Riscrivere SKILL.md per l'output ElevenLabs v3

**Files:**
- Modify: `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: nulla (primo task).
- Produces: la skill aggiornata che, invocata su un `content/<file>.md`, scrive `podcast/<slug>-NN.txt`. Le sezioni chiave che i task successivi verificano sono: "Workflow" (passo di scrittura output), "Audio tag v3", "Regola di split", "Self-check", "Common Mistakes".

- [ ] **Step 1: Aggiornare Overview e Scope**

Nel blocco `## Overview` sostituire la descrizione dell'output. Il testo deve dire che la skill produce **uno o più file di testo puro pronti per ElevenLabs v3**, salvati in `podcast/<slug>-NN.txt`, contenenti solo testo parlato + audio tag v3. Rimuovere il riferimento a "saved to `podcast/<slug>.md`" e a "text ready to read aloud (or feed to a TTS)" generico, sostituendolo con il target ElevenLabs v3. Mantenere: una voce, adattamento completo, non editare il sorgente.

- [ ] **Step 2: Aggiornare il Workflow (passo 4)**

Sostituire il passo 4 attuale ("Write it to `podcast/<slug>.md`…") con:

```
4. Scrivi l'output come uno o più file `podcast/<slug>-NN.txt` (NN a due cifre,
   da 01), creando la cartella `podcast/` se assente. Applica la regola di split
   descritta sotto. Se esistono già file `podcast/<slug>-*.txt`, chiedi conferma
   prima di rigenerarli/sovrascriverli.
```

- [ ] **Step 3: Sostituire "Script structure" con la struttura ElevenLabs pulita**

Rimuovere completamente il blocco `## Script structure` con i marker `[COLD OPEN]/[INTRO]/[CORPO]/[OUTRO]` e l'header di metadati. Sostituirlo con una sezione `## Struttura dell'output` che specifica:

```
Ogni file contiene SOLO testo parlato + audio tag v3 + tag di pausa. Nessun header,
nessun titolo, nessuna riga "Fonte:", nessun Markdown, nessun marker di sezione
testuale. L'utente incolla il contenuto del file in ElevenLabs senza tagliare nulla.

L'episodio segue comunque l'arco cold open → intro → corpo → outro, ma i confini fra
questi momenti NON sono scritti come marker: sono resi con una pausa più marcata
(`<break time="1.0s"/>`) e, dove serve, un cambio di tono via audio tag.
```

- [ ] **Step 4: Aggiungere la sezione "Audio tag v3"**

Aggiungere una nuova sezione `## Audio tag v3` con:

```
Le parentesi quadre in ElevenLabs v3 sono audio tag. Usali così:

- Pause brevi: usa `[pause]` (mai `[pausa]`).
- Pause fra i momenti dell'episodio: `<break time="1.0s"/>`.
- Espressività: usa i tag con parsimonia, solo quando cambia genuinamente
  l'intenzione di una frase — mai su ogni frase.
- Palette CHIUSA consentita (non inventare altri tag: quelli fuori vocabolario
  vengono ignorati o pronunciati):
  [pause], [thoughtful], [curious], [serious], [excited], [laughs], [sighs],
  [sarcastic], [whispers].
- Gli audio tag sono in INGLESE anche se il parlato è in un'altra lingua: è così
  che ElevenLabs li riconosce. Il testo parlato resta nella lingua del post.
```

- [ ] **Step 5: Aggiungere la sezione "Regola di split"**

Aggiungere `## Regola di split`:

```
- Ogni file resta sotto ~3.000 caratteri.
- Taglia solo su confini naturali: fine frase o fine paragrafo, preferendo i
  confini fra i momenti dell'episodio (cold open → intro → corpo → outro).
- Non tagliare MAI dentro un audio tag o un tag `<break>`.
- Evita code minuscole: se l'ultimo pezzo risulterebbe sotto ~250 caratteri,
  accorpalo al precedente.
- Numera i file `-01`, `-02`, … Se l'episodio sta sotto il limite, produci
  comunque un solo `podcast/<slug>-01.txt`.
```

- [ ] **Step 6: Aggiornare il Self-check**

Sostituire la sezione `## Self-check before writing the file` con i criteri della spec:

```
- Ogni sezione e argomento del post è rappresentato, nell'ordine del post.
- Nessun riferimento visivo e nessun codice/sintassi letto alla lettera.
- Acronimi espansi al primo uso; numeri e simboli scritti come si pronunciano.
- File 100% puliti: nessun header, nessun Markdown, nessun marker di sezione testuale.
- Solo audio tag della palette consentita; pause come `[pause]` / `<break>`.
- Ogni file < ~3.000 caratteri, tagliato su confini naturali, mai dentro un tag,
  niente code sotto ~250 caratteri.
- Output in `podcast/<slug>-NN.txt`; cartella creata; file esistenti confermati.
```

- [ ] **Step 7: Aggiornare la tabella Common Mistakes**

Aggiornare la riga sul percorso e aggiungere le righe sui tag. La tabella deve includere almeno:

| Mistake | Fix |
|---------|-----|
| Reading code/commands verbatim | Explain their meaning only; never the syntax. |
| Leaving "as shown above / in the table" | Rewrite for the ear; no visual references. |
| Markdown o marker di sezione nel file .txt | Solo testo parlato + audio tag v3; niente header/Markdown. |
| Usare `[pausa]` o marker `[CORPO]/[INTRO]` | Pause con `[pause]`/`<break>`; niente marker di sezione. |
| Inventare audio tag fuori palette | Usa solo la palette v3 consentita. |
| Un unico file oltre ~3.000 caratteri | Spezza in `podcast/<slug>-NN.txt` su confini naturali. |
| Writing into content/ | Scripts go to `podcast/<slug>-NN.txt`, outside content/. |

- [ ] **Step 8: Aggiornare l'esempio in fondo alla skill**

Sostituire l'`## Example` finale con un esempio coerente: stesso excerpt sorgente, ma lo script excerpt deve mostrare testo puro con un audio tag usato con parsimonia e senza marker di sezione. Esempio dell'output atteso:

```
[thoughtful] So let's start with where the article is right. Value really is
migrating. And here's the blunt version: if your product is just a thin shell
around a single model call, your margin is a rounding error on somebody else's
infrastructure bill. <break time="1.0s"/>
```

- [ ] **Step 9: Rilettura di coerenza del SKILL.md**

Rileggere l'intero `SKILL.md` e verificare che non siano rimasti riferimenti a `podcast/<slug>.md` (singolo, senza `-NN`), a `[COLD OPEN]/[INTRO]/[CORPO]/[OUTRO]`, a `[pausa]`, o all'header di metadati. La `description` nel front matter può restare (descrive ancora correttamente lo scopo generale); aggiornarla solo se cita il formato di output vecchio.

- [ ] **Step 10: Commit**

```bash
git add .claude/skills/write-podcast-script/SKILL.md
git commit -m "feat: write-podcast-script produce output ElevenLabs v3 (.txt + audio tag)"
```

---

### Task 2: Dogfood — rigenerare l'episodio d'esempio e verificare

**Files:**
- Delete: `podcast/hardware-ate-software-survivors-become-agents.md` (vecchio formato, sostituito)
- Create: `podcast/hardware-ate-software-survivors-become-agents-01.txt`, `-02.txt`, … (secondo lo split)
- Read (sorgente, non modificare): `content/hardware-ate-software-survivors-become-agents.md`

**Interfaces:**
- Consumes: la skill aggiornata dal Task 1.
- Produces: i file `.txt` d'esempio che dimostrano il nuovo formato.

- [ ] **Step 1: Eseguire la skill sul post d'esempio**

Invocare la skill `write-podcast-script` sul post `content/hardware-ate-software-survivors-become-agents.md`, seguendo il SKILL.md aggiornato. Confermare la sostituzione quando la skill chiede (esiste il vecchio `.md`).

- [ ] **Step 2: Verificare l'output contro il self-check**

Controllare manualmente ogni criterio del self-check sui file generati:

Run: `wc -c podcast/hardware-ate-software-survivors-become-agents-*.txt`
Expected: ogni file < 3000 caratteri, nessuno sotto ~250 (salvo file unico).

Run: `grep -nE "\[(COLD OPEN|INTRO|CORPO|OUTRO|pausa)\]|^# |^Fonte:" podcast/hardware-ate-software-survivors-become-agents-*.txt`
Expected: nessun risultato (nessun marker vecchio, header o Markdown).

Run: `grep -noE "\[[a-z ]+\]" podcast/hardware-ate-software-survivors-become-agents-*.txt | sort -u`
Expected: solo tag della palette consentita (`[pause]`, `[thoughtful]`, `[curious]`, `[serious]`, `[excited]`, `[laughs]`, `[sighs]`, `[sarcastic]`, `[whispers]`).

Verificare inoltre a lettura: adattamento completo e ordinato del post, nessun riferimento visivo, acronimi espansi (es. "MCP, il Model Context Protocol"), niente sintassi di codice letta alla lettera, tag usati con parsimonia.

- [ ] **Step 3: Rimuovere il vecchio file .md se ancora presente**

Se la skill non ha già rimosso il vecchio `podcast/hardware-ate-software-survivors-become-agents.md`, eliminarlo (è sostituito dai `.txt`).

Run: `git rm --cached -q podcast/hardware-ate-software-survivors-become-agents.md 2>/dev/null; rm -f podcast/hardware-ate-software-survivors-become-agents.md; ls podcast/`
Expected: nella cartella solo i file `-NN.txt`.

- [ ] **Step 4: Commit**

```bash
git add -A podcast/
git commit -m "test: rigenera episodio d'esempio in formato ElevenLabs v3 (dogfood)"
```

---

## Self-Review

**Spec coverage:**
- Modalità audio tag v3 → Task 1 Step 4. ✓
- Output sostituisce, file 100% puliti → Task 1 Steps 1,3,6; Task 2 Step 3. ✓
- Estensione `.txt`, percorso `-NN` → Task 1 Steps 2,3,5,6. ✓
- Split multi-file sotto ~3.000 char, confini naturali, no code corte → Task 1 Step 5; Task 2 Step 2. ✓
- Palette chiusa, tag in inglese → Task 1 Step 4; Task 2 Step 2. ✓
- Regole di stile invariate → non toccate nel SKILL.md (verifica Step 9); dogfood Step 2. ✓
- Self-check aggiornato / Common Mistakes → Task 1 Steps 6,7. ✓
- Fuori scope (niente audio, niente API, non toccare sorgente) → nessun task li introduce. ✓

**Placeholder scan:** nessun TBD/TODO; ogni step contiene il testo o i comandi concreti.

**Type consistency:** i nomi/percorsi (`podcast/<slug>-NN.txt`, palette tag, `<break time="1.0s"/>`) sono usati identici in spec, Task 1 e Task 2.
