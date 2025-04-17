import numpy as np
import elastica as ea
from material import MaterialParams
from pydantic import BaseModel


class StraightRodParams(BaseModel):
    """
    All units are in millimeters.
    """

    start_position: tuple[float, float, float]
    direction: tuple[float, float, float]  # Should be unit vector
    normal: tuple[
        float, float, float
    ]  # Should be perpendicular to direction, unit vector
    base_length: float  # Should be positive
    base_radius: float  # Should be positive

    n_elem: int = 50  # Fix to 50


def create_straight_rod(
    rod_params: StraightRodParams,
    material: MaterialParams,
) -> ea.CosseratRod:
    """
    Create a straight Cosserat rod with specified parameters.
    """

    shear_modulus = material.youngs_modulus / (2 * (1 + material.poisson_ratio))

    return ea.CosseratRod.straight_rod(
        rod_params.n_elem,
        np.array(rod_params.start_position, dtype=np.float64),
        np.array(rod_params.direction, dtype=np.float64),
        np.array(rod_params.normal, dtype=np.float64),
        rod_params.base_length,
        rod_params.base_radius,
        material.density,
        youngs_modulus=material.youngs_modulus,
        shear_modulus=shear_modulus,
    )
