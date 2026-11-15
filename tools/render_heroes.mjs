/** Rasterize deterministic SVG layouts; the portrait itself is never edited. */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { crc32, deflateSync, inflateSync } from 'node:zlib';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
if (!process.argv[2]) throw new Error('Pass the npm prefix containing @resvg/resvg-js.');
const require = createRequire(path.join(path.resolve(process.argv[2]), 'package.json'));
let Resvg;
try { ({ Resvg } = require('@resvg/resvg-js')); }
catch { throw new Error('Install @resvg/resvg-js in the specified npm prefix. See docs/PROFILE_REVIEW.md.'); }

// Recompress the existing PNG scanlines losslessly; no pixel conversion,
// quantization, or changes to the supplied portrait take place.
function optimizePNG(bytes) {
  const png = Buffer.from(bytes), chunks = [], imageData = [];
  let cursor = 8, insertion;
  while (cursor < png.length) {
    const size = png.readUInt32BE(cursor);
    if (png.toString('ascii',cursor+4,cursor+8) === 'IDAT') {
      insertion ??= chunks.length;
      imageData.push(png.subarray(cursor+8,cursor+8+size));
    } else chunks.push(png.subarray(cursor,cursor+12+size));
    cursor += size+12;
  }
  const scanlines = inflateSync(Buffer.concat(imageData));
  const payload = Buffer.concat([Buffer.from('IDAT'),deflateSync(scanlines,{level:9})]);
  const size = Buffer.alloc(4), crc = Buffer.alloc(4);
  size.writeUInt32BE(payload.length-4);
  crc.writeUInt32BE(crc32(payload));
  chunks.splice(insertion,0,Buffer.concat([size,payload,crc]));
  const optimized = Buffer.concat([png.subarray(0,8),...chunks]);
  return optimized.length < png.length ? optimized : png;
}
for (const [layout, output, width] of [
  ['hero-layout.svg', 'hero.png', 2000],
  ['hero-mobile-layout.svg', 'hero-mobile.png', 960],
]) {
  const source = fs.readFileSync(path.join(root, '.preview', layout));
  const png = new Resvg(source, { fitTo: { mode:'width', value:width } }).render().asPng();
  fs.writeFileSync(path.join(root, 'assets', output), optimizePNG(png));
}
