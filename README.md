# Hive Copilot

This repository now keeps only the Python Hive Copilot app and the React-based Streamlit custom component that renders the UI.

## Current Status

- Streamlit is the app host.
- FastAPI provides the backend API surface.
- The UI is rendered by a local Streamlit custom component so the TSX design can stay intact.
- Data is still mock-first until you wire the real Hive and Hadoop services.

## New Project Layout

```text
hive_copilot/
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/config.py
│   │   ├── schemas/query.py
│   │   └── services/
│   │       ├── hms_service.py
│   │       ├── llm_service.py
│   │       └── hive_execution_service.py
│   ├── main.py
│   └── run_backend.py
├── frontend/
│   └── app.py
└── streamlit_components/
    └── yelp_tsx_component/
        └── yelp_tsx_component/
            ├── __init__.py
            └── frontend/
                ├── src/
                └── dist/
```

## Python Dependencies

Install the migration stack with:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The Streamlit Frontend

The frontend works in local mock mode by default.

```bash
streamlit run hive_copilot/frontend/app.py
```

What works now:

- chat flow
- schema sidebar
- quick query buttons
- SQL preview
- results table
- mock chart rendering
- dashboard widgets

## Run The FastAPI Stub Backend

If you want the frontend to call HTTP endpoints instead of local mocks, start the backend:

```bash
python3 hive_copilot/backend/run_backend.py
```

Then point the frontend to it:

```bash
export STREAMLIT_BACKEND_URL=http://127.0.0.1:8000
streamlit run hive_copilot/frontend/app.py
```

## API Contract

The mock backend already exposes the contract the frontend uses:

- `GET /health`
- `GET /api/schema`
- `POST /api/query`
- `GET /api/dashboard`

This is the contract to preserve when you swap in:

- Hive Metastore access in `hms_service.py`
- LLM prompt generation in `llm_service.py`
- real Hive query execution in `hive_execution_service.py`

## Notes

- `hive_copilot/frontend/app.py` is the only live Streamlit host file.
- The custom component bundle under `hive_copilot/streamlit_components/` is required to preserve the TSX UI design inside Streamlit.
- If you edit the component source, rebuild it from `hive_copilot/streamlit_components/yelp_tsx_component/yelp_tsx_component/frontend/`.
