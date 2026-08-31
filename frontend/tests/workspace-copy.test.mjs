import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("the curriculum presents the TeachBack loop as a mission control sequence", async () => {
  const page = await readFile(new URL("../src/pages/CurriculumPage.tsx", import.meta.url), "utf8");

  assert.match(page, /Understand the system/);
  assert.match(page, /signal-orbit/);
});
