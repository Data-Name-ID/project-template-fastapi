from app.core.store import Store


class BaseAccessor:
    def __init__(self, store: Store) -> None:
        self.store = store
