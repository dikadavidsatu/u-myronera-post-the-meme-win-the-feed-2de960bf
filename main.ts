// main.ts — "Post the Meme, Win the Feed" (u-myronera-post-the-meme-win-the-feed-2de960bf)
//
// What this program does, and why it is deliberately small.
//
// The entry in this bounty is not this program. The entry is the meme post
// itself: one picture about make.fun, made for people who build AI agents,
// posted natively on X from the entrant's own public account, its text
// carrying the sponsor's mention (@_myronera) and one of the entrant's
// make.fun play codes. The house reads the post's public counts (likes,
// reposts, quotes) through FxTwitter after entries close and ranks the
// entries on engagement. Nothing this program writes about the post is
// scored, and no check reads what the picture shows.
//
// So this program has exactly one job: carry POST.json — the file at the
// repository root that names the post's address — from the bot directory
// into the output directory, byte for byte, so the gate can read it.
//
//   /bot/POST.json  ->  /output/POST.json
//
// Outside the grader's container the two directories are stood in for by
// environment variables:
//
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
//
// The program is deterministic by construction: it copies bytes, writes no
// timestamps, no random values and no absolute paths anywhere, so two runs
// over the same repository produce the same /output/POST.json. It validates
// the post address before copying, so a malformed POST.json fails loudly
// here (exit 1, message on stderr) instead of silently reaching the gate
// as an invalid entry.
//
// Runtime: Node 22, standard library only. No network, no secrets, no
// environment beyond the two directory variables above.

import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, resolve } from "node:path";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/** Where the grader mounts the entry's repository snapshot. */
const BOT_DIR: string = process.env.MAKEFUN_BOT_DIR ?? "/bot";

/** Where the gate reads the entry's outputs from. */
const OUTPUT_DIR: string = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

/** The one file this program ferries. */
const POST_FILE = "POST.json";

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------

/** Fail loudly: one line on stderr, non-zero exit, nothing half-written. */
function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

/** SHA-256 hex digest of a buffer, used to prove the copy is exact. */
function sha256Hex(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}

/**
 * Parse a post address the way the bounty rules describe it.
 *
 * Accepted shapes (the id is digits only; a query string or fragment after
 * it is read past):
 *   https://x.com/<handle>/status/<id>
 *   https://twitter.com/<handle>/status/<id>
 *   https://www.x.com/... / https://mobile.x.com/... (same for twitter.com)
 *   https://x.com/i/web/status/<id>
 *
 * Returns the normalised { handle, id } pair, or null when the address is
 * not a post address at all. A placeholder such as
 * "https://x.com/<handle>/status/<id>" is not a post address: the angle
 * brackets are not a handle and "<id>" is not digits, so it is rejected
 * here on purpose — the placeholder must be replaced with the real post
 * before the entry is submitted.
 */
function parsePostUrl(raw: unknown): { handle: string; id: string } | null {
  if (typeof raw !== "string") return null;
  let url: URL;
  try {
    url = new URL(raw.trim());
  } catch {
    return null;
  }
  if (url.protocol !== "https:") return null;

  const host = url.hostname.toLowerCase();
  const knownHosts = [
    "x.com",
    "www.x.com",
    "mobile.x.com",
    "twitter.com",
    "www.twitter.com",
    "mobile.twitter.com",
  ];
  if (!knownHosts.includes(host)) return null;

  // Split the path into its segments, ignoring a leading/trailing slash.
  const segments = url.pathname.split("/").filter((part) => part.length > 0);

  // Canonical form: /<handle>/status/<id>
  if (segments.length === 3 && segments[1] === "status") {
    const [handle, , id] = segments;
    if (isHandle(handle) && isPostId(id)) return { handle, id };
    return null;
  }

  // Web-client form: /i/web/status/<id> (no handle in the address).
  if (
    segments.length === 4 &&
    segments[0] === "i" &&
    segments[1] === "web" &&
    segments[2] === "status"
  ) {
    const id = segments[3];
    if (isPostId(id)) return { handle: "(web)", id };
    return null;
  }

  return null;
}

/** An X handle: 1-15 characters of letters, digits or underscore. */
function isHandle(handle: string): boolean {
  return /^[A-Za-z0-9_]{1,15}$/.test(handle);
}

/** A post id: digits only, at least one digit. */
function isPostId(id: string): boolean {
  return /^[0-9]+$/.test(id);
}

/**
 * Read POST.json from the bot directory and validate its shape.
 *
 * Expected content: a JSON object with exactly the shape
 *   { "url": "https://x.com/<handle>/status/<id>" }
 * Extra keys are tolerated (they are copied through untouched), but the
 * url field must be present, a string, and a post address per
 * parsePostUrl. Anything else is a hard failure: the gate would refuse
 * the entry anyway, so failing here keeps the mistake visible.
 */
function readAndValidatePost(sourcePath: string): { raw: Buffer; url: string } {
  let raw: Buffer;
  try {
    raw = readFileSync(sourcePath);
  } catch (err) {
    fail(
      `could not read ${sourcePath}: ${(err as Error).message}. ` +
        `POST.json must sit at the repository root.`,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw!.toString("utf8"));
  } catch (err) {
    fail(`POST.json is not valid JSON: ${(err as Error).message}`);
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    fail("POST.json must be a JSON object, e.g. {\"url\": \"https://x.com/<handle>/status/<id>\"}");
  }

  const url = (parsed as Record<string, unknown>).url;
  if (typeof url !== "string" || url.trim().length === 0) {
    fail('POST.json must carry a "url" string naming the X post.');
  }

  const post = parsePostUrl(url);
  if (post === null) {
    fail(
      `POST.json "url" is not an X post address: ${JSON.stringify(url)}. ` +
        `Expected https://x.com/<handle>/status/<digits> (or the twitter.com / /i/web/status/ forms). ` +
        `If this is still the starter placeholder, replace it with the real post's address first.`,
    );
  }

  return { raw: raw!, url: url.trim() };
}

// ---------------------------------------------------------------------------
// Main: copy POST.json, byte for byte, and prove the copy.
// ---------------------------------------------------------------------------

function main(): void {
  const sourcePath = join(BOT_DIR, POST_FILE);
  const destPath = join(OUTPUT_DIR, POST_FILE);

  // 0. Guard against a self-copy: when the output directory IS the bot
  //    directory, copying would be a no-op and a missing POST.json could
  //    slip through unnoticed. The grader always mounts them apart, but
  //    a local run with both variables pointed at "." must fail loudly.
  if (resolve(BOT_DIR) === resolve(OUTPUT_DIR)) {
    fail(
      `MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR both resolve to ${resolve(BOT_DIR)}; ` +
        `the output directory must differ from the bot directory.`,
    );
  }

  // 1. Read + validate first, so a bad POST.json never produces a
  //    half-copied output file.
  const { raw, url } = readAndValidatePost(sourcePath);
  const sourceHash = sha256Hex(raw);

  // 2. Make sure the output directory exists (recursive: harmless when it
  //    already does).
  mkdirSync(OUTPUT_DIR, { recursive: true });

  // 3. Copy the bytes exactly. copyFileSync preserves the content; we then
  //    re-read the destination and compare hashes so the run can prove the
  //    copy instead of merely assuming it.
  try {
    copyFileSync(sourcePath, destPath);
  } catch (err) {
    fail(`could not copy ${sourcePath} to ${destPath}: ${(err as Error).message}`);
  }

  // 4. Verify: the destination must hash identically to the source. The
  //    gate runs this program twice and requires identical bytes, so an
  //    exact copy is the whole determinism story.
  let copied: Buffer;
  try {
    copied = readFileSync(destPath);
  } catch (err) {
    fail(`could not re-read ${destPath} after copying: ${(err as Error).message}`);
  }
  if (sha256Hex(copied!) !== sourceHash) {
    fail(`${destPath} does not match ${sourcePath} after copying (hash mismatch).`);
  }

  // 5. One line of confirmation on stdout. Nothing else is written: no
  //    timestamps, no random values, no absolute paths, so the output is
  //    identical on every run.
  console.log(`main.ts: copied POST.json -> ${POST_FILE} (${url}) [sha256 ${sourceHash.slice(0, 12)}...]`);
}

main();
