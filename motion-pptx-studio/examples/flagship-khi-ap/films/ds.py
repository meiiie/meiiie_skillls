"""Design system for the flagship deck: direction A, "Khí áp" (the pressure chart).
Pure python, no deps: imported by the manimgx films, the board script and the deck builder,
so one set of tokens drives every renderer."""

# ---- palette (7 colours, each with one job) ---------------------------------------
PAPER   = '#EEEBE3'   # ground: synoptic-chart paper, warm grey
LAND    = '#E0DCD1'   # land mass on the chart, one step darker than paper
RULE    = '#C9C3B6'   # graticule, hairlines, tick rules
SLATE   = '#5E6873'   # secondary text, isobars at rest, sources
INK     = '#151C26'   # primary text, the 3.1% world isobar, needles
LOW     = '#C0391F'   # vermilion: the energy shock, low pressure, below-zero
HIGH    = '#1F4F8F'   # Prussian blue: the AI demand shock, high pressure, above-zero
VN      = '#B9850F'   # ochre: Vietnam only, used at most once per slide

ISOBAR  = '#6F8299'   # isobars (a desaturated HIGH; not a palette colour of its own)

# ---- type -------------------------------------------------------------------------
SERIF   = 'Source Serif Pro'          # display + headlines (Semibold), italics for asides
SANS    = 'IBM Plex Sans'             # body, notes
COND    = 'IBM Plex Sans Condensed'   # map labels, kickers, chart labels (weather-chart voice)
MONO    = 'IBM Plex Mono'             # numbers on dials, station codes, sources

# The only 7 sizes on any slide (pt on a 13.333 x 7.5 in canvas). Films use the same
# sizes converted to pixels at their on-slide scale, so type matches across film and slide.
SIZES = {
    'micro':   10,   # source lines, axis ticks, dial numerals
    'label':   13,   # map labels, chart labels, kickers
    'body':    17,   # body copy, callout text
    'sub':     23,   # subheads, standfirsts
    'title':   34,   # slide titles
    'display': 58,   # chapter titles, headline numbers
    'hero':   132,   # the one giant number per chapter
}

# ---- grid -------------------------------------------------------------------------
SLIDE_W, SLIDE_H = 13.333, 7.5
MARGIN_X, MARGIN_TOP, MARGIN_BOTTOM = 0.6, 0.5, 0.42
COLS, GUTTER = 12, 0.2
BASELINE = 0.125      # inches; tops of text blocks snap to it

def col_x(i):
    """left edge of column i (0-based)"""
    cw = (SLIDE_W - 2 * MARGIN_X - (COLS - 1) * GUTTER) / COLS
    return MARGIN_X + i * (cw + GUTTER)

def col_w(span):
    cw = (SLIDE_W - 2 * MARGIN_X - (COLS - 1) * GUTTER) / COLS
    return span * cw + (span - 1) * GUTTER

# The film window used by every signature scene: full text width, 64:27 (2560 x 1080)
FILM_X, FILM_W = MARGIN_X, SLIDE_W - 2 * MARGIN_X
FILM_H = FILM_W * 1080 / 2560
FILM_Y = 1.62
FILM_PX = (2560, 1080)
