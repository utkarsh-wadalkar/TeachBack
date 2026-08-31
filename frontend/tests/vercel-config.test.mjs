import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("Vercel routes API requests to the Python entrypoint", async () => {
  const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));

  assert.deepEqual(config.rewrites[0], { source: "/api/(.*)", destination: "/api/index.py" });
});

test("Vercel can install the FastAPI runtime from root requirements", async () => {
  const requirements = await readFile(new URL("../../requirements.txt", import.meta.url), "utf8");

  assert.match(requirements, /^fastapi==0\.115\.6$/m);
  assert.match(requirements, /^sqlalchemy==2\.0\.36$/m);
});

test("the Vercel install command prepares both Python and frontend dependencies", async () => {
  const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));

  assert.match(config.installCommand, /uv pip install -r requirements\.txt/);
  assert.match(config.installCommand, /cd frontend && npm ci/);
});
