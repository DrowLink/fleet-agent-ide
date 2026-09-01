"""
Fleet CLI Main Entrypoint with 1-Command App Launcher.
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
import uvicorn
from fleet_cli.client import FleetClient

app = typer.Typer(
    name="fleet",
    help="🚀 Fleet Agent IDE - Multi-Agent Local Orchestrator with Git Worktree Isolation",
)
console = Console()


@app.command()
def app_cmd(
    host: str = typer.Option("127.0.0.1", help="Host address to bind"),
    port: int = typer.Option(8000, help="Backend Daemon port"),
    web_port: int = typer.Option(5173, help="Frontend UI port"),
    no_browser: bool = typer.Option(False, help="Do not auto-open browser"),
):
    """🚀 Start the Fleet Agent IDE Full Suite (Daemon + Web Dashboard) in 1 command."""
    console.print(
        Panel.fit(
            f"[bold cyan]🚀 Launching Fleet Agent IDE Full Suite[/bold cyan]\n"
            f"[green]Backend Daemon:[/green] http://{host}:{port}\n"
            f"[cyan]Web Dashboard:[/cyan] http://{host}:{web_port}",
            border_style="cyan",
        )
    )

    # Resolve repo root
    cwd = Path.cwd()
    web_dir = cwd / "web"

    # Start Daemon process
    daemon_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "fleet_backend.api.server:app",
        "--host",
        host,
        "--port",
        str(port),
    ]

    daemon_proc = subprocess.Popen(
        daemon_cmd,
        cwd=str(cwd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Start Web Vite process
    npm_exec = "npm.cmd" if os.name == "nt" else "npm"
    web_proc = None
    if web_dir.exists():
        console.print("[dim]Starting Web Dashboard (Vite)...[/dim]")
        web_proc = subprocess.Popen(
            [npm_exec, "run", "dev", "--", "--port", str(web_port)],
            cwd=str(web_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    time.sleep(2)

    ui_url = f"http://{host}:{web_port}"
    if not no_browser:
        console.print(f"[bold green]✔ Opening {ui_url} in your browser...[/bold green]")
        webbrowser.open(ui_url)

    console.print("[bold yellow]Press Ctrl+C to stop Fleet Agent IDE...[/bold yellow]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold red]Shutting down Fleet Agent IDE...[/bold red]")
        if web_proc:
            web_proc.terminate()
        daemon_proc.terminate()
        console.print("[green]Shutdown complete.[/green]")


# Alias "fleet start" and "fleet ui" to "fleet app"
@app.command(name="start")
def start_cmd(
    host: str = typer.Option("127.0.0.1", help="Host address to bind"),
    port: int = typer.Option(8000, help="Backend Daemon port"),
    web_port: int = typer.Option(5173, help="Frontend UI port"),
    no_browser: bool = typer.Option(False, help="Do not auto-open browser"),
):
    """Alias for 'fleet app'."""
    app_cmd(host=host, port=port, web_port=web_port, no_browser=no_browser)


@app.command(name="ui")
def ui_cmd(
    host: str = typer.Option("127.0.0.1", help="Host address to bind"),
    port: int = typer.Option(8000, help="Backend Daemon port"),
    web_port: int = typer.Option(5173, help="Frontend UI port"),
    no_browser: bool = typer.Option(False, help="Do not auto-open browser"),
):
    """Alias for 'fleet app'."""
    app_cmd(host=host, port=port, web_port=web_port, no_browser=no_browser)


@app.command()
def daemon(
    host: str = typer.Option("127.0.0.1", help="Host address to bind"),
    port: int = typer.Option(8000, help="Port to run the API daemon"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
):
    """Start the Fleet Daemon background service only."""
    console.print(
        Panel.fit(
            f"[bold cyan]Fleet Agent IDE Daemon[/bold cyan]\n[green]http://{host}:{port}[/green]",
            border_style="cyan",
        )
    )
    uvicorn.run("fleet_backend.api.server:app", host=host, port=port, reload=reload)


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Feature or bugfix description"),
    title: str = typer.Option("CLI Task", help="Short title for the task"),
    base_ref: str = typer.Option("HEAD", help="Base commit or branch"),
    server: str = typer.Option("http://127.0.0.1:8000", help="Fleet Daemon URL"),
):
    """Dispatch a new task to the fleet orchestrator."""
    client = FleetClient(server)
    try:
        res = client.create_task(title=title, prompt=prompt, base_ref=base_ref)
        console.print(f"[bold green]✔ Task created and scheduled successfully![/bold green]")
        console.print(f"Task ID: [cyan]{res['task_id']}[/cyan] (Subtasks: {res['subtasks_count']})")
    except Exception as e:
        console.print(f"[bold red]Failed to submit task: {e}[/bold red]")


@app.command()
def status(
    server: str = typer.Option("http://127.0.0.1:8000", help="Fleet Daemon URL"),
):
    """Inspect active tasks and subtask states."""
    client = FleetClient(server)
    try:
        tasks = client.list_tasks()
        if not tasks:
            console.print("[yellow]No tasks recorded yet.[/yellow]")
            return

        table = Table(title="Fleet Agent Tasks", border_style="cyan")
        table.add_column("Task ID", style="cyan")
        table.add_column("Title", style="bold")
        table.add_column("Status", style="magenta")
        table.add_column("Created At", style="green")

        for t in tasks:
            table.add_row(t.get("id", ""), t.get("title", ""), t.get("status", ""), t.get("created_at", "")[:19])

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error querying daemon: {e}[/bold red]")


@app.command()
def worktrees(
    server: str = typer.Option("http://127.0.0.1:8000", help="Fleet Daemon URL"),
):
    """List active Git worktrees."""
    client = FleetClient(server)
    try:
        wts = client.list_worktrees()
        if not wts:
            console.print("[yellow]No worktrees currently active.[/yellow]")
            return

        table = Table(title="Active Git Worktrees", border_style="green")
        table.add_column("Path", style="cyan")
        table.add_column("Branch", style="magenta")
        table.add_column("Head Commit", style="green")

        for w in wts:
            table.add_row(w.get("path", ""), w.get("branch", "(detached)"), w.get("head", "")[:8])

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error listing worktrees: {e}[/bold red]")


if __name__ == "__main__":
    app()
