from typing import Any
import time

from typing_extensions import TypedDict
from mcp.server.fastmcp import FastMCP
from .manager import Manager
from .rod_strategy import StraightRodParams
from ..material import MaterialParams


class SystemResponse(TypedDict, total=True):
    last_operation_message: str
    last_operation_success: bool


class RunResponse(TypedDict, total=True):
    last_operation_message: str
    last_operation_success: bool
    simulation_start_time: float
    simulation_end_time: float
    walltime: float


def register_simulation_tools(mcp: FastMCP) -> None:
    manager = Manager()

    @mcp.tool()  # type: ignore
    def create_simulator(simulator_tag: str) -> SystemResponse:
        """
        Create a new simulation with the given simulator_tag.
        If a simulation with the same tag already exists, it will throw an error.
        """

        manager.create_simulation(simulator_tag)
        return {
            "last_operation_message": f"Simulation created with tag {simulator_tag}",
            "last_operation_success": True,
        }

    @mcp.tool()  # type: ignore
    def delete_simulator(simulator_tag: str) -> SystemResponse:
        """
        Delete the simulation with the given simulator_tag.
        """
        manager.delete_simulation(simulator_tag)
        return {
            "last_operation_message": f"Simulation deleted with tag {simulator_tag}",
            "last_operation_success": True,
        }

    @mcp.tool()  # type: ignore
    def finalize_simulator(simulator_tag: str) -> SystemResponse:
        """
        Finalize the simulation with the given simulator_tag.
        Simulation must be finalized before running it.
        Any changes to the simulation after this point will not be reflected in the results.
        """
        manager[simulator_tag].finalize()
        return {
            "last_operation_message": f"Simulation finalized with tag {simulator_tag}",
            "last_operation_success": True,
        }

    @mcp.tool()  # type: ignore
    def create_rod(
        simulator_tag: str,
        rod_tag: str,
        rod_params: dict[str, Any],
        material: dict[str, Any],
    ) -> SystemResponse:
        """
        Create a straight rod with the given parameters.

        Args:
            simulator_tag: The tag of the simulator.
            rod_tag: The tag of the rod.
            rod_params: The parameters of the rod.
                start_position: The starting position of the rod.
                direction: The direction of the rod.
                normal: The normal vector of the rod.
                base_length: The length of the rod.
                base_radius: The radius of the rod.
            material: The material of the rod.
                density: The density of the rod.
                youngs_modulus: The Young's modulus of the rod.
                poisson_ratio: The Poisson's ratio of the rod. (default: 0.5)

        Returns:
            The response of the create rod operation.
        """
        manager[simulator_tag].create_rod(
            rod_tag, StraightRodParams(**rod_params), MaterialParams(**material)
        )
        return {
            "last_operation_message": f"Rod created with tag {rod_tag}",
            "last_operation_success": True,
        }

    @mcp.tool()  # type: ignore
    def get_current_position(simulator_tag: str, rod_tag: str) -> SystemResponse:
        """
        Get the current position of the rod.

        Args:
            simulator_tag: The tag of the simulator.
            rod_tag: The tag of the rod.

        Returns:
            The current position of the rod.
        """
        return manager[simulator_tag].get_current_position(rod_tag)

    @mcp.tool()  # type: ignore
    def run_simulation(simulator_tag: str, run_time: float) -> RunResponse:
        """
        Run the simulation with the given run_time.

        Args:
            simulator_tag: The tag of the simulator.
            run_time: The time to run the simulation.

        Returns:
            The response of the run simulation operation.
        """
        status = True
        start_time = time.time()

        simulation_start_time, simulation_end_time = manager[
            simulator_tag
        ].run_simulation(run_time)

        return RunResponse(
            last_operation_message="Simulation finished running",
            last_operation_success=status,
            simulation_start_time=simulation_start_time,
            simulation_end_time=simulation_end_time,
            walltime=time.time() - start_time,
        )

    # Temporary tool
    @mcp.tool()  # type: ignore
    def mimic_snake_motion(simulator_tag: str, rod_tag: str) -> None:
        """
        Mimic snake motion with the given parameters.
        """
        manager[simulator_tag].mimic_snake_motion(rod_tag)

    @mcp.tool()  # type: ignore
    def get_velocity(simulator_tag: str, rod_tag: str) -> dict[str, float]:
        """
        Get the velocity of the rod.

        Args:
            simulator_tag: The tag of the simulator.
            rod_tag: The tag of the rod.

        Returns:
            The velocity of the rod.
                average_forward_velocity: The average forward velocity of the rod.
                average_lateral_velocity: The average lateral velocity of the rod.
        """
        return manager[simulator_tag].get_velocity(rod_tag)


# Force Application Tool
# Apply external forces (gravity, endpoint forces)
# Apply muscle torques with customizable parameters
# Add custom forces with mathematical expressions
# Constraint Builder Tool
# Add boundary conditions (fixed ends, hinges)
# Create joints between elements (fixed, hinged, ball)
# Define periodic boundary conditions
# Contact Definition Tool
# Set up rod-plane contacts with friction
# Configure rod-rod and self-contacts
# Define contact parameters
# Diagnostic Capture Tool
# Define callbacks for data collection
# Specify data to record (positions, velocities, energies)
# Set capture frequency
# Visualization Configuration Tool
# Configure rendering parameters
# Set up video generation
# Define plot types and parameters
# Simulation Runner Tool
# Run the simulation with progress tracking
# Control stop conditions
# Handle restarts
