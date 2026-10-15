
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Integer,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Saving(Base):
    __tablename__ = "savings"

    saving_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    waste_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("waste_events.waste_id"),
        nullable=False,
        unique=True,
        index=True,
    )

    cpu_saving: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    memory_saving: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    power_saving: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    cost_saving: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    estimated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    waste_event = relationship(
        "WasteEvent",
        back_populates="savings",
    )

    __table_args__ = (
        CheckConstraint(
            "cpu_saving >= 0",
            name="ck_savings_cpu_non_negative",
        ),
        CheckConstraint(
            "memory_saving >= 0",
            name="ck_savings_memory_non_negative",
        ),
        CheckConstraint(
            "power_saving >= 0",
            name="ck_savings_power_non_negative",
        ),
        CheckConstraint(
            "cost_saving >= 0",
            name="ck_savings_cost_non_negative",
        ),
    )

