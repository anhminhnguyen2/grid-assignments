# Deploying to Vercel

The app deploys as one Vercel project: the **React frontend** is served as a
static build and the **FastAPI backend** runs as a Python serverless function
under `/api`. The grid CSV lives in **Vercel Blob** so reassignments are durable
and shared — a change one viewer makes is seen by the next.

```
Browser ──► Vercel (static frontend  ──/api──►  Python function = FastAPI)
                                                      │ read / write
                                                      ▼
                                              Vercel Blob (grid_assignments.csv)
```

## One-time setup

1. **Install the CLI and log in**
   ```bash
   npm i -g vercel
   vercel login
   vercel link          # link this folder to a Vercel project
   ```

2. **Create a Blob store** — Vercel dashboard → **Storage** → **Create** →
   **Blob**. **Use Public access** (the Python REST API can't upload to a
   private store). Connect the store to your project and tick
   "Add a read-write token env var to this connection" so
   `BLOB_READ_WRITE_TOKEN` lands in the project's env vars.

3. **Seed the CSV into Blob** (uploads `data/grid_assignments.csv`):
   ```bash
   .venv/bin/python scripts/seed_blob.py
   ```
   The token is read from your local `.env` (set `BLOB_READ_WRITE_TOKEN=...`
   there). The script verifies the round-trip and prints the blob URL.

4. **Set Environment Variables** (dashboard → Settings → Environment Variables,
   or `vercel env add NAME`):

   | Variable | Value |
   |---|---|
   | `DATA_BACKEND` | `blob` |
   | `BLOB_READ_WRITE_TOKEN` | auto-injected when the Blob store is connected to the project (or add it by hand with "Sensitive" checked) |

   `BLOB_CSV_URL` is **not required** — the backend discovers the newest blob
   via the Vercel Blob `list` API.

## Alternative: save edits straight to the CSV in GitHub

Instead of Blob, the deployed app can commit every reassignment to
`data/grid_assignments.csv` in this repository (`backend/github_store.py`). A
Vercel function can't write to its own files, so it goes through the GitHub API.

1. Create a **fine-grained personal access token** (GitHub → Settings →
   Developer settings → Fine-grained tokens) limited to this repository with
   **Contents: Read and write**.
2. In Vercel → Settings → Environment Variables set:

   | Variable | Value |
   |---|---|
   | `DATA_BACKEND` | `github` |
   | `GITHUB_TOKEN` | the token (tick "Sensitive") |
   | `GITHUB_REPO` | optional, `owner/name`; defaults to the repo Vercel deploys from |
   | `GITHUB_BRANCH` | optional, defaults to `main` |

3. Redeploy. `GET /api/health` → `{"status":"ok","db":"github"}`.

What to expect:

- Each save is one commit on `main`, e.g. `Reassign ab_mtr_1 to LB (2026_04_23)
  [skip ci]`, authored by the token's owner. `[skip ci]` skips GitHub Actions,
  and `ignoreCommand` in `vercel.json` skips the Vercel rebuild for commits that
  only touch `data/`.
- Run `git pull` before working locally — `main` moves whenever someone saves.
- If two people save at the same moment, the second save is re-applied on top
  of the first rather than overwriting it.
- The edits already made in Blob are **not** in the repo's CSV. Download the
  current blob and commit it over `data/grid_assignments.csv` before switching,
  or those edits are left behind.
- A branch protection rule that requires pull requests on `main` will reject
  these commits.

## Deploy

```bash
vercel          # preview deployment
vercel --prod   # production deployment
```
(Or connect the Git repo in the dashboard for automatic deploys on push.)

## Verify the live deployment

- `GET https://<app>.vercel.app/api/health` → `{"status":"ok","db":"blob"}`
- Open the site → both tabs load, scenarios populate, charts render.
- Reassign a meter, reload in a **different** browser/session → the change is
  still there (durable + shared via Blob).

## Notes

- **Local dev is unchanged:** `DATA_BACKEND=csv` reads/writes the on-disk CSV.
  Only Vercel uses `blob`.
- **Consistency:** each write creates a **new immutable blob** (random suffix),
  and reads discover the newest via `list`. Unique URLs are never CDN-stale, so
  the next viewer always sees a write. Old versions are deleted best-effort.
  Concurrent writes are last-write-wins.
- **Data exposure:** the Blob is public-readable by URL (the data is OK to
  share). If you want only invited viewers to see the app itself, enable
  Vercel's **Deployment Protection** (Settings → Deployment Protection).
- The 6.4 MB CSV is **not** bundled into the deploy (`.vercelignore` excludes
  `data/`); the function reads it from Blob.
