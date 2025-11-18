---
cards-deck: Algoritmos
status: completo
tipo_nota: concepto
created: 2025-01-15
---

# QuickSort

QuickSort es un algoritmo de **ordenamiento por división** (divide and conquer) extremadamente eficiente.

## Concepto Principal

El algoritmo funciona seleccionando un elemento como "pivote" y particionando el array de forma que:
- Elementos menores al pivote quedan a la izquierda
- Elementos mayores al pivote quedan a la derecha
- Luego se aplica recursivamente a ambas particiones

## Complejidad

- **Caso promedio**: O(n log n)
- **Peor caso**: O(n²) - cuando el array ya está ordenado
- **Espacio**: O(log n) por la recursión

## Ventajas

- Muy rápido en la práctica
- Ordenamiento in-place (no requiere espacio adicional significativo)
- Cache-friendly por su acceso secuencial

## Implementación Python

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quicksort(left) + middle + quicksort(right)
```

## Relaciones

- Similar a [[MergeSort]] en enfoque divide y conquista
- Más rápido que [[BubbleSort]] en arrays grandes
- Usado en muchas librerías estándar como base del sort()

## Casos de Uso

- Ordenamiento de arrays grandes
- Cuando el espacio es limitado (in-place)
- Aplicaciones donde el caso promedio importa más que el peor caso
