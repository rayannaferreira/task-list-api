from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..db import db
from datetime import datetime
from typing import Optional


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    goal_id: Mapped[int | None] = mapped_column(ForeignKey("goal.id"), nullable=True)
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="tasks")

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None,
        }

        if self.goal_id is not None:
            task_dict["goal_id"] = self.goal_id

        return task_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"], description=data["description"], completed_at=None
        )
