
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class ResourceMeasurement(Base):
    __tablename__ = "resource_measurements"

    measurement_id: Mapped[int] = mapped_column(
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

    actual_cpu: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    actual_memory: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    actual_power: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    machine = relationship(
        "Machine",
        back_populates="resource_measurements",
    )

    workload = relationship(
        "Workload",
        back_populates="resource_measurements",
    )

    __table_args__ = (
        CheckConstraint(
            "actual_cpu >= 0",
            name="ck_resource_measurements_actual_cpu_non_negative",
        ),
        CheckConstraint(
            "actual_memory >= 0",
            name="ck_resource_measurements_actual_memory_non_negative",
        ),
        CheckConstraint(
            "actual_power >= 0",
            name="ck_resource_measurements_actual_power_non_negative",
        ),
        UniqueConstraint(
            "machine_id",
            "workload_id",
            "timestamp",
            name="uq_resource_measurements_machine_workload_timestamp",
        ),
    )

