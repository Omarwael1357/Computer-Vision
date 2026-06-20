from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(message)s",
        datefmt="%H:%M:%S",
        handlers=[RichHandler(markup=True, rich_tracebacks=True)],
    )


def print_banner() -> None:
    console.print("[bold cyan]Real-Time Face Recognition System[/bold cyan]")


def print_controls() -> None:
    console.print(
        "[dim]Controls: [bold]Q[/bold]=quit, [bold]E[/bold]=enroll, [bold]I[/bold]=image enroll, [bold]L[/bold]=list, [bold]R[/bold]=remove, [bold]S[/bold]=screenshot[/dim]"
    )


def print_identities(identities: list[str]) -> None:
    if not identities:
        console.print("[yellow]No enrolled identities.[/yellow]")
        return
    console.print("[green]Enrolled identities:[/green]")
    for name in identities:
        console.print(f" - {name}")


def prompt(message: str) -> str:
    return console.input(f"[bold]{message} [/bold]")
