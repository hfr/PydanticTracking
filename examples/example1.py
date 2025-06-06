from pydantic_tracking.mixin import TrackingMixin
from pydantic import BaseModel
from typing import List

class MyModel(TrackingMixin, BaseModel):
    tags: List[int] = []

m = MyModel(tags=[1])
m.tags.append(2)

print(m.is_dirty())            # True
print(m.dirty_fields())        # ['tags']
m.save()
print(m.is_dirty())            # False

