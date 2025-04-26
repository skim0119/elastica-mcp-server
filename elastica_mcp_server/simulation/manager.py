from typing import Any, Callable

import elastica as ea
import numpy as np

from ..material import MaterialParams
from .environment import (
    Simulator,
    RodCallBack,
    BuildResponse,
    compute_projected_velocity,
)
from .rod_strategy import StraightRodParams, create_straight_rod


def only_allow_once(func: Callable) -> Callable:
    """
    Decorator to allow a function to be called only once.
    """

    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        name = func.__name__
        flag_name = f"_only_allow_once_{name}"
        if not hasattr(self, flag_name):
            setattr(self, flag_name, True)
            return func(self, *args, **kwargs)
        else:
            raise ValueError(
                f"Function {name} can only be called once. If you need to modify the simulator contents, please delete the simulator and recreate it."
            )

    return wrapper


class SimulationInstance:
    """
    State of an Elastica simulation.
    """

    def __init__(self, simulator_tag: str):
        self.simulator_tag = simulator_tag
        self.simulator = Simulator()
        self.timestepper = ea.PositionVerlet()
        self.rods: dict[str, ea.CosseratRod] = {}
        self.callbacks: dict[str, dict[str, list[Any]]] = {}
        self.time_step = 1e-4
        self.rendering_fps = 60
        self.simulation_time = 0.0

    @property
    def step_skip(self) -> int:
        return int(1.0 / (self.rendering_fps * self.time_step))

    @only_allow_once
    def finalize(self) -> None:
        self.simulator.finalize()

    def create_rod(
        self, rod_tag: str, rod_params: StraightRodParams, material: MaterialParams
    ) -> BuildResponse:
        status = True

        rod = create_straight_rod(rod_params, material)
        self.rods[rod_tag] = rod
        self.simulator.append(rod)

        # Add gravity to the rod
        gravitational_acc = -9.80665
        self.simulator.add_forcing_to(rod).using(
            ea.GravityForces, acc_gravity=np.array([0.0, gravitational_acc, 0.0])
        )

        # Add damping
        damping_constant = 2e-3
        self.simulator.dampen(rod).using(
            ea.AnalyticalLinearDamper,
            damping_constant=damping_constant,
            time_step=self.time_step,
        )

        # Collect diagnostics
        pp_list: dict[str, list[Any]] = ea.defaultdict(list)
        self.simulator.collect_diagnostics(rod).using(
            RodCallBack, step_skip=self.step_skip, callback_params=pp_list
        )
        self.callbacks[rod_tag] = pp_list

        return BuildResponse(
            last_operation_message="Rod created", last_operation_success=status
        )

    def run_simulation(self, run_time: float) -> tuple[float, float]:
        simulation_start_time = self.simulation_time
        for _ in range(int(run_time / self.time_step)):
            self.simulation_time = float(
                self.timestepper.step(
                    self.simulator,
                    np.float64(self.simulation_time),
                    np.float64(self.time_step),
                )
            )

        return simulation_start_time, self.simulation_time

    def get_current_position(self, rod_tag: str) -> list[list[float]]:
        data_dict = self.callbacks[rod_tag]
        return data_dict["position"][-1].tolist()

    @only_allow_once
    def mimic_snake_motion(self, rod_tag: str, rod_params: StraightRodParams) -> None:
        wave_length = 1.0
        period = 2
        b_coeff = np.array(
            [3.4e-3, 3.3e-3, 4.2e-3, 2.6e-3, 3.6e-3, 3.5e-3, wave_length],
        )

        # Add muscle torques
        rod = self.rods[rod_tag]
        self.simulator.add_forcing_to(rod).using(
            ea.MuscleTorques,
            base_length=rod_params.base_length,
            b_coeff=b_coeff[:-1],
            period=period,
            wave_number=2.0 * np.pi / (wave_length),
            phase_shift=0.0,
            rest_lengths=rod.rest_lengths,
            ramp_up_time=period,
            direction=np.array(rod_params.normal, dtype=np.float64),
            with_spline=True,
        )

        # Add friction forces
        ground_plane = ea.Plane(
            plane_origin=np.array([0.0, -rod_params.base_radius, 0.0]),
            plane_normal=np.array(rod_params.normal, dtype=np.float64),
        )
        self.simulator.append(ground_plane)
        slip_velocity_tol = 1e-8
        froude = 0.1
        gravitational_acc = -9.80665
        mu = rod_params.base_length / (
            period * period * np.abs(gravitational_acc) * froude
        )
        kinetic_mu_array = np.array(
            [mu, 1.5 * mu, 2.0 * mu]
        )  # [forward, backward, sideways]
        static_mu_array = np.zeros(kinetic_mu_array.shape)
        self.simulator.detect_contact_between(rod, ground_plane).using(
            ea.RodPlaneContactWithAnisotropicFriction,
            k=1.0,
            nu=1e-6,
            slip_velocity_tol=slip_velocity_tol,
            static_mu_array=static_mu_array,
            kinetic_mu_array=kinetic_mu_array,
        )

    def get_velocity(self, rod_tag: str) -> dict[str, list[float]]:
        data_dict = self.callbacks[rod_tag]
        period = 2
        _, _, avg_forward, avg_lateral = compute_projected_velocity(data_dict, period)
        return {
            "average_forward_velocity": avg_forward.tolist(),
            "average_lateral_velocity": avg_lateral.tolist(),
        }


# Singleton class to manage multiple simulation instances
class Manager:
    def __new__(cls) -> "Manager":
        if not hasattr(cls, "instance"):
            cls.instance = super(Manager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.simulations = {}
        self.simulation_counter = 0

        # TODO: use multithreading later ot run multiple instances
        self._max_simulation_count = 10

    def create_simulation(self, simulator_tag: str) -> None:
        if self.simulation_counter >= self._max_simulation_count:
            raise ValueError(
                "Maximum number of simulations reached. Please delete some simulations before creating a new one."
            )
        self.simulations[simulator_tag] = SimulationInstance(simulator_tag)
        self.simulation_counter += 1

    def delete_simulation(self, simulator_tag: str) -> None:
        if simulator_tag in self.simulations:
            del self.simulations[simulator_tag]
            self.simulation_counter -= 1

    def __getitem__(self, simulator_tag: str) -> SimulationInstance:
        return self.simulations[simulator_tag]
