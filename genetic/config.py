"""
    POP_SIZE - wielkość populacji
    NEW_POP_SIZE - ilość losowo generowanych osobników co iterację

    CPB - prawdopodobieństwo zajścia krzyżowania dla danej pary
    GSPB - prawdopodobieństwo zamiany genu
    MPB - prawdopodobieństwo mutacji osobnika
    CPPB - prawdopodobieństow podmiany ścieżki w subgenie

    GA_ITERATIONS - ilość iteracji
"""

POP_SIZE = 100
NEW_POP_SIZE = 10

CPB = 80
GSPB = 20  # Gene swap probability
MPB = 50
CPPB = 1  # Change path probability

GA_ITERATIONS = 1