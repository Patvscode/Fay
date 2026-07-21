import { createReadStream, existsSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("./dist", import.meta.url));
const host = process.env.FAY_AVATAR_HOST || "127.0.0.1";
const port = Number(process.env.FAY_AVATAR_PORT || 5173);
const fayBase = process.env.FAY_HTTP_BASE || "http://127.0.0.1:5000";
const fayUrl = new URL(fayBase);
const fayWsUrl =
  process.env.FAY_WS_URL ||
  `${fayUrl.protocol === "https:" ? "wss" : "ws"}://${fayUrl.hostname}:10002`;

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".wasm": "application/wasm",
};

async function proxyAudio(request, response, pathname) {
  const filename = decodeURIComponent(pathname.slice("/fay/audio/".length));
  if (!filename || filename.includes("/") || filename.includes("\\")) {
    response.writeHead(400).end("Invalid audio filename");
    return;
  }
  const upstream = await fetch(`${fayBase}/audio/${encodeURIComponent(filename)}`);
  response.writeHead(upstream.status, {
    "content-type": upstream.headers.get("content-type") || "audio/wav",
    "cache-control": "no-store",
  });
  if (upstream.body) {
    for await (const chunk of upstream.body) response.write(chunk);
  }
  response.end();
}

const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url || "/", `http://${request.headers.host}`);
    if (url.pathname === "/fay/config") {
      response.writeHead(200, {
        "content-type": "application/json; charset=utf-8",
        "cache-control": "no-store",
      });
      response.end(JSON.stringify({ wsUrl: fayWsUrl }));
      return;
    }
    if (url.pathname.startsWith("/fay/audio/")) {
      await proxyAudio(request, response, url.pathname);
      return;
    }

    const requested = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
    const safePath = normalize(requested).replace(/^(\.\.[/\\])+/, "");
    let filePath = join(root, safePath);
    if (!existsSync(filePath)) filePath = join(root, "index.html");
    response.writeHead(200, {
      "content-type": contentTypes[extname(filePath)] || "application/octet-stream",
      "cache-control": filePath.endsWith("index.html") ? "no-store" : "public, max-age=31536000, immutable",
    });
    createReadStream(filePath).pipe(response);
  } catch (error) {
    response.writeHead(500, { "content-type": "text/plain; charset=utf-8" });
    response.end(`Avatar server error: ${error.message}`);
  }
});

server.listen(port, host, () => {
  console.log(`Fay avatar renderer: http://${host}:${port}`);
  console.log(`Fay audio source: ${fayBase}`);
  console.log(`Fay avatar WebSocket: ${fayWsUrl}`);
});
