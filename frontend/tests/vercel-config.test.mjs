import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("Vercel routes API requests to the Python entrypoint", async () => {
  const config = JSON.parse(await readFile(new URL("../../vercel.json", import.meta.url), "utf8"));

  assert.deepEqual(config.rewrites[0], { source: "/api/(.*)", destination: "/api/index.py" });
});
