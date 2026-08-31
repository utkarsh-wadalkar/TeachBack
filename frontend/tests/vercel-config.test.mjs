import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("Vercel leaves Python API routing to the native runtime", async () => {
  const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));

  assert.equal(config.rewrites, undefined);
});

test("the Vite production build feeds FastAPI's public static directory", async () => {
  const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));

  assert.match(config.buildCommand, /npm run build -- --outDir \.\.\/public --emptyOutDir/);
  assert.equal(config.outputDirectory, undefined);
});

test("the frontend uses hash navigation so static hosting needs no route rewrite", async () => {
  const entry = await readFile(new URL("../src/main.tsx", import.meta.url), "utf8");

  assert.match(entry, /HashRouter/);
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
