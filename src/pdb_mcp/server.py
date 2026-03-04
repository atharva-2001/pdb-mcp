from mcp.server.fastmcp import FastMCP

from pdb_mcp.session import PdbSession

mcp = FastMCP("pdb-mcp")

# Single global session for now
_session = PdbSession()


@mcp.tool()
def start_debug(
    file_path: str,
    args: list[str] | None = None,
    python_path: str | None = None,
    use_pytest: bool = False,
) -> str:
    """Start a pdb debugging session on a Python file.

    Args:
        file_path: Path to the Python file to debug.
        args: Optional arguments to pass to the script.
        python_path: Python interpreter to use. Auto-detected if not provided.
        use_pytest: If True, run with pytest --pdb instead of python -m pdb.
    """
    try:
        output = _session.start(file_path, args=args, python_path=python_path, use_pytest=use_pytest)
        return f"Debugging started: {_session.file_path}\n\n{output}"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def run_command(command: str) -> str:
    """Send any pdb command. This is the escape hatch for anything not covered by other tools.

    Common commands: n (next), s (step), c (continue), r (return),
    p expr (print), pp expr (pretty print), l (list), ll (long list),
    a (args), w (where/stack), u (up), d (down), b file:line (breakpoint),
    cl num (clear breakpoint), q (quit), h (help)

    Args:
        command: The pdb command string.
    """
    try:
        return _session.send(command)
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
def continue_exec() -> str:
    """Continue execution until the next breakpoint (pdb 'c' command)."""
    try:
        return _session.send("c")
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def return_exec() -> str:
    """Continue execution until the current function returns (pdb 'r' command)."""
    try:
        return _session.send("r")
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
