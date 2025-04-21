from typing import Literal, TypeAlias, Any

from pydantic import BaseModel

from mcp.server.fastmcp import FastMCP

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


def register_material_tools(mcp: FastMCP):
    @mcp.tool()  # type: ignore
    def get_material(material_name: AvailableMaterials) -> MaterialParams:
        return material_factory(material_name)
