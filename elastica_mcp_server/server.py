from mcp.server.fastmcp import FastMCP

from .environment import Simulator


mcp = FastMCP("elastica-mcp-server")
simulator = Simulator()
finalized_flag = False


@mcp.tool()  # type: ignore
def finalize_siulator() -> str:
    global finalized_flag
    finalized_flag = True
    simulator.finalize()
    return "Simulator finalized"


@mcp.tool()  # type: ignore
def reset_simulator() -> str:
    global simulator, finalized_flag
    simulator = Simulator()
    finalized_flag = False
    return "Simulator reset"


@mcp.tool()
def get_finalized_flag() -> bool:
    global finalized_flag
    return finalized_flag
