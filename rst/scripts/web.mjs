#!/usr/bin/env node

import { spawn } from "node:child_process";
import { existsSync, readFileSync, statSync, watch } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, normalize, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repository = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const output = join(repository, "rst/_build/html");
const command = process.argv[2] ?? "dev";
const arguments_ = process.argv.slice(3);
const portIndex = arguments_.indexOf("--port");
const port = Number(portIndex >= 0 ? arguments_[portIndex + 1] : process.env.PORT ?? 8000);

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error(`invalid port: ${port}`);
}
if (!["build", "dev", "preview"].includes(command)) {
  throw new Error(`usage: node rst/scripts/web.mjs build|dev|preview [--port PORT]`);
}

function releaseVersion() {
  if (process.env.GECODE_VERSION) return process.env.GECODE_VERSION;
  const inventory = join(repository, "rst/release-reference-inventory.json");
  if (!existsSync(inventory)) return "development";
  return JSON.parse(readFileSync(inventory, "utf8")).gecode_version ?? "development";
}

function build() {
  return new Promise((complete) => {
    const child = spawn(
      "uv",
      ["run", "python", "rst/scripts/build.py", "html"],
      {
        cwd: repository,
        env: { ...process.env, GECODE_VERSION: releaseVersion() },
        stdio: "inherit",
      },
    );
    child.on("error", (error) => {
      console.error(`Unable to start the documentation build: ${error.message}`);
      complete(false);
    });
    child.on("exit", (code) => complete(code === 0));
  });
}

if (command === "build") {
  process.exitCode = (await build()) ? 0 : 1;
} else {
  if (command === "dev" && !(await build())) {
    process.exitCode = 1;
  } else if (!existsSync(output)) {
    console.error("No web build found. Run `npm run build` first.");
    process.exitCode = 1;
  } else {
    const clients = new Set();
    const mime = {
      ".css": "text/css; charset=utf-8",
      ".gif": "image/gif",
      ".html": "text/html; charset=utf-8",
      ".ico": "image/x-icon",
      ".js": "text/javascript; charset=utf-8",
      ".json": "application/json; charset=utf-8",
      ".pdf": "application/pdf",
      ".png": "image/png",
      ".svg": "image/svg+xml",
      ".txt": "text/plain; charset=utf-8",
      ".woff": "font/woff",
      ".woff2": "font/woff2",
    };
    const reloadScript = `
<script data-mpg-dev-reload>
  new EventSource('/__mpg_reload').addEventListener('reload', () => location.reload());
</script>`;

    function resolveRequest(pathname) {
      let decoded;
      try {
        decoded = decodeURIComponent(pathname);
      } catch {
        return null;
      }
      const candidate = normalize(join(output, decoded));
      if (relative(output, candidate).startsWith("..")) return null;
      if (existsSync(candidate) && statSync(candidate).isDirectory()) {
        return join(candidate, "index.html");
      }
      if (!extname(candidate) && existsSync(join(candidate, "index.html"))) {
        return join(candidate, "index.html");
      }
      return candidate;
    }

    const server = createServer((request, response) => {
      const url = new URL(request.url ?? "/", `http://${request.headers.host ?? "localhost"}`);
      if (command === "dev" && url.pathname === "/__mpg_reload") {
        response.writeHead(200, {
          "Cache-Control": "no-cache",
          "Content-Type": "text/event-stream",
          Connection: "keep-alive",
        });
        response.write("retry: 500\n\n");
        clients.add(response);
        request.on("close", () => clients.delete(response));
        return;
      }
      const path = resolveRequest(url.pathname);
      if (!path || !existsSync(path) || !statSync(path).isFile()) {
        response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        response.end("Not found\n");
        return;
      }
      const extension = extname(path).toLowerCase();
      let content = readFileSync(path);
      if (command === "dev" && extension === ".html") {
        const html = content.toString("utf8");
        content = Buffer.from(html.replace("</body>", `${reloadScript}</body>`));
      }
      response.writeHead(200, {
        "Cache-Control": command === "dev" ? "no-store" : "no-cache",
        "Content-Type": mime[extension] ?? "application/octet-stream",
      });
      response.end(content);
    });

    const watchers = [];
    let timer;
    let building = false;
    let pending = false;
    async function rebuild() {
      if (building) {
        pending = true;
        return;
      }
      building = true;
      console.log("\nDocumentation changed; rebuilding…");
      const success = await build();
      building = false;
      if (success) {
        console.log("Build complete; refreshing browsers.");
        for (const client of clients) client.write("event: reload\ndata: ready\n\n");
      } else {
        console.error("Build failed; keeping the last successful preview.");
      }
      if (pending) {
        pending = false;
        await rebuild();
      }
    }
    function scheduleRebuild(_event, filename) {
      if (!filename) return;
      const changed = String(filename ?? "");
      if (changed.includes("__pycache__") || changed.endsWith(".pyc")) return;
      clearTimeout(timer);
      timer = setTimeout(rebuild, 180);
    }

    if (command === "dev") {
      for (const source of [
        "rst/content", "rst/extensions", "rst/_templates", "rst/_static",
        "rst/figures", "rst/manifests", "rst/conf.py",
      ]) {
        const path = join(repository, source);
        watchers.push(watch(path, { recursive: statSync(path).isDirectory() }, scheduleRebuild));
      }
    }

    server.listen(port, "127.0.0.1", () => {
      const mode = command === "dev" ? "Development server" : "Preview";
      console.log(`${mode}: http://127.0.0.1:${port}/`);
      if (command === "dev") console.log("Watching manual sources, templates, styles, and figures.");
    });

    function close() {
      clearTimeout(timer);
      for (const watcher of watchers) watcher.close();
      for (const client of clients) client.end();
      server.close(() => process.exit(0));
    }
    process.on("SIGINT", close);
    process.on("SIGTERM", close);
  }
}
