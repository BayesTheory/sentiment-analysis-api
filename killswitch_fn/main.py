import base64
import json
import os

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import billing_v1


billing_client = billing_v1.CloudBillingClient()

PROJECT_ID = os.environ["GCP_PROJECT"]
PROJECT_NAME = f"projects/{PROJECT_ID}"


@functions_framework.cloud_event
def stop_billing(cloud_event: CloudEvent):
    msg_b64 = cloud_event.data["message"]["data"]
    event = json.loads(base64.b64decode(msg_b64).decode("utf-8"))

    cost = float(event["costAmount"])
    budget = float(event["budgetAmount"])

    if cost < budget:
        return "No action"

    # Desativar billing: billingAccountName vazio
    billing_client.update_project_billing_info(
        name=PROJECT_NAME,
        project_billing_info=billing_v1.ProjectBillingInfo(billing_account_name=""),
    )
    return "Billing disabled"
