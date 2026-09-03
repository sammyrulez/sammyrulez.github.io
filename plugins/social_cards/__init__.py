"""Genera le social preview (og:image) 1200x630 per ogni articolo.

Design dal progetto Claude Design "Blog Restyle": card brandizzate con
pallino rosso, kicker categoria/data, titolo grande e riga di tag; le
varianti "ice blue" e "deep blue" si alternano per data di pubblicazione.
Le PNG finiscono in <output>/images/social/<slug>.png e i template le
referenziano come og:image.
"""

import logging
import os

from pelican import signals
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

W, H = 1200, 630
PAD_X, PAD_Y = 80, 72
ACCENT = "#ff3b21"

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")

VARIANTS = {
    "ice": {
        "bg": "#eaf2fb",
        "fg": "#0a1220",
        "muted": "#46586f",
        "ring": (10, 18, 32, 46),  # rgba(10,18,32,0.18)
    },
    "deep": {
        "bg": "#0a1220",
        "fg": "#ffffff",
        "muted": "#9fb2c8",
        "ring": (159, 178, 200, 89),  # rgba(159,178,200,0.35)
    },
}


def _font(name, size, weight):
    font = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    font.set_variation_by_axes([weight])
    return font


def _tracked(draw, pos, text, font, fill, tracking):
    """Testo con letter-spacing (PIL non lo supporta nativamente)."""
    x, y = pos
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x - tracking


def _wrap(draw, text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        probe = f"{line} {word}".strip()
        if line and draw.textlength(probe, font=font) > max_width:
            lines.append(line)
            line = word
        else:
            line = probe
    if line:
        lines.append(line)
    return lines


def _render_card(article, variant, path):
    v = VARIANTS[variant]
    img = Image.new("RGB", (W, H), v["bg"])

    # Cerchi decorativi in alto a destra (su layer RGBA per l'opacità)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.ellipse((W - 300, -160, W + 160, 300), outline=v["ring"], width=2)
    r, g, b = (255, 59, 33)
    odraw.ellipse((W - 200, -60, W + 60, 200), fill=(r, g, b, 41))  # opacity .16
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    # --- riga brand: pallino, wordmark, dominio
    dot_r = 10
    cy = PAD_Y + 18
    draw.ellipse((PAD_X, cy - dot_r, PAD_X + 2 * dot_r, cy + dot_r), fill=ACCENT)
    brand_font = _font("SpaceGrotesk.ttf", 30, 700)
    bx = PAD_X + 2 * dot_r + 18
    draw.text((bx, cy - 17), "Sam Reghenzi", font=brand_font, fill=v["fg"])
    bx += draw.textlength("Sam Reghenzi", font=brand_font) + 24
    domain_font = _font("JetBrainsMono.ttf", 15, 400)
    _tracked(draw, (bx, cy - 7), "BLOG.R6I.IT", domain_font, v["muted"], 2.4)

    # --- blocco centrale: kicker + titolo
    kicker_font = _font("JetBrainsMono.ttf", 17, 500)
    kicker = f"{article.category} · {article.date.strftime('%d %b %Y')}".upper()
    title = str(article.metadata.get("title") or article.title)
    title_size = 62 if len(title) > 46 else 82
    title_font = _font("SpaceGrotesk.ttf", title_size, 700)
    lines = _wrap(draw, title, title_font, W - 2 * PAD_X - 60)
    line_h = int(title_size * 1.06)

    footer_top = H - PAD_Y - 52
    block_h = 46 + len(lines) * line_h
    ty = PAD_Y + 60 + max(0, (footer_top - (PAD_Y + 60) - block_h) // 2)
    _tracked(draw, (PAD_X, ty), kicker, kicker_font, ACCENT, 3.4)
    ty += 46
    for line in lines:
        draw.text((PAD_X, ty), line, font=title_font, fill=v["fg"])
        ty += line_h

    # --- footer: riga, tag a sinistra, "Read →" a destra
    draw.line((PAD_X, footer_top, W - PAD_X, footer_top), fill=v["ring"], width=2)
    fy = footer_top + 24
    tag_font = _font("JetBrainsMono.ttf", 17, 400)
    tags = [f"#{t}" for t in (article.tags or [])][:4]
    draw.text((PAD_X, fy), "  ".join(str(t) for t in tags), font=tag_font, fill=v["muted"])
    read_font = _font("SpaceGrotesk.ttf", 19, 600)
    read = "Read →"
    draw.text((W - PAD_X - draw.textlength(read, font=read_font), fy - 2),
              read, font=read_font, fill=ACCENT)

    img.save(path, "PNG")


def generate_cards(generators):
    from pelican.generators import ArticlesGenerator

    for gen in generators:
        if not isinstance(gen, ArticlesGenerator):
            continue
        out_dir = os.path.join(gen.output_path, "images", "social")
        os.makedirs(out_dir, exist_ok=True)
        for i, article in enumerate(gen.articles):
            variant = "deep" if i % 2 else "ice"
            path = os.path.join(out_dir, f"{article.slug}.png")
            try:
                _render_card(article, variant, path)
            except Exception:
                logger.exception("social_cards: card non generata per %s", article.slug)
        logger.info("social_cards: generate %d card in %s", len(gen.articles), out_dir)


def register():
    signals.all_generators_finalized.connect(generate_cards)
