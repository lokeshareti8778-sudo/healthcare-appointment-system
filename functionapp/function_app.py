import json
import logging
import secrets
from datetime import datetime, timezone

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="create-appointment", methods=[func.HttpMethod.POST])
def create_appointment(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        body = {}

    fee = body.get("fee", 800)
    try:
        fee = int(fee)
        if fee <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return func.HttpResponse(json.dumps({"error": "fee must be a positive integer"}), status_code=400, mimetype="application/json")

    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    appointment_id = f"APT{timestamp % 9000 + 1000}"
    response = {"appointmentId": appointment_id, "token": secrets.randbelow(90) + 10, "fee": fee, "status": "Confirmed"}
    logging.info("Created appointment token %s", response["token"])
    return func.HttpResponse(json.dumps(response), status_code=200, mimetype="application/json")
