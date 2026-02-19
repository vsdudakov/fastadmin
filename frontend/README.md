# FastAdmin Frontend

React-based admin dashboard UI for [FastAdmin](https://github.com/vsdudakov/fastadmin). It provides sign-in, dashboard, list/add/change views, and configurable widgets backed by the FastAdmin API.

## Table of contents

- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project structure](#project-structure)
- [Commands](#commands)
- [How to run](#how-to-run)
- [Environment variables](#environment-variables)
- [Testing](#testing)
- [Linting and formatting](#linting-and-formatting)
- [Path alias](#path-alias)

## Tech stack

- **React 19** + **TypeScript**
- **Vite** (build & dev server)
- **Ant Design** (UI components)
- **TanStack Query** (data fetching)
- **React Router** (routing)
- **i18next** (i18n)
- **Vitest** + **Testing Library** (tests)
- **ESLint** + **Biome** (lint & format)

## Prerequisites

- Node.js 18+
- Yarn (or npm/pnpm)

## Project structure

```
src/
├── main.tsx                 # Entry point, providers, root render
├── index.css                # Global styles & design tokens
├── vite-env.d.ts            # Type declarations (e.g. Window)
├── test-setup.ts            # Vitest setup (e.g. ResizeObserver mock)
│
├── constants/
│   └── routes.ts            # Route paths & helpers
│
├── containers/              # Page-level components (routes)
│   ├── app/                 # App shell, ConfigProvider, Routes
│   ├── sign-in/
│   ├── index/               # Dashboard
│   ├── list/                # List view with filters, actions
│   ├── add/                 # Add form
│   └── change/              # Edit form
│
├── components/              # Reusable UI
│   ├── crud-container/      # Layout: header, sidebar, content card
│   ├── sign-in-container/
│   ├── form-container/      # Dynamic forms from config
│   ├── table-or-cards/      # List as table or cards (mobile)
│   ├── filter-column/
│   ├── dashboard-widget/    # Charts & dashboard blocks
│   ├── async-select/        # FK / autocomplete
│   ├── async-transfer/      # M2M picker
│   ├── upload-input/        # File/image upload
│   ├── password-input/     # Password with change modal
│   ├── slug-input/
│   ├── phone-number-input/
│   ├── json-textarea/
│   ├── texteditor-field/   # Rich text (Quill)
│   └── export-btn/
│
├── providers/
│   ├── ConfigurationProvider/   # App config from API
│   └── SignInUserProvider/       # Auth state
│
├── fetchers/
│   └── fetchers.ts         # API client (axios)
│
├── hooks/
│   ├── useTableQuery.ts    # List pagination, filters, sort
│   ├── useTableColumns.tsx
│   └── useIsMobile.ts
│
├── helpers/
│   ├── configuration.ts
│   ├── forms.ts            # Error handling, form helpers
│   ├── title.ts
│   ├── transform.tsx       # Server ↔ client data transform
│   └── widgets.ts          # Widget registry
│
└── interfaces/
    ├── configuration.ts   # API/config types
    └── user.ts
```

## Commands

| Command           | Description                          |
|-------------------|--------------------------------------|
| `yarn`            | Install dependencies                 |
| `yarn dev`        | Start dev server (Vite, default port)  |
| `yarn build`      | Type-check + production build        |
| `yarn preview`    | Preview production build             |
| `yarn test`       | Run tests (Vitest)                   |
| `yarn coverage`   | Run tests with coverage              |
| `yarn lint`       | Run ESLint                           |
| `yarn biome-check`| Run Biome (format + lint, with fix)  |

## How to run

### Development

1. Install dependencies:
   ```bash
   yarn
   ```

2. Ensure the FastAdmin backend is running and exposes the API (e.g. CORS, `/configuration`, `/sign-in`, etc.).

3. Set environment variables (see below), then start the dev server:
   ```bash
   yarn dev
   ```
   Open the URL shown (e.g. `http://localhost:5173`).

### Production build

The build outputs to the parent package’s static folder (`../fastadmin/static/`) as UMD:

- `index.min.js`
- `index.min.css`
- `chunk.min.js`

```bash
yarn build
```

Serve the backend as usual; it will serve these static assets for the admin UI.

## Environment variables

The app uses [vite-plugin-environment](https://www.npmjs.com/package/vite-plugin-environment) with no prefix. Environment variables are exposed on `import.meta.env` and, where used, on `window` in the built bundle.

Common variables (injected by the backend or at build/serve time):

| Variable         | Description                    |
|------------------|--------------------------------|
| `SERVER_URL`     | API base URL (e.g. `http://localhost:8000`) |
| `SERVER_DOMAIN`  | Public origin for assets/links (e.g. `http://localhost:8000`) |

For local dev, you can use a `.env` file in the frontend root or pass them when starting the dev server.

## Testing

- Tests live next to components (e.g. `index.test.tsx`).
- Run tests: `yarn test`.
- Run with coverage: `yarn coverage`.
- Test setup: `src/test-setup.ts` (e.g. ResizeObserver mock for jsdom).

## Linting and formatting

- **ESLint**: `yarn lint` (config in `eslint.config.mjs`).
- **Biome**: `yarn biome-check` (format and lint with auto-fix), `yarn biome-lint` (lint only). Config in `biome.json`.

## Path alias

- The `@/` alias resolves to `src/` (see `vite.config.ts` and `tsconfig.json`).
