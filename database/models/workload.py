from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Workload(Base):
    __tablename__ = "workloads"

    workload_id: Mapped[int] = mapped_column(
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

    workload_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal",
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    active_tasks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    machine = relationship(
        "Machine",
        back_populates="workloads",
    )

    resource_measurements = relationship(
        "ResourceMeasurement",
        back_populates="workload",
    )

    waste_events = relationship(
        "WasteEvent",
        back_populates="workload",
    )

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'critical')",
            name="ck_workloads_priority",
        ),
        CheckConstraint(
            "active_tasks >= 0",
            name="ck_workloads_active_tasks_non_negative",
        ),
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time",
            name="ck_workloads_valid_time_range",
        ),
    )
