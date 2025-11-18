---
cards-deck: Algoritmos
status: completo
tipo_nota: concepto
created: 2025-01-15
---

# MergeSort

MergeSort es un algoritmo de ordenamiento estable que utiliza el paradigma **divide y conquista**.

## Concepto

El algoritmo divide el array en mitades, ordena recursivamente cada mitad, y luego merge (fusiona) las dos mitades ordenadas.

## Complejidad

- **Todos los casos**: O(n log n) - GARANTIZADO
- **Espacio**: O(n) - requiere array auxiliar
- **Estabilidad**: Sí - mantiene el orden relativo de elementos iguales

## Ventajas sobre QuickSort

- Complejidad garantizada O(n log n) incluso en peor caso
- Algoritmo estable
- Predecible en rendimiento

## Desventajas

- Requiere O(n) espacio adicional
- Más lento en la práctica que [[QuickSort]] para arrays pequeños

## Implementación Python

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])

    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

## Casos de Uso

- Cuando necesitas estabilidad
- Cuando el peor caso importa
- Ordenamiento externo (archivos grandes)
- Listas enlazadas (no requiere acceso aleatorio)

## Relaciones

- Comparte paradigma divide y conquista con [[QuickSort]]
- Más predecible que [[QuickSort]]
- Base de TimSort (usado en Python y Java)
