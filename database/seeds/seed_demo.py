from datetime import datetime, timedelta, timezone

from database.models import (
    Alert,
    Machine,
    Recommendation,
    ReplayResult,
    ResourceMeasurement,
    Saving,
    WasteEvent,
    Workload,
)
from database.session import SessionLocal


def seed_demo_data():
    db = SessionLocal()

    try:
        # Prevent duplicate demo data.
        existing_machine = (
            db.query(Machine)
            .filter(Machine.machine_name == "demo-linuxone-01")
            .first()
        )

        if existing_machine:
            print("Demo data already exists.")
            return

        now = datetime.now(timezone.utc)

        # ---------------------------------------------------------
        # Machine
        # ---------------------------------------------------------
        machine = Machine(
            machine_name="demo-linuxone-01",
            cpu_capacity=100.0,
            memory_capacity=256.0,
            status="active",
        )
        db.add(machine)
        db.flush()

        # ---------------------------------------------------------
        # Workload
        # ---------------------------------------------------------
        workload = Workload(
            machine_id=machine.machine_id,
            workload_type="batch_processing",
            priority="high",
            start_time=now - timedelta(hours=2),
            end_time=None,
            active_tasks=25,
        )
        db.add(workload)
        db.flush()

        # ---------------------------------------------------------
        # Resource measurements
        # ---------------------------------------------------------
        measurement_1 = ResourceMeasurement(
            machine_id=machine.machine_id,
            workload_id=workload.workload_id,
            timestamp=now - timedelta(minutes=10),
            actual_cpu=82.50,
            actual_memory=140.00,
            actual_power=185.00,
        )

        measurement_2 = ResourceMeasurement(
            machine_id=machine.machine_id,
            workload_id=workload.workload_id,
            timestamp=now - timedelta(minutes=5),
            actual_cpu=86.00,
            actual_memory=145.00,
            actual_power=192.00,
        )

        db.add_all([measurement_1, measurement_2])

        # ---------------------------------------------------------
        # Waste event
        # ---------------------------------------------------------
        waste_event = WasteEvent(
            machine_id=machine.machine_id,
            workload_id=workload.workload_id,
            timestamp=now - timedelta(minutes=5),
            waste_score=87.50,
            severity="high",
            waste_type="excess_cpu",
            confidence=0.94,
            persistent=True,
        )
        db.add(waste_event)
        db.flush()

        # ---------------------------------------------------------
        # Alert
        # ---------------------------------------------------------
        alert = Alert(
            waste_id=waste_event.waste_id,
            severity="high",
            message="Persistent excess CPU usage detected.",
            status="open",
        )
        db.add(alert)

        # ---------------------------------------------------------
        # Saving estimate
        # ---------------------------------------------------------
        saving = Saving(
            waste_id=waste_event.waste_id,
            cpu_saving=24.00,
            memory_saving=12.00,
            power_saving=38.00,
            cost_saving=4.75,
        )
        db.add(saving)

        # ---------------------------------------------------------
        # Waste Replay
        # ---------------------------------------------------------
        replay = ReplayResult(
            waste_id=waste_event.waste_id,
            actual_cpu=86.00,
            expected_cpu=62.00,
            actual_power=192.00,
            expected_power=154.00,
            estimated_saving=38.00,
        )
        db.add(replay)

        # ---------------------------------------------------------
        # Recommendation
        # ---------------------------------------------------------
        recommendation = Recommendation(
            waste_id=waste_event.waste_id,
            recommendation="Reduce CPU allocation during sustained low-demand periods.",
            resource="cpu",
            current_value=86.00,
            suggested_value=65.00,
            estimated_benefit=24.00,
        )
        db.add(recommendation)

        db.commit()

        print("Demo data seeded successfully.")
        print(f"Machine ID: {machine.machine_id}")
        print(f"Workload ID: {workload.workload_id}")
        print(f"Waste Event ID: {waste_event.waste_id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()