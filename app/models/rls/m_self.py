from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from __main__ import Person  # forward reference for type hints

class ParentChild(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(nullable=False)

    parent_id: UUID = Field(foreign_key="person.id", nullable=False)
    child_id: UUID = Field(foreign_key="person.id", nullable=False)


class Person(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(nullable=False)
    name: str
    person_type: str

    children: List["Person"] = Relationship(
        back_populates="parents",
        link_model=ParentChild,
        sa_relationship_kwargs={
            "primaryjoin": "Person.id==ParentChild.parent_id",
            "secondaryjoin": "Person.id==ParentChild.child_id",
            # foreign_keys must reference columns directly, not Fields
            "foreign_keys": [ParentChild.__table__.c.parent_id, ParentChild.__table__.c.child_id],
        },
    )

    parents: List["Person"] = Relationship(
        back_populates="children",
        link_model=ParentChild,
        sa_relationship_kwargs={
            "primaryjoin": "Person.id==ParentChild.child_id",
            "secondaryjoin": "Person.id==ParentChild.parent_id",
            "foreign_keys": [ParentChild.__table__.c.parent_id, ParentChild.__table__.c.child_id],
        },
    )
