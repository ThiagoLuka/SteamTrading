

class InputValidation:

    @staticmethod
    def int_within_range(menor, maior, text_to_show: str = '') -> int:
        a = 0
        invalid = True
        while invalid:
            try:
                a = int(input(text_to_show))
                if a not in range(menor, maior+1):
                    print(f'Valor fora do intervalo. Entre com o valor entre {menor} e {maior}: ')
                else:
                    invalid = False
            except ValueError as e:
                print('Entrada não numérica.')
        return a

    @staticmethod
    def continuar() -> bool:
        a = False
        invalid = True
        while invalid:
            try:
                a = str(input('Continuar nesse menu? (y/n) '))
                if a == 'y':
                    a = True
                    invalid = False
                elif a == 'n':
                    a = False
                    invalid = False
                else:
                    invalid = False
                    print('Entrada inválida.')
            except ValueError as e:
                print('Entrada inválida.')
        return a

