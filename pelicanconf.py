AUTHOR = 'Sam Reghenzi'
SITENAME = 'Sam Reghenzi Homepage'
SITEURL = ""

PATH = "content"

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = 'en'
THEME = 'theme/chunk'

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