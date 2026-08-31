import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

test("the dark visual system exposes its reference-inspired primitives", async () => {
  const css = await readFile(new URL("../src/index.css", import.meta.url), "utf8");

  for (const token of ["--color-void", "--color-signal", ".dark-grid", ".signal-orbit"]) {
    assert.match(css, new RegExp(token.replace(/[.*+?^${}()|[\\]\\]/g, "\\$&")));
  }
});
