import json


class JSONWriter:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def write(self, data: list[dict[str, any]]) -> None:
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
