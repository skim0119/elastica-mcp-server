from typing import Literal, TypeAlias, Any

from pydantic import BaseModel

AvailableMaterials: TypeAlias = Literal[
    "MuscleHydrostat", "SoftMaterial", "BoneMaterial"
]


class MaterialParams(BaseModel):
    density: float
    youngs_modulus: float
    poisson_ratio: float = 0.5


def material_factory(material_name: AvailableMaterials) -> dict[str, Any]:
    if material_name == "MuscleHydrostat":
        return {
            "density": 1000,
            "youngs_modulus": 1e6,
        }
    elif material_name == "SoftMaterial":
        return {
            "density": 1000,
            "youngs_modulus": 5e5,
        }
    elif material_name == "BoneMaterial":
        return {
            "density": 3000,
            "youngs_modulus": 1e7,
            "poisson_ratio": 0.3,
        }
    else:
        raise ValueError(f"Invalid material name: {material_name}")
