from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Integer,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    waste_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("waste_events.waste_id"),
        nullable=False,
        index=True,
    )

    recommendation: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    resource: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    current_value: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    suggested_value: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    estimated_benefit: Mapped[float] = mapped_column(
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
        back_populates="recommendations",
    )

    __table_args__ = (
        CheckConstraint(
            "current_value >= 0",
            name="ck_recommendations_current_value_non_negative",
        ),
        CheckConstraint(
            "suggested_value >= 0",
            name="ck_recommendations_suggested_value_non_negative",
        ),
        CheckConstraint(
            "estimated_benefit >= 0",
            name="ck_recommendations_benefit_non_negative",
        ),
    )
