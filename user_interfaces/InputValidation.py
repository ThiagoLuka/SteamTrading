

class InputValidation:

    @staticmethod
    def int_within_range(lesser, greater, text_to_show: str = '') -> int:
        user_input = 0
        invalid = True
        error_message = f'Please enter a value between {lesser} and {greater}.'
        while invalid:
            try:
                user_input = int(input(text_to_show))
                if user_input not in range(lesser, greater + 1):
                    print(f'Value out of range. {error_message}')
                else:
                    invalid = False
            except ValueError:
                print(f'Non numeric input. {error_message}')
        return user_input

    @staticmethod
    def yes_or_no(text_to_show: str = '') -> bool:
        user_input = False
        invalid = True
        error_message = 'Please enter "y" for yes or "n" for no.\n'
        while invalid:
            try:
                user_input = str(input(text_to_show))
                if user_input == 'y':
                    user_input = True
                    invalid = False
                elif user_input == 'n':
                    user_input = False
                    invalid = False
                else:
                    invalid = False
                    print(f'Invalid input. {error_message}')
            except ValueError:
                print(f'Invalid input. {error_message}')
        return user_input
