"""
Herramienta de calculadora para cotizaciones.
Permite multiplicar precio por cantidad para varios productos y sumar los totales.
"""

from typing import List
from pydantic import BaseModel, Field
from langchain.tools import tool

class ProductItem(BaseModel):
    """Esquema para un único producto en la cotización."""
    name: str = Field(..., description="Nombre del producto.")
    price: float = Field(..., gt=0, description="Precio unitario del producto.")
    quantity: int = Field(..., gt=0, description="Cantidad del producto.")

class QuoteInput(BaseModel):
    """Esquema del input para la herramienta de cálculo, conteniendo una lista de productos."""
    products: List[ProductItem] = Field(..., description="Lista de productos para la cotización.")

class CalculationResult(BaseModel):
    """Esquema para el resultado del cálculo."""
    subtotals: List[dict]
    grand_total: float
    details: str

@tool
def calculator_tool(quote_input: QuoteInput) -> str:
    """
    Calcula el costo total para una lista de productos.
    Para cada producto, multiplica su precio por la cantidad para obtener el subtotal.
    Finalmente, suma todos los subtotales para obtener el gran total de la cotización.

    Args:
        quote_input: Un objeto que contiene una lista de productos. Cada producto
                     debe tener 'name' (str), 'price' (float), y 'quantity' (int).

    Returns:
        Un string JSON con los subtotales, el total general y un resumen detallado.
    """
    products = quote_input.products
    if not products:
        return "No se proporcionaron productos para calcular."

    subtotals = []
    grand_total = 0

    for product in products:
        subtotal = product.price * product.quantity
        subtotals.append({
            "product": product.name,
            "subtotal": subtotal
        })
        grand_total += subtotal

    details = []
    for item in subtotals:
        details.append(f"- {item['product']}: ${item['subtotal']:.2f}")

    details.append(f"\n**Total General: ${grand_total:.2f}**")

    result = CalculationResult(
        subtotals=subtotals,
        grand_total=grand_total,
        details="\n".join(details)
    )

    return result.model_dump_json(indent=2)