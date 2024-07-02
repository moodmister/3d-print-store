import math
import re
import subprocess
import time

from celery import shared_task, Task
from celery.utils.log import logging

from celery.result import AsyncResult
from flask import Blueprint, render_template
from flask import request
import logging

from print3dstore.models import File, Material, Order, StlModel, db

from . import tasks

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

@bp.get("/result/<id>")
def result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }


@bp.post("/block")
def block() -> dict[str, object]:
    result = tasks.block.delay()
    return {"result_id": result.id}


@bp.post("/process")
def process() -> dict[str, object]:
    result = tasks.process.delay(total=request.form.get("total", type=int))
    return {"result_id": result.id}

@shared_task(ignore_result=False, autoretry_for=(Exception,))
def slice(file_path: str, material_id: int) -> dict:
    try:
        material = db.get_or_404(Material, material_id)
        file = db.session.execute(
            db.select(File).filter_by(full_path=file_path)
        ).scalar_one_or_none()

        if file is None:
            raise Exception(f"Error with passed {file_path=} is not found.")
        
        logger.debug(f"{file.full_path} found.")

        logger.info(f"Begin slicing file {file.full_path}...")
        run_command = subprocess.run(
            ["bash", "./print3dstore/slicer/prusa-slicer", "-g", file_path, "--load", "./print3dstore/slicer/general.ini", "--threads", "1"],
            capture_output=True
        )

        run_result = run_command.stdout.decode("utf-8")
        run_error = run_command.stderr.decode("utf-8")
        if run_result in (None, ""):
            raise Exception("Error slicing the requested file", run_error)

        gcode_path = re.search(r"Slicing result exported to (.+)", run_result, re.MULTILINE | re.IGNORECASE)

        if gcode_path is None:
            errors = []
            if "exceeds the maximum build volume height" in run_error:
                errors.append("This model cannot be printed, because it is too big. Try scaling it down.")

            if len(errors) > 0:
                file.stl_model.errors = " ".join(errors)
                file.stl_model.order.status = Order.Status.CANCELLED
                db.session.commit()
            raise Exception("Error with sliced file. Could not find result of slicing\n", f"Slicer error: {run_error}")

        logger.info(f"Gcode exported to {gcode_path.group(1)}. Looking for estimates")

        gcode_file = open(gcode_path.group(1), "r")
        gcode_contents = gcode_file.read()

        estimated_time_regex = re.search(r"estimated printing time \(normal mode\) = (.+)", gcode_contents, re.MULTILINE | re.IGNORECASE)
        filament_used_regex = re.search(r"total filament used \[g\] = (.+)", gcode_contents, re.MULTILINE | re.IGNORECASE)

        if estimated_time_regex is None:
            raise Exception("Error finding estimated time in gcode file")
        
        if filament_used_regex is None:
            raise Exception("Error finding filament cost in resulted gcode")

        estimated_time = estimated_time_regex.group(1)
        filament_used = filament_used_regex.group(1)

        gcode_file.close()

        hours = re.search(r"(\d+)h", estimated_time)
        minutes = re.search(r"(\d+)m", estimated_time)
        seconds = re.search(r"(\d+)s", estimated_time)
        estimated_hours = int(hours.group(1)) if hours else 0
        estimated_minutes = int(minutes.group(1)) if minutes else 0
        estimated_seconds = int(seconds.group(1)) if seconds else 0

        estimated_time_in_seconds = estimated_hours * 3600 + \
            estimated_minutes * 60 + \
                estimated_seconds

        file.stl_model.estimated_time = estimated_time_in_seconds
        file.stl_model.estimated_cost = math.ceil(estimated_time_in_seconds / 3600) * 150 +\
            math.ceil(float(filament_used)) * material.cost_per_gram

        db.session.commit()

        return dict(gcode_path=gcode_path.group(1), estimated_time=estimated_time)
    except Exception as exception:
        logger.error(exception)



@shared_task()
def block() -> None:
    time.sleep(5)


@shared_task(bind=True, ignore_result=False)
def process(self: Task, total: int) -> object:
    for i in range(total):
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": total})
        time.sleep(1)

    return {"current": total, "total": total}
