from infrastructure.fakes.task_queue import FakeTaskQueue


async def test_encolar_registers_the_task_and_returns_a_job_id() -> None:
    queue = FakeTaskQueue()

    job_id = await queue.encolar("recalcular_proyeccion", {"suministro_id": "S1"})

    assert job_id
    assert queue.tareas_encoladas == [("recalcular_proyeccion", {"suministro_id": "S1"})]


async def test_each_call_returns_a_different_job_id() -> None:
    queue = FakeTaskQueue()

    job_id_1 = await queue.encolar("tarea_a", {})
    job_id_2 = await queue.encolar("tarea_b", {})

    assert job_id_1 != job_id_2
