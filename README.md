# Fraud Detection API and Frontend

This project already contains a trained scikit-learn model at
`artifacts/models/fraud_detection_model.joblib`. The API loads that artifact and
the selected decision threshold from `artifacts/reports/threshold_tuning.csv`
when it starts. The threshold is selected from the existing tuning report by
maximum F1 score (0.90 in the current report).

## Run the backend

From the project root, run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8001
```

The API is available at `http://127.0.0.1:8001`. Open
`http://127.0.0.1:8001/docs` to try the endpoints in Swagger UI.

## Run the frontend

In a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. The frontend calls
`http://127.0.0.1:8001/api/v1` by default. To run FastAPI on port 8000 or another
port, set `VITE_API_BASE_URL` to that API's `/api/v1` URL before starting Vite.

## Dashboard sections

- **Dashboard:** full-dataset PaySim totals and fraud mix, fraud rates by type,
  and saved holdout test metrics.
- **Fraud Alerts:** a clearly labeled demo queue with probability-based risk
  levels, search and filters, and in-session review/resolution controls. The
  backend currently has no alert-history or alert-status persistence endpoint;
  demo records are not model predictions.
- **Predict Fraud:** submits a transaction to the loaded model through
  `POST /api/v1/predict`.
- **Transactions:** searches and filters the real labeled holdout split at
  `GET /api/v1/transactions`. These are data labels, not model predictions or
  newly processed live transactions.
- **Analytics:** reads the saved test evaluation and confusion matrix from
  `GET /api/v1/analytics`.
- **Model Monitoring:** reads API health, model/threshold availability, the
  latest completed MLflow validation run, and training-versus-test feature PSI
  comparison from `GET /api/v1/monitoring`. The PSI view is a dataset consistency
  check—not live production drift monitoring, which is not configured.

The transactions endpoint scans the compressed holdout CSV to apply search and
filters. It returns page-sized responses and may take longer than the artifact
summary endpoints.

## Fraud alert demo

The Fraud Alerts page uses illustrative sample records because the API currently
does not expose alert history or status updates. Its review and resolution
statuses are saved in the browser tab's session storage so they remain while
navigating between sections or refreshing the page. They are not sent to FastAPI
and reset when the tab is closed; this is not backend alert-history persistence.

Risk bands use fraud probability, independently from the model's prediction
decision threshold. Defaults are medium at `0.30` and high at `0.70`. To
customize them, set these optional variables in `frontend/.env.local` before
starting Vite, then restart the frontend:

```env
VITE_ALERT_MEDIUM_RISK_THRESHOLD=0.30
VITE_ALERT_HIGH_RISK_THRESHOLD=0.70
```

Both values must be between `0` and `1`, and the high-risk threshold must be
greater than the medium-risk threshold.

## Currency display

The frontend formats displayed transaction amounts and balances in Indian
rupees using the `en-IN` locale. This changes presentation only: numeric values
sent to the prediction API and amounts returned by the backend are not
converted.

## Prediction request

`POST /api/v1/predict` accepts the `step`, `amount`, transaction type, and
origin/destination balance values used by this project's training features.
The request schema and its example are also shown in Swagger. For example:

```json
{
  "step": 1,
  "amount": 9839.64,
  "transaction_type": "PAYMENT",
  "old_balance_origin": 170136.0,
  "new_balance_origin": 160296.36,
  "old_balance_destination": 0.0,
  "new_balance_destination": 0.0
}
```

The response includes the binary prediction (`0` legitimate, `1` fraud), the
fraud probability, and the threshold used. Values must be non-negative and
transaction types must match one of the categories supported by the trained
model. Unknown fields and non-finite numbers are rejected with HTTP 422."# Fraud_detection_project" 
