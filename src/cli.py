import click
import sys
import os
from src.core.controller import DTMController
from src.core.remote import RemoteManager

@click.group()
@click.version_option(
    version="0.2.1", # Fallback or hardcoded since we are controlling source
    prog_name="dtm"
)
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

@main.command()
@click.argument('commit_a')
@click.argument('commit_b')
def diff(commit_a, commit_b):
    """Show changes between two commits."""
    try:
        controller = DTMController()
        diff_output = controller.diff(commit_a, commit_b)
        click.echo(diff_output)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.option('--port', default=8000, help='Port to run the web server on')
def web(port):
    """Start the Web Visualization Dashboard."""
    import uvicorn
    # Verify DTM repo exists
    if not os.path.exists(".dtm"):
        click.echo("Error: Not a DTM repository. Run 'dtm init' first.", err=True)
        return
        
    click.echo(f"Starting DTM Dashboard on http://localhost:{port}")
    uvicorn.run("src.web.app:app", host="127.0.0.1", port=port, log_level="info")

@main.group()
def remote():
    """Manage remote repositories."""
    pass

@remote.command(name="add")
@click.argument("name")
@click.argument("uri")
def remote_add(name, uri):
    """Add a new remote."""
    try:
        manager = RemoteManager()
        manager.add_remote(name, uri)
        click.echo(f"Added remote '{name}' pointing to {uri}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument("remote_name")
def push(remote_name):
    """Push commits and objects to a remote."""
    try:
        manager = RemoteManager()
        manager.push(remote_name)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument("remote_name")
def pull(remote_name):
    """Pull commits and objects from a remote."""
    try:
        manager = RemoteManager()
        manager.pull(remote_name)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    main()
