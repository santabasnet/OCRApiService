from dataclasses import dataclass
from typing import List
from dacite import from_dict

data = {
    "id": 124,
    "statuses": [
        {
            "status": [{"value": "to do"}],
            "orderindex": 0,
            "color": "#d3d3d3",
            "type": "open"
        }]
}


@dataclass
class Text:
    value: str


@dataclass
class StatusElement:
    status: List[Text]
    orderindex: int
    color: str
    type: str


@dataclass
class Root:
    id: int
    statuses: List[StatusElement]


lst: Root = from_dict(Root, data)
print(lst.statuses[0].status[0])
