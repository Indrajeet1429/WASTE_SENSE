from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class WasteEvent(Base):
    __tablename__ = "waste_events"

    waste_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    machine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("machines.machine_id"),
        nullable=False,
        index=True,
    )

    workload_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workloads.workload_id"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    waste_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    waste_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    persistent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    machine = relationship(
        "Machine",
        back_populates="waste_events",
    )

    workload = relationship(
        "Workload",
        back_populates="waste_events",
    )

    alerts = relationship(
        "Alert",
        back_populates="waste_event",
    )

    savings = relationship(
        "Saving",
        back_populates="waste_event",
        uselist=False,
    )

    replay_result = relationship(
        "ReplayResult",
        back_populates="waste_event",
        uselist=False,
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="waste_event",
    )

    __table_args__ = (
        CheckConstraint(
            "waste_score >= 0 AND waste_score <= 100",
            name="ck_waste_events_score_range",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_waste_events_confidence_range",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_waste_events_severity",
        ),
    )
