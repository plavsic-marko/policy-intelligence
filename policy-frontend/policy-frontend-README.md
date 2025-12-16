# Policy Frontend Webapp

This project is a **web application UI** for querying and exploring policy-related content
stored in the **PolicyChunksUnified** dataset.

The application is **React-based**, written in **TypeScript**, and uses:
- Zustand for state management
- React Router for navigation
- Tailwind CSS for styling

The app is designed as a **simple, lightweight interface** that communicates directly
with an **n8n webhook**, which handles retrieval logic and data access.

The frontend itself contains **no backend logic**.

---

## How to start

In the project directory (`policy-frontend`), you can run:

### `npm start`

Runs the app in development mode.  
Open http://localhost:3000 to view it in your browser.

The page will reload automatically when you make changes.  
You may also see lint warnings or errors in the console.

---

### `npm run build`

Builds the app for production into the `build` folder.

The build:
- bundles React in production mode
- optimizes assets for best performance
- generates hashed filenames for caching

The output is ready to be deployed on any static hosting or web server.

---

## Environment configuration

The app requires a single environment variable.

Create a `.env` file based on the example:

```bash
cp .env.example .env
```

### Required variable
```env
REACT_APP_N8N_WORKFLOW_URL=https://<n8n-webhook-url>
```

This URL points to an **n8n webhook** responsible for handling queries and returning results.

> Note: React environment variables are exposed in the browser.
> The webhook is therefore expected to be **read-only**.

---

## Deployment

The application is deployed as a **static frontend**.

Typical deployment flow:
1. Build the app using `npm run build`
2. Serve the `build/` folder via:
   - Nginx / Apache
   - Cloud hosting (e.g. Vercel, Netlify)
   - Internal infrastructure

CI/CD setup depends on the target environment and is handled separately.

---

## Tech stack

- React
- TypeScript
- Zustand
- React Router
- Tailwind CSS
- Create React App

---

## Author

Marko Plavšić
