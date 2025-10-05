"""Main CLI entry point for AIR toolkit."""

import click
from rich.console import Console

from air import __version__
from air.commands import (
    init,
    link,
    validate,
    status,
    classify,
    pr,
    review,
    claude,
    task,
    track,
    summary,
    analyze,
    findings,
    wait,
    upgrade,
)

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="air")
@click.pass_context
def main(ctx: click.Context) -> None:
    """AIR - AI Review & Development Toolkit.

    A unified toolkit for AI-assisted development and multi-project code assessment.

    \b
    Assessment Workflow:
      air init my-review        Create assessment project
      air link                  Link repositories
      air validate              Validate structure
      air status                Show project status

    \b
    Task Tracking:
      air track init            Initialize .ai/ tracking
      air task new "desc"       Create task file
      air summary               Generate summary
    """
    ctx.ensure_object(dict)


# Assessment commands
main.add_command(init.init)
main.add_command(link.link)
main.add_command(validate.validate)
main.add_command(status.status)
main.add_command(classify.classify)
main.add_command(pr.pr)
main.add_command(review.review)
main.add_command(analyze.analyze)
main.add_command(findings.findings)
main.add_command(wait.wait)
main.add_command(upgrade.upgrade)

# AI assistant commands
main.add_command(claude.claude)

# Task tracking commands
main.add_command(task.task)
main.add_command(track.track)
main.add_command(summary.summary)


if __name__ == "__main__":
    main()
