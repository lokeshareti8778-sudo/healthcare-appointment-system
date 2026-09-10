# Healthcare Appointment System

Production-oriented Flask healthcare appointment management for patients, doctors, and administrators. It uses PostgreSQL, SQLAlchemy, Flask-Migrate, Flask-Login, Bootstrap 5, an Azure Function HTTP trigger, and GitHub Actions deployment to Azure without Docker.

## Features

- Patient registration, login, doctor directory, protected booking, history, and prescriptions.
- Doctor portal for appointment review, status updates, and prescriptions.
- Admin portal for doctor lifecycle management and operational reporting.
- JSON endpoints for health, doctors, and authenticated appointment data.
- Azure Function that generates appointment IDs, queue tokens, fees, and confirmation status.

## Local setup

Prerequisites: Python 3.12, PostgreSQL 14+, and optionally Azure Functions Core Tools for the function app.

```powershell
cd webapp
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with a real SECRET_KEY and PostgreSQL DATABASE_URL
flask --app app:create_app db upgrade
flask --app app:create_app run --debug
```

On a fresh checkout, initialize migrations before upgrading: `flask --app app:create_app db init`, then `flask --app app:create_app db migrate -m "initial schema"` and `flask --app app:create_app db upgrade`. For an initial database without migrations, run `database/schema.sql` against PostgreSQL instead. To create later migrations, run `flask --app app:create_app db migrate -m "describe change"` followed by `flask --app app:create_app db upgrade`.

The web app expects `AZURE_FUNCTION_URL` to point to the deployed Function endpoint and optionally uses `AZURE_FUNCTION_KEY`. Without it, bookings fail closed rather than creating records without an appointment ID.

## Azure deployment

Create an Azure App Service using Python 3.12 and configure these application settings: `SECRET_KEY`, `DATABASE_URL`, `AZURE_FUNCTION_URL`, `AZURE_FUNCTION_KEY`, and `APPOINTMENT_FEE`. Set the App Service startup command to `gunicorn --chdir webapp app:app` or configure the working directory as `webapp` and use `gunicorn app:app`.

Create a Python 3.12 Azure Function App, configure its publish profile as a GitHub secret, and deploy `functionapp/`. The workflow secrets are `AZURE_WEBAPP_NAME`, `AZURE_WEBAPP_PUBLISH_PROFILE`, `AZURE_FUNCTIONAPP_NAME`, and `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`.

For local Functions testing:

```powershell
cd functionapp
pip install -r requirements.txt
func start
```

## Security notes

Keep `.env` and `local.settings.json` out of source control. Use HTTPS, a managed PostgreSQL identity or secret store, restrictive CORS at the hosting layer, database backups, Application Insights, and rotated Azure publish profiles in production. Flask-WTF CSRF protection is enabled for browser forms, passwords are hashed, and role checks are enforced server-side.
