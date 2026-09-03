AUTHOR = 'Sam Reghenzi'
SITENAME = 'Sam Reghenzi Homepage'
SITEURL = ""

PATH = "content"

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = 'en'
THEME = 'theme/chunk'

# Hero (homepage) — theme/chunk "Blog Restyle"
HERO_KICKER = 'Data & AI architect'
HERO_TAGLINE = 'Field notes on LLMs, agents, and the architecture that has to hold them.'
FOOTER_TEXT = 'blog.r6i.it — powered by <a href="http://getpelican.com">Pelican</a>'

PLUGINS = ['pelican.plugins.yaml_metadata']
# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Github", "https://github.com/sammyrulez"),
    ("LinkedIn", "https://www.linkedin.com/in/sammyrulez/")
)

# Social widget
SOCIAL = (
   
)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True