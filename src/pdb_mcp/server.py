from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from pdb_mcp.session import PdbSession

_session = PdbSession()


@asynccontextmanager
async def lifespan(server):
    yield
    _session.end()


mcp = FastMCP("pdb-mcp", lifespan=lifespan)


@mcp.tool()
def start_debug(
    file_path: str,
    args: list[str] | None = None,
    python_path: str | None = None,
    use_pytest: bool = False,
    ssh_host: str | None = None,
    remote_cwd: str | None = None,
    remote_python: str | None = None,
) -> str:
    """Start a pdb debugging session on a Python file.

    Args:
        file_path: Path to the Python file to debug.
        args: Optional arguments to pass to the script.
        python_path: Python interpreter to use (local). Auto-detected if not provided.
        use_pytest: If True, run with pytest --pdb instead of python -m pdb.
        ssh_host: SSH host to debug on remotely (e.g. "myserver" or "user@host"). Requires key-based SSH auth configured in ~/.ssh/.
        remote_cwd: Working directory on the remote host. Required for remote debugging.
        remote_python: Python interpreter path on the remote host. Defaults to "python3".
    """
    try:
        output = _session.start(
            file_path, args=args, python_path=python_path, use_pytest=use_pytest,
            ssh_host=ssh_host, remote_cwd=remote_cwd, remote_python=remote_python,
        )
        return f"Debugging started: {_session.file_path}\n\n{output}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def run_command(command: str, timeout: int | None = None) -> str:
    """Send any pdb command. This is the escape hatch for anything not covered by other tools.

    Common commands: n (next), s (step), c (continue), r (return),
    p expr (print), pp expr (pretty print), l (list), ll (long list),
    a (args), w (where/stack), u (up), d (down), b file:line (breakpoint),
    cl num (clear breakpoint), q (quit), h (help),
    until <line> (run until line), jump <line> (set execution point),
    display expr (auto-print expr at every stop), undisplay expr

    Args:
        command: The pdb command string.
        timeout: Seconds to wait for response. Defaults to 10. Increase for long-running commands.
    """
    try:
        return _session.send(command, timeout=timeout)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def step() -> str:
    """Step into the next function call (pdb 's' command)."""
    try:
        return _session.send("s")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def next_line() -> str:
    """Execute the next line, stepping over function calls (pdb 'n' command)."""
    try:
        return _session.send("n")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def continue_exec(timeout: int = 30) -> str:
    """Continue execution until the next breakpoint (pdb 'c' command).

    Args:
        timeout: Seconds to wait for next breakpoint. Defaults to 30.
    """
    try:
        return _session.send("c", timeout=timeout)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def return_exec(timeout: int = 30) -> str:
    """Continue execution until the current function returns (pdb 'r' command).

    Args:
        timeout: Seconds to wait. Defaults to 30.
    """
    try:
        return _session.send("r", timeout=timeout)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def print_expr(expression: str) -> str:
    """Evaluate and print an expression in the current frame.

    Args:
        expression: Python expression to evaluate (e.g., variable name, len(items), self.attr).
    """
    try:
        return _session.send(f"p {expression}")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def set_breakpoint(file_path: str, line: int, condition: str | None = None) -> str:
    """Set a breakpoint at file:line, optionally with a condition.

    Args:
        file_path: Path to the file.
        line: Line number.
        condition: Optional condition expression (breakpoint only triggers when True).
    """
    try:
        cmd = f"b {file_path}:{line}"
        if condition:
            cmd += f", {condition}"
        return _session.send(cmd)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def clear_breakpoint(bp_number: int) -> str:
    """Clear a breakpoint by its number. Use list_breakpoints to see numbers.

    Args:
        bp_number: Breakpoint number to clear.
    """
    try:
        return _session.send(f"cl {bp_number}")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_breakpoints() -> str:
    """List all current breakpoints."""
    try:
        return _session.send("b")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def where() -> str:
    """Show the current stack trace."""
    try:
        return _session.send("w")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def up() -> str:
    """Move up one frame in the call stack."""
    try:
        return _session.send("u")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def down() -> str:
    """Move down one frame in the call stack."""
    try:
        return _session.send("d")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def list_source(lines: int | None = None) -> str:
    """Show source code around the current line.

    Args:
        lines: Number of lines to show. Omit for default (11 lines).
    """
    try:
        cmd = f"l .{'' if lines is None else f', {lines}'}"
        return _session.send(cmd)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def restart() -> str:
    """Restart the debugging session from the beginning with the same file and arguments.
    Useful after editing code — no need to call end_debug + start_debug.
    """
    try:
        output = _session.restart()
        return f"Restarted: {_session.file_path}\n\n{output}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def until(line: int) -> str:
    """Continue execution until a line greater than or equal to the given line is reached.
    Useful for skipping past loops.

    Args:
        line: Line number to run until.
    """
    try:
        return _session.send(f"until {line}", timeout=30)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def jump(line: int) -> str:
    """Set the next line to be executed. Does not execute intervening code.

    Args:
        line: Line number to jump to.
    """
    try:
        return _session.send(f"jump {line}")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def display(expression: str) -> str:
    """Auto-print an expression every time execution stops.
    Call again with the same expression to remove it.
    Use without arguments (via run_command('display')) to see all active display expressions.

    Args:
        expression: Python expression to watch (e.g., self.state, len(items)).
    """
    try:
        return _session.send(f"display {expression}")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def undisplay(expression: str) -> str:
    """Remove a display expression so it no longer auto-prints at each stop.

    Args:
        expression: The expression to stop watching.
    """
    try:
        return _session.send(f"undisplay {expression}")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def end_debug() -> str:
    """End the current debugging session and clean up."""
    try:
        _session.end()
        return "Debugging session ended."
    except Exception as e:
        return f"Error: {e}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
