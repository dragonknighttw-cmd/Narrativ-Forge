import { cp, mkdir, stat } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const standalone = path.join(root, ".next", "standalone");
const staticSource = path.join(root, ".next", "static");
const publicSource = path.join(root, "public");
const server = path.join(standalone, "server.js");

await stat(server);
await mkdir(path.join(standalone, ".next"), { recursive: true });
await cp(staticSource, path.join(standalone, ".next", "static"), {
  recursive: true,
  force: true,
});

try {
  await stat(publicSource);
  await cp(publicSource, path.join(standalone, "public"), {
    recursive: true,
    force: true,
  });
} catch (error) {
  if (error?.code !== "ENOENT") throw error;
}

console.log("Prepared Next.js standalone server with static assets.");
