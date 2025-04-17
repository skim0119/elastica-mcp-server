from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class SimulationState:
    """
    State of an Elastica simulation.

    Attributes
    ----------
    is_running : bool
        Whether the simulation is currently running.
    progress : float
        Simulation progress from 0.0 to 1.0.
    current_time : float
        Current simulation time.
    parameters : SimulationParameters
        Parameters used for the simulation.
    avg_forward_velocity : Optional[float]
        Average forward velocity (if available).
    avg_lateral_velocity : Optional[float]
        Average lateral velocity (if available).
    results : Optional[Dict[str, List]]
        Post-processing data from the simulation (if available).
    """

    is_running: bool = False
    progress: float = 0.0
    current_time: float = 0.0
    avg_forward_velocity: Optional[float] = None
    avg_lateral_velocity: Optional[float] = None
    results: Optional[Dict[str, List]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the state to a dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the state.
        """
        return {
            "is_running": self.is_running,
            "progress": self.progress,
            "current_time": self.current_time,
            "parameters": self.parameters.to_dict(),
            "avg_forward_velocity": self.avg_forward_velocity,
            "avg_lateral_velocity": self.avg_lateral_velocity,
            # Exclude results as they can be large
        }
