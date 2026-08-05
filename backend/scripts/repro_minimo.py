"""
repro_minimo.py -- reproduccion minima, SIN NADA del proyecto FFE.

Prueba exactamente el mismo patron que graphe_agent_llm.py: un nodo que
decide un booleano, una arista condicional que lo lee, y un nodo final.
Si esto falla tambien en tu maquina, confirmamos un problema de LangGraph
en si mismo (posiblemente especifico de Windows) -- no de tu codigo.

Uso:
    uv run python repro_minimo.py
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


class Estado(TypedDict, total=False):
    valor: bool
    texto: str


def nodo_decide(estado: Estado) -> dict:
    return {"valor": True, "texto": "hola"}


def nodo_final(estado: Estado) -> dict:
    return {"texto": "final"}


def arista(estado: Estado) -> str:
    print("  [arista ve] valor =", estado.get("valor"))
    return "si" if estado.get("valor") else "no"


grafo = StateGraph(Estado)
grafo.add_node("decide", nodo_decide)
grafo.add_node("intermedio", lambda e: {"texto": "paso por intermedio"})
grafo.add_node("final", nodo_final)
grafo.set_entry_point("decide")
grafo.add_conditional_edges("decide", arista, {"si": "intermedio", "no": "final"})
grafo.add_edge("intermedio", "final")
grafo.add_edge("final", END)

compilado = grafo.compile()
resultado = compilado.invoke({})
print("resultado final:", resultado)

assert "valor" in resultado, "FALLO: 'valor' no esta en el resultado final"
assert resultado["valor"] is True
print("OK: todo correcto")
