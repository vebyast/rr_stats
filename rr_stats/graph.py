from rr_stats import rr_stats
import os
import subprocess
import shutil
import tempfile
import itertools
import more_itertools
import math

data = list(rr_stats.read_db(os.environ["HOME"] + "/src/rr_stats_data/bia.sqlite"))
xmin = math.floor(min(d.timestamp for d in data).timestamp())
xmax = math.ceil(max(d.timestamp for d in data).timestamp())
headerline = "\t".join(
    [
        '"Timestamp"',
        '"Total Views"',
        '"Average Views"',
        '"Favorites"',
        '"Followers"',
        '"Ratings"',
        '"Comments"',
    ]
)

def format_line(d):
    values = [
        d.timestamp.timestamp(),
        d.total_views,
        d.average_views,
        d.favorites,
        d.followers,
        d.ratings,
        d.comments,
    ]
    return "\t".join(str(s) for s in values)

datalines = [format_line(d) for d in data]

termsize = shutil.get_terminal_size((80, 20))

lines = [
    # Inline data
    "$Data << EOD",
    headerline,
    *datalines,
    "EOD",
    # Configure terminal
    f"set terminal dumb ansirgb size {termsize.columns} {termsize.lines / 6} enhanced",
    "set colorsequence classic",
    # Configure X axis
    'set xlabel "Date"',
    "set xdata time",
    'set timefmt "%s"',
    f"set xrange [{xmin}:{xmax}]",
    'set format x "%y/%m/%d %H:%M:%S"',
    "set xtics out",
    # Configure Y axis
    "set ytics out",
    'set lmargin "15"',
    # Plots
    'set title "{/:Bold Total Views}" enhanced',
    f'plot $Data using "Timestamp":"Total Views" notitle with points pt "o";',
    'set title "Average Views"',
    f'plot $Data using "Timestamp":"Average Views" notitle with points pt "o";',
    'set title "Favorites"',
    f'plot $Data using "Timestamp":"Favorites" notitle with points pt "o";',
    'set title "Followers"',
    f'plot $Data using "Timestamp":"Followers" notitle with points pt "o";',
    'set title "Comments"',
    f'plot $Data using "Timestamp":"Comments" notitle with points pt "o";',
]

g = subprocess.run(
    ["gnuplot"],
    input="\n".join(lines).encode("utf-8"),
    check=True,
)
