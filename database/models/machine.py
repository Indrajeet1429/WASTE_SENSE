from datetime import datetime, timezone

from sqlalchemy import BigInteger, Integer, CheckConstraint, DateTime, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Machine(Base):
    __tablename__ = "machines"

    machine_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    machine_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    cpu_capacity: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    memory_capacity: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workloads = relationship(
        "Workload",
        back_populates="machine",
    )

    resource_measurements = relationship(
        "ResourceMeasurement",
        back_populates="machine",
    )

    waste_events = relationship(
        "WasteEvent",
        back_populates="machine",
    )

    __table_args__ = (
        CheckConstraint(
            "cpu_capacity > 0",
            name="ck_machines_cpu_capacity_positive",
        ),
        CheckConstraint(
            "memory_capacity > 0",
            name="ck_machines_memory_capacity_positive",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'maintenance')",
            name="ck_machines_status",
        ),
    )
