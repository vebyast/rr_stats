import pkg_resources
import datetime
from typing import Iterable, List
import colorama
from rr_stats import stats
from rr_stats import figletize
import os
import subprocess
import shutil
import tempfile
import itertools
import more_itertools
import math

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


def _make_gnuplot_program(
    data: Iterable[stats.Stat], termsize: os.terminal_size
) -> List[str]:
    xmin = math.floor(min(d.timestamp for d in data).timestamp())
    xmax = math.ceil(max(d.timestamp for d in data).timestamp())

    return [
        # Inline data
        "$Data << EOD",
        _HEADERLINE,
        *[_format_line(d) for d in data],
        "EOD",
        # Configure terminal
        f"set terminal dumb ansirgb size {termsize.columns} {(termsize.lines - 12) / 5} enhanced",
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
        "set border back",
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


_ONE_DAY = datetime.timedelta(days=1)


def big_display(x, previous):
    # Display the current total view count in big letters using figlet
    termsize = shutil.get_terminal_size((80, 20))
    font = pkg_resources.resource_filename("rr_stats", "data/bigmono12.tlf")
    left = figletize.figletize(
        str(x),
        font=font,
        spacing=figletize.Spacing.FULLWIDTH,
    )
    left_width = max(len(l) for l in left.splitlines())
    right = figletize.figletize(
        f"(+{x - previous})",
        font=font,
        justification=figletize.Justification.RIGHT,
        width=termsize.columns - left_width,
        spacing=figletize.Spacing.FULLWIDTH,
    )
    print(
        colorama.Style.BRIGHT
        + colorama.Fore.GREEN
        + figletize.concat(left, right)
        + colorama.Style.RESET_ALL
    )


def small_display(field, x, previous):
    termsize = shutil.get_terminal_size((80, 20))
    line = f"{field}: {x} (+{x - previous})"
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN + line + colorama.Style.RESET_ALL)


def main():
    # Get necessary information and set things up
    colorama.init()
    print(colorama.ansi.clear_screen())
    termsize = shutil.get_terminal_size((80, 20))
    data = list(stats.read_samples(stats.connect(stats.OpenMode.READ_ONLY)))

    current = max(data, key=lambda d: d.timestamp)
    in_last_day = [d for d in data if current.timestamp - d.timestamp < _ONE_DAY]
    last_day = min(in_last_day, key=lambda d: d.timestamp)

    big_display(current.total_views, last_day.total_views)
    small_display("Average Views", current.average_views, last_day.average_views)
    small_display("Favorites", current.favorites, last_day.favorites)
    small_display("Followers", current.followers, last_day.followers)

    # Display graphs of major stats
    gnuplot_program = _make_gnuplot_program(data, termsize)
    plot = subprocess.run(
        ["gnuplot"],
        input="\n".join(gnuplot_program).encode("utf-8"),
        check=True,
    )


def watch():
    main()
    stats.watch_db(main)
