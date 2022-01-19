from __future__ import annotations

from typing import Callable, Generator, Optional

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, Task, TimeElapsedColumn
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

PENDING = "[bright_black]PENDING... "
DONE = "[bold green]COMPLETED :heavy_check_mark:"


class PulseBarColumn(BarColumn):
    def render(self, task: Task) -> ProgressBar:
        """Gets a progress bar widget for a task."""
        return ProgressBar(
            total=max(0, task.total),
            completed=max(0, task.completed),
            width=None if self.bar_width is None else max(1, self.bar_width),
            pulse=task.completed < task.total,
            animation_time=task.get_time(),
            style=self.style,
            complete_style=self.complete_style,
            finished_style=self.finished_style,
            pulse_style=self.pulse_style,
        )


def init_ui(sequence: dict[str, Callable[[], None]]) -> None:
    class InitProgress(Progress):
        def get_renderables(self) -> Generator:
            try:
                task = self.tasks[0]
            except IndexError:
                return
            if task.completed >= task.total:
                task.description = "[bold]Initialized! :tada:"

            progress_bar = self.make_tasks_table(self.tasks)
            # Get spinner animation
            spinner: Text = next(progress_bar.columns[0].cells)  # type: ignore
            table = self.gen_init_table(int(task.completed), spinner=spinner)

            yield Panel(
                Group(table, "", progress_bar),
                title="[bold]Welcome to HiSeq! :clown_face:",
                expand=False,
            )

        def gen_init_table(self, now_at: int = 0, spinner: Optional[Text] = None) -> Table:
            grid = Table.grid(padding=(0, 25))
            grid.add_column()
            grid.add_column(justify="right")
            for i, step in enumerate(sequence.keys()):
                status: RenderableType
                if i > now_at:
                    name = "[bright_black]" + step
                    status = PENDING
                elif i == now_at:
                    name = "[bold]" + step
                    status = "DOING "
                    if spinner is not None:
                        status = Text(status, style="bold") + spinner
                else:
                    name = step
                    status = DONE

                grid.add_row(name, status)
            return grid

    with InitProgress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        PulseBarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[bold]Initializing...", total=len(sequence))
        for f in sequence.values():
            f()
            progress.advance(task)
