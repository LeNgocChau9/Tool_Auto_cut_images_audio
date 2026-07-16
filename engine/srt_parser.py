"""SRT subtitle file parser.

Handles standard SRT format with multiple encoding fallbacks
for Vietnamese and other non-ASCII content.
"""

import re
from dataclasses import dataclass


@dataclass
class SrtSegment:
    """A single subtitle segment with timing and text."""

    index: int
    start_time: float   # seconds
    end_time: float      # seconds
    text: str

    @property
    def duration(self) -> float:
        """Duration of this segment in seconds."""
        return self.end_time - self.start_time

    def start_display(self) -> str:
        """Format start time as HH:MM:SS."""
        return _format_time(self.start_time)

    def end_display(self) -> str:
        """Format end time as HH:MM:SS."""
        return _format_time(self.end_time)


def _format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_timestamp(ts: str) -> float:
    """Convert SRT timestamp string to seconds.

    Accepts formats: HH:MM:SS,mmm or HH:MM:SS.mmm
    """
    match = re.match(r'(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})', ts.strip())
    if not match:
        raise ValueError(f"Invalid SRT timestamp: '{ts}'")
    hours, minutes, seconds, millis = match.groups()
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis) / 1000
    )


def parse_srt(filepath: str) -> list[SrtSegment]:
    """Parse an SRT file into a list of SrtSegments.

    Tries multiple encodings to handle Vietnamese and other
    non-ASCII text: UTF-8 BOM, UTF-8, Latin-1, Windows-1252.

    Args:
        filepath: Path to the .srt file.

    Returns:
        List of SrtSegment sorted by index.

    Raises:
        ValueError: If the file cannot be read or parsed.
    """
    content = None
    for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        raise ValueError(f"Cannot read SRT file (encoding issue): {filepath}")

    segments = []
    # Split into blocks by one or more blank lines
    blocks = re.split(r'\n\s*\n', content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue

        # Line 1: subtitle index
        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        # Line 2: timestamp range
        ts_match = re.match(
            r'(\d{1,2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{3})',
            lines[1].strip()
        )
        if not ts_match:
            continue

        start_time = parse_timestamp(ts_match.group(1))
        end_time = parse_timestamp(ts_match.group(2))

        # Lines 3+: subtitle text
        text = '\n'.join(lines[2:]).strip()

        segments.append(SrtSegment(
            index=index,
            start_time=start_time,
            end_time=end_time,
            text=text,
        ))

    if not segments:
        raise ValueError("No valid subtitle segments found in SRT file.")

    segments.sort(key=lambda s: s.index)
    return segments
