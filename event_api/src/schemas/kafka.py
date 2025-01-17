import json
from typing import Any

from pydantic import BaseModel


class KafkaMessage(BaseModel):
    key: str | bytes | None
    value: str | bytes | dict

    def model_post_init(self, __context: Any) -> None:
        if isinstance(self.key, str):
            self.key = self.key.encode("utf-8")
        if isinstance(self.value, str):
            self.value = self.value.encode("utf-8")
        elif isinstance(self.value, dict):
            self.value = json.dumps(self.value).encode("utf-8")
