from user_interfaces.InputValidation import InputValidation


class GenericUI:

    @staticmethod
    def not_implemented() -> None:
        print('Not implemented')

    @staticmethod
    def continuar() -> bool:
        return InputValidation.continuar()

    @staticmethod
    def get_string(text_to_show: str) -> str:
        return str(input(text_to_show))

    @staticmethod
    def progress_completed(progress: int, total: int, text: str = '') -> None:
        percentage_progress = progress / total
        end = ''
        if percentage_progress == 1:
            end = '\n'
        if text:
            print(f'\r{percentage_progress * 100:^7.2f}%  -  {text}', end=end, flush=True)
        else:
            print(f'\r{percentage_progress * 100:^7.2f}%', end=end, flush=True)
