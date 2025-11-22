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
    Calcula el costo total para una lista de productos, generando subtotales y un total general.

    Esta herramienta es útil para generar cotizaciones detalladas. Para cada producto en la lista
    de entrada, multiplica su precio unitario por la cantidad solicitada para obtener el subtotal.
    Luego, suma los subtotales de todos los productos para calcular el costo total de la cotización.

    La herramienta devuelve un string en formato JSON que contiene una lista de los subtotales
    por producto, el total general de la cotización y un resumen detallado en texto plano
    ideal para ser mostrado directamente al usuario.

    Args:
        quote_input (QuoteInput): Un objeto que encapsula la lista de productos a cotizar.
            - products (List[ProductItem]): Una lista donde cada elemento representa un producto
              y debe contener:
                - name (str): El nombre del producto.
                - price (float): El precio unitario del producto (debe ser mayor que 0).
                - quantity (int): La cantidad de unidades del producto (debe ser mayor que 0).

    Returns:
        str: Un string en formato JSON con la siguiente estructura:
             - "subtotals": Una lista de diccionarios, cada uno con "product" y "subtotal".
             - "grand_total": El costo total de la cotización.
             - "details": Un resumen en texto formateado con el desglose de la cotización.
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