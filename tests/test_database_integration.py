from datetime import datetime, timezone
from uuid import uuid4

from database.models import Machine, Workload, ResourceMeasurement, WasteEvent
from database.session import SessionLocal


def test_database_relationship_flow():
    db = SessionLocal()

    machine = None

    try:
        machine = Machine(
            machine_name=f"test-machine-{uuid4().hex[:8]}",
            cpu_capacity=100.0,
            memory_capacity=64.0,
            status="active",
        )
        db.add(machine)
        db.flush()

        workload = Workload(
            machine_id=machine.machine_id,
            workload_type="batch_processing",
            priority="normal",
            start_time=datetime.now(timezone.utc),
            active_tasks=5,
        )
        db.add(workload)
        db.flush()

        measurement = ResourceMeasurement(
            machine_id=machine.machine_id,
            workload_id=workload.workload_id,
            timestamp=datetime.now(timezone.utc),
            actual_cpu=75.0,
            actual_memory=40.0,
            actual_power=120.0,
        )
        db.add(measurement)

        waste_event = WasteEvent(
            machine_id=machine.machine_id,
            workload_id=workload.workload_id,
            timestamp=datetime.now(timezone.utc),
            waste_score=82.5,
            severity="high",
            waste_type="excess_cpu",
            confidence=0.94,
            persistent=True,
        )
        db.add(waste_event)

        db.commit()

        assert machine.machine_id is not None
        assert workload.workload_id is not None
        assert measurement.measurement_id is not None
        assert waste_event.waste_id is not None

    finally:
        if machine is not None and machine.machine_id is not None:
            db.rollback()

        db.close()