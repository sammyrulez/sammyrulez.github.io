theme: Letters from Sweden, 4
slidenumbers: true
autoscale: true
footer: blog.r6i.it

# [fit] L'ontologia è sempre stata un Bounded Context

### Ontologie e pipeline agentiche: un problema già risolto vent'anni fa

**Sam Reghenzi** — blog.r6i.it

^ Presentazione veloce: chi sono, cosa faccio, e che questo talk nasce da un articolo sul blog (blog.r6i.it) — chi vuole i riferimenti e i link agli studi citati li trova lì.
^ Anticipare la tesi in una frase, senza svilupparla: il mondo agentic sta riscoprendo le ontologie, e ha ragione a farlo — ma la soluzione che il mercato propone (un'ontologia globale condivisa) è la risposta sbagliata a un problema che il software engineering ha già risolto vent'anni fa. Il titolo è lo spoiler: la risposta si chiama bounded context.
^ Impostare il patto col pubblico: non è un talk contro le ontologie né contro gli agenti. È un talk su dove mettere l'ontologia e chi la governa. Chi viene da DDD si sentirà a casa; chi viene dal mondo knowledge graph troverà un ponte, non un attacco.

---

## Due agenti si incontrano al parco...

"Ho ricevuto un reclamo da un cliente."

"Cos'è un cliente?"

"Chiunque abbia un account."

Un terzo agente: *"No. Cliente = subscription attiva."*

^ Raccontarla come una barzelletta vera, con i tempi comici: due agenti al parco, arriva il terzo. Non spiegare niente durante — la spiegazione è la slide dopo. Lasciare respirare la battuta finale del terzo agente e fare una pausa.
^ Il trucco della scenetta: il primo agente legge dal CRM (cliente = chiunque ha un account), il terzo dal sistema di billing (cliente = subscription attiva). Se qualcuno ride, è perché ha già vissuto questa scena in un progetto vero — probabilmente non tra agenti ma tra microservizi o tra team.
^ Nota di regia: questa è la versione per il palco della scena di apertura dell'articolo. Funziona anche sostituendo "cliente" con il termine ambiguo del dominio del pubblico, se il contesto è un'azienda specifica (es. "ordine", "pratica", "paziente").

---

## Il vero failure mode multi-agente

Non è un'allucinazione: ogni agente risponde correttamente **nel proprio sistema**.

È un **disaccordo semantico mai dichiarato**:
stessa parola, significati diversi.

E nessun layer della pipeline può accorgersene da solo.

^ La morale della scenetta, da dare con calma perché è la fondazione di tutto il talk: nessuno dei tre agenti sbaglia. Il CRM risponde correttamente secondo il CRM, il billing secondo il billing. Non c'è un fatto falso da nessuna parte.
^ Passare in rassegna i layer che NON catturano questo errore, perché è controintuitivo: la schema validation passa (i tipi sono giusti), le eval passano (ogni risposta è localmente corretta e "faithful"), il prompt non aiuta (nessun agente sa che l'altro usa una definizione diversa). È un errore che vive NELL'INTEGRAZIONE, non in un componente — e per questo nessun test di componente lo troverà mai.
^ Dare un nome al fenomeno: disaccordo semantico implicito. "Implicito" è la parola chiave: se fosse dichiarato, sarebbe gestibile. Il problema non è che le definizioni divergono — è che nessuno ha mai scritto da nessuna parte che divergono.
^ Transizione: questo è il buco che il mercato sta correndo a riempire con la parola "ontologia". E — spoiler — su questo il mercato ha ragione. Vediamo i numeri.

---

## Ancorare gli agenti a un'ontologia funziona

I numeri lo confermano:

| Studio | Approccio | Risultato |
| --- | --- | --- |
| OG-RAG — EMNLP 2025 | retrieval su hypergraph ontologico | **+55%** fact recall, **+40%** correttezza |
| Biomedico — 2026 | grounding su ontologia RDF/OWL | allucinazioni **dal 63% all'1,7%** |

Un modello **esplicito e verificabile** del dominio rende l'agente misurabilmente più affidabile.

^ Scopo della slide: prima di criticare l'hype, riconoscere che il fenomeno è reale. Non voglio passare per quello che dice "le ontologie non servono" — dicono il contrario, e i dati lo mostrano.
^ Primo dato — OG-RAG, presentato a EMNLP 2025. L'idea: invece di fare retrieval su un indice vettoriale piatto (il RAG classico: chunk di testo + embedding + similarità), il retrieval viene ancorato a un hypergraph costruito sopra un'ontologia di dominio. Le entità e le relazioni del dominio guidano che cosa viene recuperato e come viene assemblato il contesto. Risultato sullo stesso corpus: +55% di fact recall (il sistema ritrova più fatti pertinenti) e +40% di correttezza delle risposte rispetto al RAG standard. Non è un miglioramento marginale: è la differenza tra un sistema demo e uno usabile.
^ Secondo dato — studio biomedico del 2026, dominio clinico, quindi il caso dove l'errore costa di più. Gli output dell'agente vengono validati contro un'ontologia di dominio formale espressa in RDF/OWL: se l'affermazione non è compatibile con il modello, viene bloccata o rigenerata. Le allucinazioni su query cliniche passano dal 63% (o 48%, a seconda della baseline di confronto) all'1,7%, con accuratezza intorno al 98%. Da "inutilizzabile in produzione" a "affidabile", con lo stesso modello sotto.
^ Il punto da fissare prima di andare avanti: in entrambi i casi la struttura è ESPLICITA (scritta, ispezionabile, verificabile da una macchina) e sta FUORI dal modello. Non è fine-tuning, non è prompt engineering: è un vincolo che l'output deve attraversare.
^ Transizione verso la slide dopo: quindi i vendor hanno ragione? Sul fatto che serva un'ontologia, sì. Ma attenzione: questi studi usano ontologie DI DOMINIO, piccole e scoped — non un modello globale dell'enterprise. La domanda che decide tutto non è architetturale, è organizzativa: ontologia di chi? che copre cosa? mantenuta da chi, quando il dominio cambia? È qui che la risposta dei vendor — "una sola, di tutti, per sempre" — comincia a non reggere. Ed è il resto del talk.

---

## La ricetta dei vendor

Palantir, Stardog, RelationalAI:

**un** modello semantico dell'enterprise,
tutti gli agenti collegati,
un'unica fonte di verità.

^ Descrivere la proposta commerciale in modo onesto, senza caricatura: Palantir con Foundry Ontology (il caso più maturo: un layer di oggetti di business con write-back operativo), Stardog (RDF/SPARQL con reasoning OWL e virtual graph), RelationalAI (semantic model per "decisioni governate"). Prodotti seri, aziende serie.
^ La promessa comune, ridotta all'osso: il disaccordo semantico si risolve centralizzando il significato. UN modello semantico dell'enterprise, tutti gli agenti collegati ad esso, un'unica fonte di verità su cosa significa "cliente", "ordine", "pratica". Se tutti leggono dallo stesso dizionario, nessuno può fraintendere.
^ Enfatizzare la parola "un": tutto il resto del talk attacca quel numero, non la parola "ontologia". Il pubblico deve uscire da questa slide pensando "sembra ragionevole" — perché le slide dopo fanno il lavoro di smontarlo. Non anticipare la critica qui.

---

## Il caso più maturo: Palantir Foundry

L'ontologia come **digital twin dell'organizzazione**:

- **Layer semantico** — oggetti, proprietà e link mappati sui dati reali
- **Layer cinetico** — azioni con *write-back* sui sistemi operativi
- **AIP** — gli agenti leggono *e agiscono* attraverso l'ontologia

Non un catalogo: **il punto di passaggio obbligato di ogni azione.**

^ Approfondire il vendor più serio prima di criticare l'approccio: Palantir Foundry è la versione più matura e più istruttiva della ricetta, perché non è un glossario o un data catalog — è un'ontologia OPERATIVA.
^ Spiegare i tre livelli. Il layer semantico mappa i dataset dell'azienda su oggetti di business tipizzati (Cliente, Ordine, Spedizione), con proprietà e link: gli utenti e gli agenti ragionano su oggetti, non su tabelle. Il layer cinetico è la parte distintiva: l'ontologia definisce anche le AZIONI possibili su quegli oggetti ("approva rimborso", "riassegna spedizione") con write-back verso i sistemi sorgente — l'ontologia non descrive soltanto, ESEGUE. Sopra, AIP (la piattaforma agentic di Palantir): gli agenti LLM leggono il mondo attraverso l'ontologia e agiscono solo attraverso le azioni che l'ontologia dichiara, con permessi e audit incorporati.
^ Riconoscere cosa c'è di giusto, perché è parecchio: azione validata prima del commit, stati illegali bloccati, tracciabilità di ogni operazione. È l'argomento del post "The Guardrail Is Not in the Model" implementato su scala industriale — e infatti dove le domande mappano su dati operativi strutturati (supply chain, fleet, inventory) funziona davvero.
^ Il "ma" che prepara la slide dopo: tutto questo presuppone UN ontologia dell'intera organizzazione, gestita centralmente sulla piattaforma. Ogni definizione contesa ("cliente", "ordine") deve essere risolta una volta per tutti, e ogni evoluzione del modello passa da lì. Vi ricorda qualcosa? Abbiamo già visto un progetto con questa esatta ambizione — e un decennio di budget.

### Semantic Web, 2001–2010

Non è fallito perché la semantica formale non funziona.

È fallito sul **costo umano di governare un modello di *tutto***.

^ Contesto storico per chi non c'era: 2001, Tim Berners-Lee pubblica la visione del Semantic Web su Scientific American. RDF per asserire fatti, OWL per definire semantica e vincoli, linked data per collegare tutto: un web di dati con significato formale, leggibile dalle macchine. Il W3C ci investe un decennio.
^ Il punto tecnico che spesso si perde: la tecnologia FUNZIONAVA e funziona ancora. SHACL valida vincoli in modo economico e affidabile, i triple store sono maturi, il reasoning OWL fa quello che promette — alla scala giusta. Chi liquida il Semantic Web come "tecnologia fallita" sbaglia diagnosi.
^ La vera causa di morte: il costo UMANO e ORGANIZZATIVO. Per funzionare, la visione richiedeva che organizzazioni diverse (o anche solo team diversi della stessa organizzazione) si accordassero su un modello condiviso di tutto — e poi lo mantenessero allineato mentre ogni dominio evolveva per conto suo. L'accordo iniziale era già costosissimo; mantenerlo nel tempo si è rivelato impossibile. Non è un problema di sintassi, è un problema di governance.
^ Il ponte con la slide precedente, da esplicitare a voce: la ricetta dei vendor di oggi È questa visione, con gli stessi ingredienti (spesso letteralmente: RDF e OWL) e un nuovo mercato. Quindi la domanda onesta è: cosa è cambiato dal 2010 che dovrebbe far funzionare oggi ciò che è già fallito una volta?

---

## Cosa è cambiato davvero?

Oggi l'LLM scrive l'ontologia **per pochi centesimi**.

Ma il Semantic Web non è morto di authoring.
È morto di **governance**.

**Costruire ≠ possedere.**

^ Rispondere onestamente alla domanda della slide prima: UNA cosa è cambiata davvero, ed è il costo di scrittura. Nel 2005 servivano knowledge engineer che intervistavano esperti di dominio e codificavano il modello a mano, per settimane. Oggi un LLM legge la tua documentazione, i tuoi schemi, i tuoi ticket, e produce una bozza di ontologia plausibile per pochi centesimi. Questo è progresso reale, non va sminuito.
^ Ma qui sta l'errore di ragionamento del mercato: il Semantic Web non è morto per il costo di AUTHORING. È morto per il costo di GOVERNANCE — cosa succede sei mesi dopo, quando la definizione di "cliente" del team billing e quella del team support cominciano a divergere in produzione, e qualcuno deve accorgersene, decidere chi ha ragione, aggiornare il modello e propagare il cambiamento. Quel costo l'LLM non lo tocca: anzi, generare ontologie a basso costo rende più facile crearne tante da governare.
^ Chiudere con lo slogan della slide, scandito: costruire non è possedere. Il prezzo di un'ontologia non è quello che paghi per scriverla, è quello che paghi per tenerla vera nel tempo. E per un modello globale di tutto, quel prezzo cresce con tutto ciò che il modello copre.
^ Transizione: quindi il problema è "come tenere vero un modello nel tempo senza che il costo esploda". Il software engineering ha già una risposta, e ha vent'anni.

---

## DDD l'aveva già risolto (2003)

**Bounded Context**: un modello deve essere coerente
solo *dentro un confine esplicito*.

- *Billing*: cliente = subscription attiva ✓
- *Support*: cliente = account ✓

**Non dovevano mai condividere la definizione.**

^ Il cuore del talk. Eric Evans, "Domain-Driven Design", 2003. Il problema che il libro affronta è ESATTAMENTE quello della scenetta iniziale: parti diverse di un'organizzazione usano la stessa parola per cose diverse, e i sistemi costruiti su quelle parole si rompono quando si integrano.
^ E la risposta di Evans NON è stata "costruite un modello unico e mettetevi d'accordo". È stata il bounded context: rinunciare esplicitamente al modello globale, e chiedere a ogni modello di essere coerente solo dentro un confine dichiarato. Dentro il confine, ogni termine ha una e una sola definizione, e ogni regola vale senza eccezioni. Fuori dal confine, quella definizione semplicemente non si applica.
^ Riprendere la scenetta e risolverla: nel contesto billing, "cliente = subscription attiva" è giusto, punto. Nel contesto support, "cliente = chiunque ha un account" è giusto, punto. Il bug non era che le definizioni divergono — è FISIOLOGICO che divergano, perché servono a scopi diversi. Il bug era pretendere che fossero la stessa cosa senza averlo mai verificato. I tre agenti al parco non avevano bisogno di mettersi d'accordo: avevano bisogno di sapere di appartenere a contesti diversi.
^ Il collegamento con gli agenti, esplicito: un agente È un bounded context. Ha un compito, un vocabolario, un modello del mondo scoped al suo compito. L'ontologia che gli serve è quella del SUO contesto — piccola, coerente, governabile — non una fetta di un modello enterprise.

---

## Ubiquitous Language

L'ontologia locale **è** il vocabolario del contesto.

Non un artefatto separato,
da sincronizzare con un processo che nessuno ama.

^ Secondo concetto DDD, che risponde alla domanda "ma allora cos'è l'ontologia in questo quadro?". L'ubiquitous language di Evans è il vocabolario condiviso tra sviluppatori ed esperti di dominio DENTRO un contesto: le stesse parole nel parlato, nel codice, nei test, nei nomi delle tabelle. Non un glossario compilato a parte: il linguaggio di lavoro quotidiano.
^ La tesi della slide: quando un'ontologia funziona (come negli studi della slide 4), è perché sta facendo esattamente questo mestiere — è il vocabolario formalizzato di UN contesto, usato dall'agente che in quel contesto opera. Entità, relazioni e vincoli del dominio in cui l'agente lavora, scritti in forma verificabile.
^ Il contrasto da rendere vivido: l'anti-pattern è l'ontologia come artefatto SEPARATO — mantenuta da un altro team, in un altro repository, con un processo di sincronizzazione che nessuno ama e che infatti prima o poi si smette di fare. Chi ha vissuto un "data dictionary aziendale" o un wiki di architettura abbandonato sa già come va a finire. DDD ha speso un libro intero a spiegare perché il modello e il codice devono vivere insieme: vale identico per il modello e l'agente.

---

## E quando i contesti devono parlarsi?

| Pattern DDD | Nel mondo agentic |
| --- | --- |
| Shared Kernel | Ontologia co-posseduta da due agenti |
| Anticorruption Layer | Consumare senza importare assunzioni |
| Partnership | Contesti che evolvono in sincrono |

^ L'obiezione naturale a questo punto del talk: "ok, contesti separati — ma i miei agenti DEVONO parlarsi". Vero. E anche qui DDD ha già la risposta: il context mapping, il catalogo dei modi in cui due bounded context possono relazionarsi, ognuno con i suoi trade-off documentati da vent'anni di pratica.
^ Spiegare le tre righe della tabella con esempi concreti. Shared Kernel: i due agenti co-possiedono una PICCOLA fetta di ontologia condivisa (es. la definizione di "ordine" che serve a entrambi) e ogni modifica richiede l'accordo di entrambi i team — costoso, quindi si tiene minimo. Anticorruption Layer: l'agente A consuma i dati dell'agente B, ma li TRADUCE nel proprio modello a un confine esplicito, senza importare le assunzioni di B — è quello che avrebbe salvato i tre agenti al parco. Partnership: due team decidono di far evolvere i loro contesti in sincrono, con rilasci coordinati.
^ Transizione: e non sono io a dire che questi pattern sono la risposta ai problemi degli agenti — lo sta dicendo, senza saperlo, la letteratura di ricerca. Slide dopo.

---

## Questa riscoperta ha già un nome

La ricerca 2024–2026 la chiama:

*"multi-agent semantic interoperability"*
*"ontology alignment"*

Stessi problemi: chi possiede il pezzo condiviso,
come tradurre al confine, quando co-evolvere.

**È context mapping, riscoperto con un nome nuovo.**

^ Il punto della slide: la letteratura recente su come far dialogare agenti con vocabolari diversi — la trovate sotto le etichette "multi-agent semantic interoperability" e "ontology alignment" — sta affrontando esattamente le tre domande del context mapping. Chi possiede il pezzo di modello condiviso (Shared Kernel). Come consumare il modello altrui senza importarne le assunzioni (Anticorruption Layer). Quando due contesti devono evolvere insieme (Partnership).
^ La battuta dell'articolo, da usare a voce se il pubblico è caldo: è "context mapping con i numeri di serie limati" — come la refurtiva a cui si lima il numero di serie per nasconderne la provenienza. Stessa merce, nomi nuovi, origine non citata.
^ Il tono giusto: NON è un'accusa di plagio, ed è importante dirlo — è la buona notizia del talk. Significa che il corpo di conoscenza per progettare l'interoperabilità tra agenti esiste già, è maturo, ha vent'anni di trade-off documentati e casi reali. Non serve aspettare che la ricerca converga per tentativi: basta aprire il libro giusto.

---

## L'altra metà: gli eventi

**Evento = fatto, non comando**

`OrderPlaced`, non `PlaceOrder`

Ogni consumer interpreta il fatto **nel proprio contesto**.
Nessuno schema globale condiviso in tempo reale.

^ Cambio di capitolo, da segnalare a voce: i bounded context risolvono metà del problema — come tenere coerente un modello locale. L'altra metà è come i contesti restano sincronizzati SENZA ricollassare in uno schema condiviso. Questa metà l'ha risolta l'architettura event-driven.
^ La distinzione centrale, con l'esempio sulla slide: un COMANDO ("PlaceOrder") è un'istruzione — presuppone che il ricevente condivida il tuo modello abbastanza da sapere cosa farne, e ti accoppia a lui. Un FATTO ("OrderPlaced") è un'asserzione: qualcosa è accaduto, punto, espresso nel vocabolario del contesto che lo ha emesso. Chi consuma il fatto lo interpreta nel PROPRIO modello: il billing ci vede una fattura da emettere, il warehouse una spedizione da preparare, l'analytics un data point. Nessuno dei tre deve condividere lo schema degli altri.
^ Tradurre per gli agenti: due agenti che si scambiano fatti nel vocabolario di chi li emette sono accoppiati in modo lasco e possono evolvere separatamente. Due agenti che si chiamano in modo sincrono con un payload che entrambi devono capire identico stanno ricostruendo l'accoppiamento stretto — e ogni evoluzione di uno rompe l'altro. Il tempo è parte del problema: il comando richiede accordo in tempo reale, il fatto no.

---

## E l'audit trail?

L'event log immutabile è **già**
la tracciabilità che l'enterprise ontology
vende come valore differenziale.

⚠️ Intanto MCP + LangGraph/CrewAI ricostruiscono
l'orchestratore centrale sincrono —
**ciò da cui i sistemi distribuiti scappano da vent'anni.**

^ Prima metà — smontare l'argomento commerciale residuo: "ok, ma l'enterprise ontology ci serve per audit e accountability". Risposta: un event log ben progettato è GIÀ un record completo, ordinato e immutabile di ogni fatto che il sistema ha asserito. È event sourcing, ed è esattamente la tracciabilità che Palantir e Stardog vendono come valore differenziale del layer ontologico. Per l'audit trail non serve un modello semantico globale: serve un log che nessuno può mutare.
^ Seconda metà — la nota dolente sullo stack attuale, da dare col tono di chi lo usa (non di chi lo disprezza): MCP è un buon protocollo per quello che fa — un modo standard per un modello di scoprire e chiamare tool. Il problema è il PATTERN che ci si sta costruendo sopra con LangGraph, CrewAI, AutoGen: un orchestratore centrale che chiama ogni agente in modo sincrono, assumendo che entrambi i lati capiscano il payload allo stesso modo.
^ Il paradosso storico, che è il pugno della slide: i sistemi distribuiti hanno passato vent'anni a imparare — pagando caro — a preferire la coreografia (eventi, accoppiamento lasco) all'orchestrazione centrale sincrona. Lo stack agentic sta allegramente ricostruendo la seconda, nel momento esatto in cui aggiunge al sistema i componenti PIÙ non-deterministici mai messi in produzione. Se l'accoppiamento stretto era fragile con i microservizi deterministici, figurarsi ora.

---

## "Ma gli agenti non sono deterministici!"

Vero. Ed è **il motivo per cui serve la struttura.**

Output stocastico + schema esplicito = **comportamento regolarizzato**
*(le allucinazioni da ~50-60% a 1,7% — slide 4)*

Bonus: **introspezione** — un posto dove *guardare*
quando il comportamento va spiegato.

**Non una gabbia. Uno strumento.**

^ Dare voce all'obiezione più forte, in forma onesta: "i microservizi sono deterministici, gli LLM no — quindi imporre uno schema rigido a un processo intrinsecamente stocastico è snaturarlo". È l'obiezione che farebbe chiunque abbia lavorato con gli LLM, e merita una risposta vera, non una scrollata di spalle.
^ Il ribaltamento, che è il momento chiave del talk: è ESATTAMENTE il contrario. Proprio perché l'output è stocastico, dargli una forma esplicita in cui atterrare è ciò che lo rende usabile. E non è un'opinione: sono i numeri della slide 4 — il crollo delle allucinazioni dal 50-60% all'1,7% È l'effetto di vincolare la generazione a uno schema esplicito. La struttura non combatte la natura del modello: la compensa.
^ L'analogia per il pubblico di sviluppatori: il type system. Nessuno dice che i tipi "snaturano" un linguaggio — danno alle parti che devono essere affidabili un posto solido dove stare, e lasciano flessibile il resto. Stessa cosa qui.
^ Il secondo beneficio, che spesso si sottovaluta: l'introspezione. Con un'ontologia locale esplicita, quando l'agente fa qualcosa di strano hai un posto dove GUARDARE — quali entità e relazioni ha usato, quali vincoli ha violato o rispettato — invece di rileggere un transcript e tirare a indovinare. È debugging del processo, non solo validazione dell'output.
^ Aggancio per chi legge il blog: è l'estensione dell'argomento del post "The Guardrail Is Not in the Model" — la struttura che conta vive fuori dal modello. Qui il passo in più: quella struttura non è solo una gabbia che blocca gli stati illegali, è uno strumento che rende leggibili quelli legali.

---

## Chi la mantiene? Il loop, non il curatore

1. L'agente **nota il drift** (azioni rifiutate, eventi che non combaciano)
2. **Propone una patch** — scoped al *suo* contesto, mai globale
3. L'umano **rivede e mergia**

Sparisce solo la pagina bianca.
**Funziona perché la cosa da mantenere è piccola.**

^ L'ultima obiezione in piedi, quella vera: "tutto bello, ma qualcuno deve MANTENERE queste ontologie nel tempo, ed è quello che ha ucciso il Semantic Web". Concederla per intero: sì, è il problema serio. E la risposta di DDD non è mai stata "scrivi il modello una volta e basta" — un contesto maturo fa model refinement continuo, perché l'ubiquitous language evolve col dominio.
^ Cosa cambia oggi: chi scrive la BOZZA del refinement. Camminare sui tre passi della slide. Uno: l'agente stesso è nella posizione migliore per notare il drift — le sue azioni vengono rifiutate dallo schema locale sempre più spesso, o gli eventi di un altro contesto non combaciano più col suo modello. Due: propone una patch specifica e SCOPED al suo bounded context — mai al modello globale, ed è questo vincolo che tiene il loop trattabile. Tre: un umano rivede il diff e decide. L'umano resta il gate di validazione; smette di essere il redattore che parte dalla pagina bianca.
^ Esempio concreto da raccontare: il business introduce i rimborsi parziali. La regola "al massimo un rimborso per ordine" comincia a rifiutare operazioni legittime. L'agente del contesto payments segnala il pattern di rifiuti anomali e propone la modifica al vincolo; il team la rivede e la mergia come qualunque pull request. Confrontare con il mondo Semantic Web, dove serviva che un knowledge engineer si accorgesse del problema, capisse il dominio e riscrivesse il modello a mano.
^ La chiusura del ragionamento, da scandire: questo loop funziona SOLO perché la cosa da mantenere è piccola. Una patch a un'ontologia di contesto è un diff leggibile che una persona può rivedere. Una patch a un modello enterprise globale è una trattativa tra dieci team. Lo scoping non è un dettaglio implementativo: è ciò che rende sostenibile l'intera economia della manutenzione.

---

## Grazie!

Nessuna nuova disciplina.
**Bounded context + eventi come fatti + loop di revisione.**

Articolo completo su **blog.r6i.it**

- 🌐 blog.r6i.it
- 💼 linkedin.com/in/sammyrulez
- 🐙 github.com/sammyrulez

^ Ricapitolare la tesi in tre mosse, indicando la riga in grassetto: non serve inventare una disciplina nuova chiamata "ontology engineering for agentic AI". Serve applicare agli agenti la disciplina che il software distribuito ha già: un bounded context e un'ontologia locale per ogni agente, eventi come fatti per collegare i contesti, e un loop di revisione co-pilotato dall'LLM per tenere i modelli veri nel tempo.
^ La provocazione finale, da lasciare come ultima frase prima dei ringraziamenti: prima di comprare una piattaforma che si vende come "l'enterprise ontology layer per i tuoi agenti", fatti una domanda più brutale — ti manca davvero un nuovo layer epistemico, o ti mancano solo un buon design dei bounded context, un event bus e un processo di revisione che non hai ancora costruito? Nella mia esperienza è quasi sempre la seconda. E costa meno.
^ Chiudere coi riferimenti: l'articolo completo con tutti i link agli studi citati (OG-RAG, lo studio biomedico, i pezzi sul dibattito ontologie vs embedding) è sul blog. Per domande e obiezioni: LinkedIn e GitHub. Aprire al Q&A.