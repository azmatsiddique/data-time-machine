import click
import sys
from src.core.controller import DTMController

@click.group()
def main():
    """Data Lineage Time Machine (DTM) CLI."""
    pass

@main.command()
def init():
    """Initialize a new DTM repository."""
    try:
        controller = DTMController()
        controller.init()
        click.echo("Initialized DTM repository.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.option('--message', '-m', required=True, help='Commit message')
def snapshot(message):
    """Snapshot the current state of the workspace."""
    try:
        controller = DTMController()
        commit_id = controller.snapshot(message)
        click.echo(f"Created snapshot: {commit_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('commit_id')
def checkout(commit_id):
    """Restore the workspace to a specific snapshot."""
    try:
        controller = DTMController()
        controller.checkout(commit_id)
        click.echo(f"Checked out snapshot: {commit_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
def log():
    """Show the snapshot history."""
    try:
        controller = DTMController()
        history = controller.log()
        for commit in history:
            click.echo(f"Commit: {commit.id}")
            click.echo(f"Date:   {commit.timestamp}")
            click.echo(f"Message: {commit.message}")
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    main()
