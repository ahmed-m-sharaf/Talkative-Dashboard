from core import REGISTRY, Intent


class Dispatcher:

    @staticmethod
    def dispatch(
        intent: Intent,
        parameters: dict,
    ):

        handler = REGISTRY.get(intent)

        if handler is None:
            raise ValueError(f"Unsupported intent: {intent}")

        return handler(**parameters)