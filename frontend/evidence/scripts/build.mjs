import { build } from "esbuild";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repository = resolve(frontend, "../..");
const output = join(repository, "src/bond/data/web/evidence");
const tokenFile = join(repository, "src/bond/data/design_tokens.json");
const tokens = JSON.parse(await readFile(tokenFile, "utf8"));

function digest(content) {
  return createHash("sha256").update(content).digest("hex");
}

function declarations() {
  const result = [];

  for (const [name, value] of Object.entries(tokens.primitives)) {
    result.push(`--bond-p-${name.replaceAll("_", "-")}: ${value};`);
  }

  for (const [name, reference] of Object.entries(tokens.semantic)) {
    if (!(reference in tokens.primitives)) throw new Error("Unknown primitive token.");
    result.push(
      `--bond-s-${name.replaceAll("_", "-")}: var(--bond-p-${reference.replaceAll("_", "-")});`,
    );
  }

  for (const [name, reference] of Object.entries(tokens.components)) {
    if (!(reference in tokens.semantic)) throw new Error("Unknown semantic token.");
    result.push(
      `--bond-c-${name.replaceAll("_", "-")}: var(--bond-s-${reference.replaceAll("_", "-")});`,
    );
  }

  return `.bond-explorer { ${result.join("\n")} }`;
}

async function collect(directory) {
  const found = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) found.push(...await collect(path));
    else found.push(path);
  }
  return found;
}

await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });

await build({
  absWorkingDir: frontend,
  entryPoints: ["src/index.tsx"],
  bundle: true,
  format: "esm",
  platform: "browser",
  target: ["es2022"],
  outdir: output,
  entryNames: "evidence",
  jsx: "automatic",
  minify: true,
  sourcemap: false,
  legalComments: "external",
  define: { "process.env.NODE_ENV": '"production"' },
  plugins: [
    {
      name: "bond-shared-tokens",
      setup(builder) {
        builder.onResolve({ filter: /^bond:tokens$/ }, () => ({
          path: "tokens",
          namespace: "bond",
        }));
        builder.onLoad({ filter: /.*/, namespace: "bond" }, () => ({
          contents: declarations(),
          loader: "css",
        }));
      },
    },
  ],
});

const sourceFiles = [
  ...await collect(join(frontend, "src")),
  ...await collect(join(frontend, "scripts")),
  join(frontend, "package.json"),
  join(frontend, "package-lock.json"),
  join(frontend, "tsconfig.json"),
  join(frontend, "eslint.config.mjs"),
  tokenFile,
].sort();

const sources = {};
for (const path of sourceFiles) {
  sources[relative(repository, path).split("\\").join("/")] =
    digest(await readFile(path));
}

const outputs = {};
for (const path of (await collect(output)).sort()) {
  outputs[relative(output, path)] = digest(await readFile(path));
}

await writeFile(
  join(output, "build_manifest.json"),
  JSON.stringify(
    {
      schema_version: 1,
      component: "bond_evidence_explorer",
      sources,
      outputs,
    },
    null,
    2,
  ) + "\n",
);

console.log("Built packaged component assets with source and output checksums.");
