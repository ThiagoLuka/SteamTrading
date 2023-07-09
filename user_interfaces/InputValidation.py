

class InputValidation:

    @staticmethod
    def int_within_range(lesser, greater, text_to_show: str = '', allow_out_of_range: bool = True) -> int:
        user_input = 0
        invalid = True
        error_message = f'Please enter a numeric value between {lesser} and {greater}.'
        allow_out_of_range_message = 'This value is out of the pre established range. ' \
                                     'Are you sure you want to continue with it?'
        while invalid:
            try:
                user_input = int(input(text_to_show))
                if user_input not in range(lesser, greater + 1):
                    if allow_out_of_range:
                        if InputValidation.yes_or_no(allow_out_of_range_message):
                            invalid = False
                        else:
                            print(error_message)
                    else:
                        print(f'Value out of range. {error_message}')
                else:
                    invalid = False
            except ValueError:
                print(f'Non numeric input. Please enter a numeric value between {lesser} and {greater}.')
        return user_input

    @staticmethod
    def yes_or_no(text_to_show: str = '') -> bool:
        user_input = False
        invalid = True
        error_message = 'Please enter "y" for yes or "n" for no.'
        while invalid:
            try:
                user_input = str(input(f'{text_to_show} (y/n) '))
                if user_input == 'y':
                    user_input = True
                    invalid = False
                elif user_input == 'n':
                    user_input = False
                    invalid = False
                else:
                    print(f'Invalid input. {error_message}')
            except ValueError:
                print(f'Invalid input. {error_message}')
        return user_input
