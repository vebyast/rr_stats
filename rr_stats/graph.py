from typing import Iterable, List
from rr_stats import stats
import os
import subprocess
import shutil
import tempfile
import itertools
import more_itertools
import math
import xdg

_HEADERLINE = "\t".join(
    [
        '"Timestamp"',
        '"Total Views"',
        '"Average Views"',
        '"Favorites"',
        '"Followers"',
        '"Ratings"',
        '"Pages"',
    ]
)

def _format_line(d: stats.Stat):
    values = [
        d.timestamp.timestamp(),
        d.total_views,
        d.average_views,
        d.favorites,
        d.followers,
        d.ratings,
        d.pages,
    ]
    return "\t".join(str(s) for s in values)

def _make_gnuplot_program(data: Iterable[stats.Stat], termsize: os.terminal_size) -> List[str]:
    xmin = math.floor(min(d.timestamp for d in data).timestamp())
    xmax = math.ceil(max(d.timestamp for d in data).timestamp())

    return [
        # Inline data
        "$Data << EOD",
        _HEADERLINE,
        *[_format_line(d) for d in data],
        "EOD",
        # Configure terminal
        f"set terminal dumb ansirgb size {termsize.columns} {(termsize.lines - 8) / 4} enhanced",
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
        # Configure all plots
        'set grid back linecolor "gray10"',
        'set title textcolor "green"',
        'set border back',
        'set style line 1 linecolor "red" pointtype "o"',
        # Make plots
        'set title "Total Views"',
        f'plot $Data using "Timestamp":"Total Views" notitle with points linestyle 1;',
        'set title "Average Views"',
        f'plot $Data using "Timestamp":"Average Views" notitle with points linestyle 1;',
        'set title "Favorites"',
        f'plot $Data using "Timestamp":"Favorites" notitle with points linestyle 1;',
        'set title "Followers"',
        f'plot $Data using "Timestamp":"Followers" notitle with points linestyle 1;',
    ]

def main():
    data = list(stats.read_samples(stats.connect()))
    termsize = shutil.get_terminal_size((80, 20))
    program = _make_gnuplot_program(data, termsize)
    subprocess.run(
        ["gnuplot"],
        input="\n".join(program).encode("utf-8"),
        check=True,
    )

