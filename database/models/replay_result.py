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


class ReplayResult(Base):
    __tablename__ = "replay_results"

    replay_id: Mapped[int] = mapped_column(
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

    actual_cpu: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    expected_cpu: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    actual_power: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    expected_power: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    estimated_saving: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    waste_event = relationship(
        "WasteEvent",
        back_populates="replay_result",
    )

    __table_args__ = (
        CheckConstraint(
            "actual_cpu >= 0",
            name="ck_replay_actual_cpu_non_negative",
        ),
        CheckConstraint(
            "expected_cpu >= 0",
            name="ck_replay_expected_cpu_non_negative",
        ),
        CheckConstraint(
            "actual_power >= 0",
            name="ck_replay_actual_power_non_negative",
        ),
        CheckConstraint(
            "expected_power >= 0",
            name="ck_replay_expected_power_non_negative",
        ),
        CheckConstraint(
            "estimated_saving >= 0",
            name="ck_replay_estimated_saving_non_negative",
        ),
    )
