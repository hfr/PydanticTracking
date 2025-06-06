from pydantic_tracking.mixin import TrackingMixin
from pydantic import BaseModel, Field
from typing import List

class MyModel(TrackingMixin, BaseModel):
    tags: List[int] = Field(default_factory=list)

def test_list_tracking():
    model = MyModel(tags=[1])
    model.tags.append(2)
    assert model.is_dirty()
    assert "tags" in model.dirty_fields()
