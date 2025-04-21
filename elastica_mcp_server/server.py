from typing import Any

from mcp.server.fastmcp import FastMCP

from .material import register_material_tools
from .simulation import register_simulation_tools


def instantiate_server() -> FastMCP:
    mcp = FastMCP("elastica-mcp-simulator")

    register_simulation_tools(mcp)
    register_material_tools(mcp)
    return mcp


def main() -> None:
    """
    Main function to run the server.
    """
    mcp = instantiate_server()

    # TODO: temporary
    @mcp.tool()
    def get_snake_rod_params() -> dict[str, Any]:
        """
        Get the parameters of the snake rod.

        Returns:
            dict[str, Any]: The parameters of the snake rod.
                start_position: The starting position of the snake rod.
                direction: The direction of the snake rod.
                normal: The normal vector of the snake rod.
                base_length: The length of the snake rod.
                base_radius: The radius of the snake rod.
                End-position is defined as start_position + direction * base_length.
        """
        return {
            "start_position": (0.0, 0.0, 0.0),
            "direction": (0.0, 0.0, 1.0),
            "normal": (0.0, 1.0, 0.0),
            "base_length": 0.35,
            "base_radius": 0.35 * 0.011,
        }

    mcp.run()


if __name__ == "__main__":
    main()
