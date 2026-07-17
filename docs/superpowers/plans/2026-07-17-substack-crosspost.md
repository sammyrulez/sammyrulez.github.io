# Substack Cross-posting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pubblicare automaticamente su Substack ogni nuovo articolo del blog Pelican, al push su `main`, senza intervento umano.

**Architecture:** Uno script Python (`tools/substack_crosspost.py` + moduli in `tools/substack/`) viene invocato da un nuovo step del workflow GitHub Actions dopo il deploy. Riceve i file `.md` aggiunti nel push, estrae metadati (front matter) e corpo (HTML già renderizzato in `output/`), converte il corpo in una rappresentazione intermedia (IR) e lo pubblica su Substack via `python-substack` come `published` senza email, con link canonical. La logica è decomposta in unità piccole e testabili; solo il wrapper `SubstackClient` tocca la libreria non ufficiale.

**Tech Stack:** Python 3.12, `python-substack` (API non ufficiale), `beautifulsoup4` (parsing HTML output), `PyYAML` (già presente), `Unidecode` (già presente, per lo slugify), `pytest` (test, dev-only).

## Global Constraints

- Python 3.12 (come nel workflow esistente `.github/workflows/pelican.yaml`).
- Nessun segreto nel repo: credenziali Substack solo da variabili d'ambiente.
- Se le credenziali Substack mancano → **successo silenzioso** (exit 0), per non rompere deploy su fork/PR.
- Pubblicazione: `published` **senza** invio email agli iscritti (`send_email=False`).
- Ogni post include il **link canonical** `https://sammyrulez.github.io/<slug>.html`.
- Idempotenza: prima di pubblicare, saltare se esiste già su Substack un post con lo stesso titolo.
- Lo step del workflow usa `continue-on-error: true`: un errore di cross-posting non deve marcare rosso il deploy già avvenuto.
- Il front matter dei post è in **due formati**: blocco YAML delimitato da `---` **oppure** classico Pelican `Key: value` (righe fino alla prima riga vuota). Entrambi vanno supportati, chiavi case-insensitive.
- Il corpo dell'articolo nell'HTML renderizzato è nel selettore CSS `div.post div.entry-content`.
- Dipendenze pinnate con `==` in `requirements.txt` (coerente con lo stile esistente).

---

## File Structure

- `tools/__init__.py` — package marker.
- `tools/substack/__init__.py` — package marker.
- `tools/substack/front_matter.py` — `front_matter(md_path) -> dict` (title, summary, slug, tags).
- `tools/substack/body.py` — `extract_body(html_path) -> str` (HTML del corpo) + `html_to_ir(body_html) -> list[dict]` (IR a blocchi).
- `tools/substack/client.py` — `SubstackClient` (wrapper su `python-substack`).
- `tools/substack_crosspost.py` — orchestratore CLI (`main(argv)`).
- `tests/tools/substack/test_front_matter.py`
- `tests/tools/substack/test_body.py`
- `tests/tools/substack/test_client.py`
- `tests/tools/test_crosspost.py`
- `tests/tools/fixtures/` — fixture `.md` e `.html`.
- `requirements.txt` — aggiunta `python-substack`, `beautifulsoup4`.
- `requirements-dev.txt` — `pytest` (nuovo).
- `.github/workflows/pelican.yaml` — nuovo step di cross-posting.

**Intermediate Representation (IR)** — lista di blocchi, ognuno un dict. Tipi:
- `{"type": "heading", "level": 2|3, "runs": [Run, ...]}`
- `{"type": "paragraph", "runs": [Run, ...]}`
- `{"type": "code", "text": "..."}`
- `{"type": "blockquote", "runs": [Run, ...]}`
- `{"type": "list", "ordered": bool, "items": [[Run, ...], ...]}`
- `{"type": "image", "src": "https://...", "alt": "..."}`

dove un **Run** è `{"text": "...", "href": "https://..."|None}` (segmento di testo inline, eventualmente link).

---

### Task 1: Scaffolding e dipendenze

**Files:**
- Create: `tools/__init__.py`, `tools/substack/__init__.py`
- Create: `tests/__init__.py`, `tests/tools/__init__.py`, `tests/tools/substack/__init__.py`
- Create: `requirements-dev.txt`
- Modify: `requirements.txt`
- Create: `pytest.ini`

**Interfaces:**
- Consumes: nulla.
- Produces: struttura di package importabile `tools.substack.*`; `pytest` eseguibile dalla root.

- [ ] **Step 1: Creare i package marker (file vuoti)**

Creare cinque file vuoti:
`tools/__init__.py`, `tools/substack/__init__.py`, `tests/__init__.py`, `tests/tools/__init__.py`, `tests/tools/substack/__init__.py`.

- [ ] **Step 2: Aggiungere dipendenze runtime a `requirements.txt`**

Aggiungere in fondo a `requirements.txt`:

```
python-substack==0.1.8
beautifulsoup4==4.12.3
```

- [ ] **Step 3: Creare `requirements-dev.txt`**

```
-r requirements.txt
pytest==8.3.4
```

- [ ] **Step 4: Creare `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 5: Installare e verificare**

Run: `pip install -r requirements-dev.txt && python -c "import substack, bs4; print('ok')"`
Expected: stampa `ok` senza errori.

- [ ] **Step 6: Verificare che pytest parta (nessun test ancora)**

Run: `pytest -q`
Expected: `no tests ran` (exit 5) — è atteso, non è un fallimento del setup.

- [ ] **Step 7: Commit**

```bash
git add tools/ tests/ requirements.txt requirements-dev.txt pytest.ini
git commit -m "chore: scaffolding cross-posting Substack e dipendenze"
```

---

### Task 2: Parser del front matter

**Files:**
- Create: `tools/substack/front_matter.py`
- Test: `tests/tools/substack/test_front_matter.py`
- Create fixtures: `tests/tools/fixtures/post_classic.md`, `tests/tools/fixtures/post_yaml.md`

**Interfaces:**
- Consumes: nulla.
- Produces: `front_matter(md_path: str | pathlib.Path) -> dict` con chiavi esatte:
  - `title: str`
  - `summary: str`
  - `slug: str`
  - `tags: list[str]`

- [ ] **Step 1: Creare le fixture**

`tests/tools/fixtures/post_classic.md`:

```markdown
Title: OAuth's Original Sin
Date: 2026-06-19 22:48
Category: AI
Tags: oauth, mcp, security
Slug: oauth-original-sin
Summary: Perché MCP ha ereditato un problema pensato per gli umani.

Corpo dell'articolo qui.
```

`tests/tools/fixtures/post_yaml.md`:

```markdown
---
title: "MCP vs Skills: when to use which"
date: 2026-05-10 22:48
category: AI
tags: mcp, skills
slug: mcp-vs-skills
summary: Quando usare l'uno o l'altro.
---

Corpo dell'articolo qui.
```

- [ ] **Step 2: Scrivere i test che falliscono**

`tests/tools/substack/test_front_matter.py`:

```python
from pathlib import Path

from tools.substack.front_matter import front_matter

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_classic_format():
    meta = front_matter(FIXTURES / "post_classic.md")
    assert meta["title"] == "OAuth's Original Sin"
    assert meta["summary"] == "Perché MCP ha ereditato un problema pensato per gli umani."
    assert meta["slug"] == "oauth-original-sin"
    assert meta["tags"] == ["oauth", "mcp", "security"]


def test_yaml_format():
    meta = front_matter(FIXTURES / "post_yaml.md")
    assert meta["title"] == "MCP vs Skills: when to use which"
    assert meta["summary"] == "Quando usare l'uno o l'altro."
    assert meta["slug"] == "mcp-vs-skills"
    assert meta["tags"] == ["mcp", "skills"]


def test_slug_derived_from_title_when_missing(tmp_path):
    p = tmp_path / "no_slug.md"
    p.write_text("Title: Ciao Mondo! Àccenti\nDate: 2026-01-01\n\nCorpo.", encoding="utf-8")
    meta = front_matter(p)
    assert meta["slug"] == "ciao-mondo-accenti"
```

- [ ] **Step 3: Eseguire i test per verificarne il fallimento**

Run: `pytest tests/tools/substack/test_front_matter.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tools.substack.front_matter'`

- [ ] **Step 4: Implementare `front_matter.py`**

```python
import re
from pathlib import Path

import yaml
from unidecode import unidecode


def _slugify(title: str) -> str:
    s = unidecode(title).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def _normalize_tags(raw) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, str):
        return [t.strip() for t in raw.split(",") if t.strip()]
    return [str(t).strip() for t in raw if str(t).strip()]


def front_matter(md_path) -> dict:
    text = Path(md_path).read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        _, block, _ = text.lstrip().split("---", 2)
        data = yaml.safe_load(block) or {}
        meta = {str(k).lower(): v for k, v in data.items()}
    else:
        meta = {}
        for line in text.splitlines():
            if not line.strip():
                break
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip()

    title = str(meta.get("title", "")).strip().strip('"')
    summary = str(meta.get("summary", "")).strip()
    slug = str(meta.get("slug", "")).strip() or _slugify(title)
    tags = _normalize_tags(meta.get("tags"))
    return {"title": title, "summary": summary, "slug": slug, "tags": tags}
```

- [ ] **Step 5: Eseguire i test per verificarne il successo**

Run: `pytest tests/tools/substack/test_front_matter.py -v`
Expected: 3 PASSED

- [ ] **Step 6: Commit**

```bash
git add tools/substack/front_matter.py tests/tools/substack/test_front_matter.py tests/tools/fixtures/
git commit -m "feat: parser front matter (formato YAML e classico Pelican)"
```

---

### Task 3: Estrazione e conversione del corpo

**Files:**
- Create: `tools/substack/body.py`
- Test: `tests/tools/substack/test_body.py`
- Create fixture: `tests/tools/fixtures/rendered.html`

**Interfaces:**
- Consumes: nulla.
- Produces:
  - `extract_body(html_path: str | pathlib.Path) -> str` — restituisce l'HTML interno di `div.post div.entry-content`. Solleva `ValueError` se il selettore non trova nulla.
  - `html_to_ir(body_html: str) -> list[dict]` — converte l'HTML del corpo nella IR a blocchi descritta sopra.

- [ ] **Step 1: Creare la fixture HTML**

`tests/tools/fixtures/rendered.html` (riproduce la struttura del tema `chunk`):

```html
<!DOCTYPE html>
<html><body>
<div class="post" id="post">
  <div class="main">
    <div class="entry-content">
      <h2>Titolo Sezione</h2>
      <p>Testo con un <a href="https://example.com/x">link</a> dentro.</p>
      <pre><code>print("ciao")</code></pre>
      <ul><li>uno</li><li>due</li></ul>
      <blockquote><p>Citazione.</p></blockquote>
      <p><img src="https://sammyrulez.github.io/images/foo.png" alt="Foo"></p>
    </div>
  </div>
</div>
</body></html>
```

- [ ] **Step 2: Scrivere i test che falliscono**

`tests/tools/substack/test_body.py`:

```python
from pathlib import Path

import pytest

from tools.substack.body import extract_body, html_to_ir

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_extract_body_returns_inner_html():
    body = extract_body(FIXTURES / "rendered.html")
    assert "Titolo Sezione" in body
    assert "entry-content" not in body  # solo il contenuto interno
    assert 'href="https://example.com/x"' in body


def test_extract_body_missing_selector(tmp_path):
    p = tmp_path / "empty.html"
    p.write_text("<html><body><p>nulla</p></body></html>", encoding="utf-8")
    with pytest.raises(ValueError):
        extract_body(p)


def test_html_to_ir_blocks():
    body = extract_body(FIXTURES / "rendered.html")
    ir = html_to_ir(body)
    types = [b["type"] for b in ir]
    assert types == ["heading", "paragraph", "code", "list", "blockquote", "image"]


def test_html_to_ir_heading_level_and_text():
    ir = html_to_ir("<h3>Sub</h3>")
    assert ir[0] == {"type": "heading", "level": 3, "runs": [{"text": "Sub", "href": None}]}


def test_html_to_ir_paragraph_link_runs():
    ir = html_to_ir('<p>pre <a href="https://e.com">mid</a> post</p>')
    assert ir[0]["type"] == "paragraph"
    assert ir[0]["runs"] == [
        {"text": "pre ", "href": None},
        {"text": "mid", "href": "https://e.com"},
        {"text": " post", "href": None},
    ]


def test_html_to_ir_code_text():
    ir = html_to_ir('<pre><code>print("ciao")</code></pre>')
    assert ir[0] == {"type": "code", "text": 'print("ciao")'}


def test_html_to_ir_list():
    ir = html_to_ir("<ul><li>uno</li><li>due</li></ul>")
    assert ir[0]["type"] == "list"
    assert ir[0]["ordered"] is False
    assert ir[0]["items"] == [
        [{"text": "uno", "href": None}],
        [{"text": "due", "href": None}],
    ]


def test_html_to_ir_image():
    ir = html_to_ir('<p><img src="https://e.com/a.png" alt="A"></p>')
    assert ir[0] == {"type": "image", "src": "https://e.com/a.png", "alt": "A"}
```

- [ ] **Step 3: Eseguire i test per verificarne il fallimento**

Run: `pytest tests/tools/substack/test_body.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tools.substack.body'`

- [ ] **Step 4: Implementare `body.py`**

```python
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


def extract_body(html_path) -> str:
    html = Path(html_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    node = soup.select_one("div.post div.entry-content")
    if node is None:
        raise ValueError(f"selettore 'div.post div.entry-content' non trovato in {html_path}")
    return node.decode_contents().strip()


def _runs_from(node) -> list[dict]:
    """Estrae segmenti di testo inline (con eventuale href) da un elemento."""
    runs: list[dict] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if text:
                runs.append({"text": text, "href": None})
        elif isinstance(child, Tag):
            if child.name == "a":
                runs.append({"text": child.get_text(), "href": child.get("href")})
            elif child.name == "img":
                continue  # gestita come blocco a parte
            else:
                runs.extend(_runs_from(child))
    # unisce run adiacenti senza link e scarta i vuoti
    merged: list[dict] = []
    for run in runs:
        if not run["text"]:
            continue
        if merged and merged[-1]["href"] is None and run["href"] is None:
            merged[-1]["text"] += run["text"]
        else:
            merged.append(run)
    return merged


def _image_block(tag: Tag) -> dict:
    return {"type": "image", "src": tag.get("src", ""), "alt": tag.get("alt", "")}


def html_to_ir(body_html: str) -> list[dict]:
    soup = BeautifulSoup(body_html, "html.parser")
    blocks: list[dict] = []
    for el in soup.children:
        if not isinstance(el, Tag):
            continue
        name = el.name
        if name in ("h2", "h3"):
            blocks.append({"type": "heading", "level": int(name[1]), "runs": _runs_from(el)})
        elif name == "pre":
            blocks.append({"type": "code", "text": el.get_text().strip("\n")})
        elif name in ("ul", "ol"):
            items = [_runs_from(li) for li in el.find_all("li", recursive=False)]
            blocks.append({"type": "list", "ordered": name == "ol", "items": items})
        elif name == "blockquote":
            blocks.append({"type": "blockquote", "runs": _runs_from(el)})
        elif name == "p":
            img = el.find("img")
            if img is not None and not el.get_text(strip=True):
                blocks.append(_image_block(img))
            else:
                runs = _runs_from(el)
                if runs:
                    blocks.append({"type": "paragraph", "runs": runs})
        elif name == "img":
            blocks.append(_image_block(el))
    return blocks
```

- [ ] **Step 5: Eseguire i test per verificarne il successo**

Run: `pytest tests/tools/substack/test_body.py -v`
Expected: 8 PASSED

- [ ] **Step 6: Commit**

```bash
git add tools/substack/body.py tests/tools/substack/test_body.py tests/tools/fixtures/rendered.html
git commit -m "feat: estrazione corpo articolo e conversione in IR a blocchi"
```

---

### Task 4: Wrapper `SubstackClient`

**Files:**
- Create: `tools/substack/client.py`
- Test: `tests/tools/substack/test_client.py`

**Interfaces:**
- Consumes: la IR prodotta da `html_to_ir` (Task 3).
- Produces:
  - `SubstackClient.from_env() -> SubstackClient | None` — costruisce il client da variabili d'ambiente; ritorna `None` se le credenziali mancano.
  - `SubstackClient.exists(title: str) -> bool`
  - `SubstackClient.publish(title: str, subtitle: str, ir: list[dict], canonical_url: str) -> None` — pubblica `published` senza email.

Note: questo è l'**unico** modulo che tocca `python-substack`. La costruzione della Post dalla IR vive qui in `_build_post`. Se l'API della libreria cambia, si corregge solo questo file.

- [ ] **Step 1: Scrivere i test che falliscono (con `substack.Api` mockato)**

`tests/tools/substack/test_client.py`:

```python
from unittest.mock import MagicMock, patch

import pytest

from tools.substack.client import SubstackClient


def test_from_env_returns_none_without_credentials(monkeypatch):
    for var in ("SUBSTACK_TOKEN", "SUBSTACK_EMAIL", "SUBSTACK_PASSWORD", "SUBSTACK_PUBLICATION_URL"):
        monkeypatch.delenv(var, raising=False)
    assert SubstackClient.from_env() is None


@patch("tools.substack.client.Api")
def test_from_env_builds_client_with_email_password(mock_api, monkeypatch):
    monkeypatch.setenv("SUBSTACK_EMAIL", "me@example.com")
    monkeypatch.setenv("SUBSTACK_PASSWORD", "secret")
    monkeypatch.setenv("SUBSTACK_PUBLICATION_URL", "https://x.substack.com")
    client = SubstackClient.from_env()
    assert client is not None
    mock_api.assert_called_once()


def test_exists_true_when_title_present():
    api = MagicMock()
    api.get_published_posts.return_value = [{"title": "Ciao"}, {"title": "Altro"}]
    client = SubstackClient(api=api, publication_url="https://x.substack.com")
    assert client.exists("Ciao") is True


def test_exists_false_when_title_absent():
    api = MagicMock()
    api.get_published_posts.return_value = [{"title": "Altro"}]
    client = SubstackClient(api=api, publication_url="https://x.substack.com")
    assert client.exists("Ciao") is False


@patch("tools.substack.client.Post")
def test_publish_calls_library_without_email(mock_post_cls):
    api = MagicMock()
    api.get_user_id.return_value = 42
    api.post_draft.return_value = {"id": 999}
    client = SubstackClient(api=api, publication_url="https://x.substack.com")

    ir = [{"type": "paragraph", "runs": [{"text": "ciao", "href": None}]}]
    client.publish("Titolo", "Sottotitolo", ir, "https://blog/x.html")

    api.post_draft.assert_called_once()
    api.publish_draft.assert_called_once()
    # send_email deve essere False
    _, kwargs = api.publish_draft.call_args
    assert kwargs.get("send_email") is False
```

- [ ] **Step 2: Eseguire i test per verificarne il fallimento**

Run: `pytest tests/tools/substack/test_client.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tools.substack.client'`

- [ ] **Step 3: Implementare `client.py`**

```python
import os

from substack import Api
from substack.post import Post


class SubstackClient:
    def __init__(self, api, publication_url: str):
        self._api = api
        self._publication_url = publication_url

    @classmethod
    def from_env(cls):
        publication_url = os.environ.get("SUBSTACK_PUBLICATION_URL")
        token = os.environ.get("SUBSTACK_TOKEN")
        email = os.environ.get("SUBSTACK_EMAIL")
        password = os.environ.get("SUBSTACK_PASSWORD")
        if not publication_url or not (token or (email and password)):
            return None
        if token:
            api = Api(token=token, publication_url=publication_url)
        else:
            api = Api(email=email, password=password, publication_url=publication_url)
        return cls(api=api, publication_url=publication_url)

    def exists(self, title: str) -> bool:
        posts = self._api.get_published_posts()
        return any(p.get("title") == title for p in posts)

    def _build_post(self, title: str, subtitle: str, ir: list[dict]) -> Post:
        post = Post(title=title, subtitle=subtitle, user_id=self._api.get_user_id())
        for block in ir:
            btype = block["type"]
            if btype == "heading":
                post.heading(_runs_text(block["runs"]), block["level"])
            elif btype == "paragraph":
                para = post.paragraph()
                _apply_runs(para, block["runs"])
            elif btype == "code":
                post.code(block["text"])
            elif btype == "blockquote":
                post.captioned_image  # noqa: no-op placeholder guard (vedi nota)
                post.paragraph(_runs_text(block["runs"]))
            elif btype == "list":
                if block["ordered"]:
                    post.ordered_list([_runs_text(i) for i in block["items"]])
                else:
                    post.bulleted_list([_runs_text(i) for i in block["items"]])
            elif btype == "image":
                post.captioned_image(src=block["src"], alt=block.get("alt", ""))
        return post

    def publish(self, title: str, subtitle: str, ir: list[dict], canonical_url: str) -> None:
        post = self._build_post(title, subtitle, ir)
        draft_payload = post.get_draft()
        draft_payload["canonical_url"] = canonical_url
        draft = self._api.post_draft(draft_payload)
        self._api.prepublish_draft(draft["id"])
        self._api.publish_draft(draft["id"], send_email=False)


def _runs_text(runs: list[dict]) -> str:
    return "".join(r["text"] for r in runs)


def _apply_runs(paragraph, runs: list[dict]) -> None:
    for run in runs:
        if run["href"]:
            paragraph.text(run["text"]).marks([{"type": "link", "href": run["href"]}])
        else:
            paragraph.text(run["text"])
```

> **Nota implementativa (fragilità nota):** l'API di `python-substack` (`Api`, `Post`) è quella su cui poggia tutto e può differire dalla versione installata. Al momento dell'implementazione, verificare i metodi reali di `Post` (`paragraph`, `heading`, `code`, `bulleted_list`, `ordered_list`, `captioned_image`, `text`, `marks`, `get_draft`) e di `Api` (`get_user_id`, `get_published_posts`, `post_draft`, `prepublish_draft`, `publish_draft`) con `python -c "import substack; help(substack.post.Post)"`. Adattare `_build_post`/`publish` alla firma effettiva **mantenendo invariata l'interfaccia pubblica** (`from_env`, `exists`, `publish`) su cui si basano i test e l'orchestratore. Rimuovere il placeholder `post.captioned_image  # no-op` nel ramo blockquote: renderizzare la citazione come paragrafo è accettabile per la v1.

- [ ] **Step 4: Eseguire i test per verificarne il successo**

Run: `pytest tests/tools/substack/test_client.py -v`
Expected: 5 PASSED
(Se un test fallisce per differenze nell'API della libreria, adattare `_build_post`/`publish` come da nota, mantenendo verdi le asserzioni sull'interfaccia pubblica.)

- [ ] **Step 5: Commit**

```bash
git add tools/substack/client.py tests/tools/substack/test_client.py
git commit -m "feat: wrapper SubstackClient (from_env, exists, publish senza email)"
```

---

### Task 5: Orchestratore CLI

**Files:**
- Create: `tools/substack_crosspost.py`
- Test: `tests/tools/test_crosspost.py`

**Interfaces:**
- Consumes: `front_matter` (Task 2), `extract_body`/`html_to_ir` (Task 3), `SubstackClient` (Task 4).
- Produces: `main(argv: list[str], client=None, output_dir="output") -> int` — ritorna exit code (0 = ok/silent-success, 1 = almeno un post fallito). Il parametro `client` permette l'iniezione nei test; se `None`, usa `SubstackClient.from_env()`.

Comportamento per ogni file `.md` argomento:
1. `meta = front_matter(md)`
2. `html_path = output_dir/<slug>.html`; se manca → warning e skip.
3. Se `client.exists(meta["title"])` → skip (idempotenza).
4. Altrimenti `client.publish(title, summary, html_to_ir(extract_body(html_path)), canonical)` dove `canonical = https://sammyrulez.github.io/<slug>.html`.
5. Eccezione su un file → log e `continue`, segnando `failed = True`.

Se `client` è `None` (credenziali assenti) → log "nessuna credenziale, skip" e `return 0`.

- [ ] **Step 1: Scrivere i test che falliscono**

`tests/tools/test_crosspost.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock

from tools.substack_crosspost import main

FIXTURES = Path(__file__).parent / "fixtures"


def _make_post(tmp_path, slug="foo", title="Titolo Foo"):
    content = tmp_path / "content"
    output = tmp_path / "output"
    content.mkdir()
    output.mkdir()
    md = content / f"{slug}.md"
    md.write_text(f"Title: {title}\nSlug: {slug}\nSummary: Riassunto.\n\nCorpo.", encoding="utf-8")
    (output / f"{slug}.html").write_text(
        '<div class="post"><div class="entry-content"><p>Ciao</p></div></div>',
        encoding="utf-8",
    )
    return md, output


def test_silent_success_without_client(tmp_path, capsys):
    md, output = _make_post(tmp_path)
    rc = main([str(md)], client=None, output_dir=str(output))
    assert rc == 0


def test_publishes_new_post(tmp_path):
    md, output = _make_post(tmp_path, title="Nuovo")
    client = MagicMock()
    client.exists.return_value = False
    rc = main([str(md)], client=client, output_dir=str(output))
    assert rc == 0
    client.publish.assert_called_once()
    args, kwargs = client.publish.call_args
    assert args[0] == "Nuovo"  # title
    assert args[3] == "https://sammyrulez.github.io/foo.html"  # canonical


def test_skips_existing_post(tmp_path):
    md, output = _make_post(tmp_path)
    client = MagicMock()
    client.exists.return_value = True
    rc = main([str(md)], client=client, output_dir=str(output))
    assert rc == 0
    client.publish.assert_not_called()


def test_skips_when_html_missing(tmp_path):
    md, output = _make_post(tmp_path)
    (output / "foo.html").unlink()
    client = MagicMock()
    client.exists.return_value = False
    rc = main([str(md)], client=client, output_dir=str(output))
    assert rc == 0
    client.publish.assert_not_called()


def test_returns_1_on_publish_error(tmp_path):
    md, output = _make_post(tmp_path)
    client = MagicMock()
    client.exists.return_value = False
    client.publish.side_effect = RuntimeError("boom")
    rc = main([str(md)], client=client, output_dir=str(output))
    assert rc == 1
```

- [ ] **Step 2: Eseguire i test per verificarne il fallimento**

Run: `pytest tests/tools/test_crosspost.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tools.substack_crosspost'`

- [ ] **Step 3: Implementare `tools/substack_crosspost.py`**

```python
import sys
from pathlib import Path

from tools.substack.body import extract_body, html_to_ir
from tools.substack.client import SubstackClient
from tools.substack.front_matter import front_matter

SITEURL = "https://sammyrulez.github.io"


def main(argv: list[str], client=None, output_dir: str = "output") -> int:
    if client is None:
        client = SubstackClient.from_env()
    if client is None:
        print("[substack] nessuna credenziale configurata: skip cross-posting.")
        return 0

    failed = False
    for md in argv:
        try:
            meta = front_matter(md)
            slug = meta["slug"]
            html_path = Path(output_dir) / f"{slug}.html"
            if not html_path.exists():
                print(f"[substack] HTML mancante per '{slug}' ({html_path}): skip.")
                continue
            if client.exists(meta["title"]):
                print(f"[substack] gia' presente '{meta['title']}': skip.")
                continue
            ir = html_to_ir(extract_body(html_path))
            canonical = f"{SITEURL}/{slug}.html"
            client.publish(meta["title"], meta["summary"], ir, canonical)
            print(f"[substack] pubblicato '{meta['title']}'.")
        except Exception as exc:  # noqa: BLE001 - continua sugli altri post
            failed = True
            print(f"[substack] errore su '{md}': {exc}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 4: Eseguire i test per verificarne il successo**

Run: `pytest tests/tools/test_crosspost.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Eseguire l'intera suite**

Run: `pytest -q`
Expected: tutti PASSED (front_matter 3 + body 8 + client 5 + crosspost 5 = 21).

- [ ] **Step 6: Commit**

```bash
git add tools/substack_crosspost.py tests/tools/test_crosspost.py
git commit -m "feat: orchestratore cross-posting (idempotenza, skip, continue-on-error)"
```

---

### Task 6: Integrazione nel workflow GitHub Actions

**Files:**
- Modify: `.github/workflows/pelican.yaml`

**Interfaces:**
- Consumes: `tools/substack_crosspost.py` (Task 5); i GitHub Secrets `SUBSTACK_TOKEN` (o `SUBSTACK_EMAIL`+`SUBSTACK_PASSWORD`) e `SUBSTACK_PUBLICATION_URL`.
- Produces: pubblicazione automatica al push su `main`.

Requisiti sul checkout: serve `fetch-depth: 0` per poter calcolare il diff tra `github.event.before` e `github.event.after`.

- [ ] **Step 1: Modificare il checkout per avere la storia git**

In `.github/workflows/pelican.yaml`, sostituire:

```yaml
    - uses: actions/checkout@v4
```

con:

```yaml
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
```

- [ ] **Step 2: Aggiungere lo step di cross-posting dopo il Deploy**

Aggiungere in fondo alla lista `steps:` (dopo lo step `Deploy`):

```yaml
    - name: Cross-post to Substack
      continue-on-error: true
      env:
        SUBSTACK_PUBLICATION_URL: ${{ secrets.SUBSTACK_PUBLICATION_URL }}
        SUBSTACK_TOKEN: ${{ secrets.SUBSTACK_TOKEN }}
        SUBSTACK_EMAIL: ${{ secrets.SUBSTACK_EMAIL }}
        SUBSTACK_PASSWORD: ${{ secrets.SUBSTACK_PASSWORD }}
      run: |
        NEW_POSTS=$(git diff --name-only --diff-filter=A ${{ github.event.before }} ${{ github.event.after }} -- 'content/*.md')
        if [ -z "$NEW_POSTS" ]; then
          echo "Nessun nuovo articolo da pubblicare."
          exit 0
        fi
        echo "Nuovi articoli:"; echo "$NEW_POSTS"
        python -m tools.substack_crosspost $NEW_POSTS
```

> Nota: `output/` esiste ancora nel runner perché generato dallo step di build precedente; lo script lo legge da lì (default `output_dir="output"`).

- [ ] **Step 3: Validare la sintassi YAML del workflow**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/pelican.yaml')); print('yaml ok')"`
Expected: stampa `yaml ok`

- [ ] **Step 4: Verifica a secco del comando diff in locale**

Run: `git diff --name-only --diff-filter=A HEAD~1 HEAD -- 'content/*.md' || echo "(nessun nuovo .md nell'ultimo commit, atteso)"`
Expected: elenco di file `.md` aggiunti nell'ultimo commit, oppure vuoto — conferma che la sintassi del comando è valida.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/pelican.yaml
git commit -m "ci: step di cross-posting su Substack al push"
```

- [ ] **Step 6: Configurare i GitHub Secrets (azione manuale dell'utente)**

Documentare per l'utente (non è codice): impostare su GitHub → Settings → Secrets and variables → Actions:
- `SUBSTACK_PUBLICATION_URL` (es. `https://tuonome.substack.com`)
- `SUBSTACK_TOKEN` **oppure** `SUBSTACK_EMAIL` + `SUBSTACK_PASSWORD`

Senza questi secret, lo step gira ma esce in successo silenzioso (nessuna pubblicazione).

---

## Self-Review

**1. Spec coverage:**
- Trigger GitHub Actions al push, dopo il deploy → Task 6. ✓
- Contenuto: articolo completo + canonical → Task 3 (corpo) + Task 5 (canonical). ✓
- Published senza email → Task 4 (`publish_draft(send_email=False)`), asserito nei test. ✓
- Rilevamento nuovi post via diff del push → Task 6 (`git diff --diff-filter=A`). ✓
- Guardia idempotente (skip se titolo esiste) → Task 4 (`exists`) + Task 5. ✓
- Sorgente corpo = HTML renderizzato in `output/` → Task 3 + Task 5. ✓
- Segreti solo da env, silent-success se assenti → Task 4 (`from_env` → None) + Task 5. ✓
- `continue-on-error` sul workflow → Task 6. ✓
- HTML mancante → warning e skip → Task 5, test `test_skips_when_html_missing`. ✓
- Front matter doppio formato → Task 2, test dedicati. ✓
- Testing senza rete reale → tutti i test mockano il client/Api. ✓

**2. Placeholder scan:** nessun "TBD/TODO". L'unico `# no-op placeholder guard` nel ramo blockquote di Task 4 è esplicitamente segnalato e ne è indicata la rimozione nella nota implementativa. Ogni step di codice mostra il codice reale.

**3. Type consistency:** interfaccia IR (`heading/paragraph/code/blockquote/list/image`, Run `{text, href}`) coerente tra Task 3 (produzione), Task 4 (consumo in `_build_post`) e Task 5. Firme `front_matter -> dict{title,summary,slug,tags}`, `extract_body -> str`, `html_to_ir -> list[dict]`, `SubstackClient.from_env/exists/publish`, `main(argv, client, output_dir) -> int` coerenti tra definizione e uso.

## Fuori scope (come da spec)

Sync di modifiche a post esistenti, import bulk storico, invio email, altre piattaforme.
