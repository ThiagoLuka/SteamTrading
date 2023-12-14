
class MathUtils:

    @staticmethod
    def highest_triangular_number_and_nth_term_below(ceiling: int) -> (int, int):
        triangular_number, nth = 0, 0
        previous_number, previous_nth = triangular_number, nth
        while ceiling > triangular_number:
            previous_number, previous_nth = triangular_number, nth
            nth += 1
            triangular_number += nth
        return previous_number, previous_nth

    @staticmethod
    def triangular_number_given_nth_term(nth: int) -> int:
        triangular_number = 0
        for i in range(0, nth + 1):
            triangular_number += i
        return triangular_number
