from typing import Any

import time
import numpy as np
import elastica as ea

from mcp.server.fastmcp import FastMCP

from material import material_factory, MaterialParams, AvailableMaterials
from rod_strategy import StraightRodParams, create_straight_rod
from environment import Simulator, BuildResponse, RodCallBack, RunResponse


mcp = FastMCP("elastica-mcp-server")
simulator = Simulator()
timestepper = ea.PositionVerlet()
callbacks = {}
time_step = 1e-4
rendering_fps = 60
finalized_flag = False
simulation_time = 0.0


@mcp.tool()  # type: ignore
def finalize_siulator() -> str:
    global finalized_flag
    finalized_flag = True
    simulator.finalize()
    return "Simulator finalized"


@mcp.tool()  # type: ignore
def reset_simulator() -> str:
    global simulator, finalized_flag, simulation_time
    simulator = Simulator()
    finalized_flag = False
    simulation_time = 0.0
    return "Simulator reset"


@mcp.tool()
def get_finalized_flag() -> bool:
    return finalized_flag


@mcp.tool()
def get_material(material_name: AvailableMaterials) -> MaterialParams:
    return material_factory(material_name)


@mcp.tool()
def get_snake_rod_params() -> dict[str, Any]:
    # TODO: temporary
    return {
        "start_position": (0.0, 0.0, 0.0),
        "direction": (0.0, 0.0, 1.0),
        "normal": (0.0, 1.0, 0.0),
        "base_length": 0.35,
        "base_radius": 0.35 * 0.011,
    }


@mcp.tool()
def create_rod(
    rod_name: str,
    rod_params: dict[str, Any],  # StraightRodParams
    material: dict[str, Any],  # MaterialParams
) -> BuildResponse:
    """
    Create a rod with the given parameters.

    Args:
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
        The response of the build operation.
            last_operation_message: The message of the last operation.
            last_operation_success: The success of the last operation.
    """
    # check schema
    _rod_params = StraightRodParams(**rod_params)
    _material = MaterialParams(**material)

    status = True

    rod = create_straight_rod(_rod_params, _material)
    simulator.append(rod)

    # Add gravity to the rod
    gravitational_acc = -9.80665
    simulator.add_forcing_to(rod).using(
        ea.GravityForces, acc_gravity=np.array([0.0, gravitational_acc, 0.0])
    )

    # Add damping
    step_skip = int(1.0 / (rendering_fps * time_step))
    damping_constant = 2e-3
    simulator.dampen(rod).using(
        ea.AnalyticalLinearDamper,
        damping_constant=damping_constant,
        time_step=time_step,
    )

    # Collect diagnostics
    pp_list: dict[str, list[Any]] = ea.defaultdict(list)
    simulator.collect_diagnostics(rod).using(
        RodCallBack, step_skip=step_skip, callback_params=pp_list
    )
    callbacks[rod_name] = pp_list

    return BuildResponse(
        last_operation_message="Rod created", last_operation_success=status
    )


@mcp.tool()
def get_position(rod_name: str) -> list[list[float]]:
    """
    Get the position of the rod.

    Args:
        rod_name: The name of the rod.

    Returns:
        The position of the rod at the last step.
    """
    data = callbacks[rod_name]

    return data["position"][-1].tolist()


@mcp.tool()
def run_simulation(run_time: float) -> RunResponse:
    global simulation_time
    status = True
    start_time = time.time()

    simulation_start_time = simulation_time
    for _ in range(int(run_time / time_step)):
        simulation_time = timestepper.step(simulator, simulation_time, time_step)

    return RunResponse(
        last_operation_message="Simulation run",
        last_operation_success=status,
        simulation_start_time=simulation_start_time,
        simulation_end_time=simulation_time,
        walltime=time.time() - start_time,
    )
