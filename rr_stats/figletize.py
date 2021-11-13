import subprocess
import enum
from typing import Optional, Union
import pathlib


class Justification(enum.Enum):
    DEFAULT = "-x"
    TEXT = "-x"
    LEFT = "-l"
    RIGHT = "-r"
    CENTER = "-c"


class RTL(enum.Enum):
    DEFAULT = "-X"
    FONT = "-X"
    LEFT_TO_RIGHT = "-L"
    RIGHT_TO_LEFT = "-R"


class Spacing(enum.Enum):
    DEFAULT = "-s"
    SMUSH = "-s"
    FORCE_SMUSH = "-S"
    KERN = "-k"
    FULLWIDTH = "-W"
    OVERLAP = "-o"


def figletize(
    text: str,
    justification: Optional[Justification] = None,
    rtl: Optional[RTL] = None,
    spacing: Optional[Spacing] = None,
    font: Union[None, str, pathlib.Path] = None,
    width: Optional[int] = None,
) -> str:
    args = ["figlet"]
    if justification:
        args += [justification.value]
    if rtl:
        args += [rtl.value]
    if spacing:
        args += [spacing.value]
    if font:
        args += ["-f", font]
    if width:
        args += ["-w", str(width)]
    else:
        args += ["-t"]

    p = subprocess.run(
        args,
        input=text.encode("utf-8"),
        check=True,
        capture_output=True,
    )
    return p.stdout.decode("utf-8")


def concat(left: str, right: str) -> str:
    return "\n".join(l + r for l, r in zip(left.splitlines(), right.splitlines()))
