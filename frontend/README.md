# WasteSense frontend (React + Vite)

Monitoring and intelligence UI for WasteSense. React 18, React Router 6, Vite. No chart or UI libraries.

## Run
Create an account on the sign in screen, then explore the app.
```bash
cd frontend
npm install
cp .env.example .env     # VITE_USE_MOCK=true uses sample data
npm run dev              # http://localhost:5173
npm run build            # production build in dist/
```

## Structure
```
src/
  main.jsx, App.jsx            entry and routes only
  pages/                       one file per screen
    Dashboard, Machines, MachineDetails, Trends        Member 3 (monitoring)
    WasteEvents, WasteDetails, Replay, Optimization, Savings   Member 4 (intelligence)
    Alerts                     listed under both members in the brief: agree one owner
    Landing, Login, NotFound   shared
  components/
    common/   Logo, Icon, Badge, Panel, PageHeader, Note, DataState, AppLayout, ProtectedRoute
    cards/    StatCard, CaseSection, Fingerprint, BigNumbers
    charts/   LineChart, BarChart, ExpectedActual, Meter, ChartLegend
    tables/   DataTable
    alerts/   AlertSummary, AlertTable
  hooks/      useApi, useAuth, useTheme
  services/   api.js (HTTP client), wastesenseService.js (all data calls), mockData.js, authService.js
  styles/     global.css (tokens), landing.css, app.css
  utils/      format.js, constants.js
```

## Connect FastAPI
1. `cp .env.example .env` (defaults: `VITE_USE_MOCK=false`, `VITE_API_BASE_URL=` empty). Set `VITE_USE_MOCK=true` for sample data.
2. Start the backend on `http://127.0.0.1:8000`. The dev server proxies `/api` to it (`VITE_PROXY_TARGET`). To call it directly instead, set `VITE_API_BASE_URL=http://127.0.0.1:8000` (backend CORS must allow the origin).
3. Layers: `src/api/` (apiClient + one module per resource, matching the integration spec) -> `src/services/adapters.js` (maps API responses to page shapes) -> `src/services/wastesenseService.js` (only file pages import). Pages are unchanged.
4. Assumptions to confirm with backend/ML: measurement CPU/memory are treated as % and power as W; waste `confidence` 0-1 is shown as %; machine status `inactive`/`maintenance` shows as offline; memory replay values and contributing factors are not in the API so those parts are hidden/empty; alerts get `machine_id` via their waste event.
