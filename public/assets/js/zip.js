const CRC_TABLE = new Uint32Array(256);

for (let n = 0; n < 256; n += 1) {
  let c = n;
  for (let k = 0; k < 8; k += 1) {
    c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
  }
  CRC_TABLE[n] = c >>> 0;
}

function crc32(bytes) {
  let crc = 0xffffffff;
  for (let i = 0; i < bytes.length; i += 1) {
    const index = (crc ^ bytes[i]) & 0xff;
    crc = CRC_TABLE[index] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function dosDateTime(date = new Date()) {
  const year = Math.max(1980, date.getFullYear());
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hour = date.getHours();
  const minute = date.getMinutes();
  const second = Math.floor(date.getSeconds() / 2);

  const dosTime = (hour << 11) | (minute << 5) | second;
  const dosDate = ((year - 1980) << 9) | (month << 5) | day;
  return { dosDate, dosTime };
}

function writeUint16(view, offset, value) {
  view.setUint16(offset, value & 0xffff, true);
}

function writeUint32(view, offset, value) {
  view.setUint32(offset, value >>> 0, true);
}

function concatUint8(chunks) {
  const total = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const merged = new Uint8Array(total);
  let offset = 0;
  chunks.forEach((chunk) => {
    merged.set(chunk, offset);
    offset += chunk.length;
  });
  return merged;
}

function normalizePath(path) {
  return path.replace(/\\+/g, "/").replace(/^\/+/, "");
}

export async function buildZip(entries) {
  const encoder = new TextEncoder();
  const localParts = [];
  const centralParts = [];
  let localOffset = 0;

  for (const entry of entries) {
    const normalizedName = normalizePath(entry.name);
    if (!normalizedName || normalizedName.includes("..")) {
      throw new Error(`Invalid zip entry path: ${entry.name}`);
    }

    let fileBytes;
    if (entry.data instanceof Uint8Array) {
      fileBytes = entry.data;
    } else if (entry.data instanceof ArrayBuffer) {
      fileBytes = new Uint8Array(entry.data);
    } else if (typeof entry.data === "string") {
      fileBytes = encoder.encode(entry.data);
    } else {
      throw new Error(`Unsupported entry type for ${entry.name}`);
    }

    const nameBytes = encoder.encode(normalizedName);
    const crc = crc32(fileBytes);
    const size = fileBytes.length;
    const { dosDate, dosTime } = dosDateTime(entry.date || new Date());

    const localHeader = new Uint8Array(30 + nameBytes.length);
    const lv = new DataView(localHeader.buffer);
    writeUint32(lv, 0, 0x04034b50);
    writeUint16(lv, 4, 20);
    writeUint16(lv, 6, 0);
    writeUint16(lv, 8, 0);
    writeUint16(lv, 10, dosTime);
    writeUint16(lv, 12, dosDate);
    writeUint32(lv, 14, crc);
    writeUint32(lv, 18, size);
    writeUint32(lv, 22, size);
    writeUint16(lv, 26, nameBytes.length);
    writeUint16(lv, 28, 0);
    localHeader.set(nameBytes, 30);

    localParts.push(localHeader, fileBytes);

    const centralHeader = new Uint8Array(46 + nameBytes.length);
    const cv = new DataView(centralHeader.buffer);
    writeUint32(cv, 0, 0x02014b50);
    writeUint16(cv, 4, 20);
    writeUint16(cv, 6, 20);
    writeUint16(cv, 8, 0);
    writeUint16(cv, 10, 0);
    writeUint16(cv, 12, dosTime);
    writeUint16(cv, 14, dosDate);
    writeUint32(cv, 16, crc);
    writeUint32(cv, 20, size);
    writeUint32(cv, 24, size);
    writeUint16(cv, 28, nameBytes.length);
    writeUint16(cv, 30, 0);
    writeUint16(cv, 32, 0);
    writeUint16(cv, 34, 0);
    writeUint16(cv, 36, 0);
    writeUint32(cv, 38, 0);
    writeUint32(cv, 42, localOffset);
    centralHeader.set(nameBytes, 46);
    centralParts.push(centralHeader);

    localOffset += localHeader.length + fileBytes.length;
  }

  const centralData = concatUint8(centralParts);
  const endRecord = new Uint8Array(22);
  const ev = new DataView(endRecord.buffer);
  writeUint32(ev, 0, 0x06054b50);
  writeUint16(ev, 4, 0);
  writeUint16(ev, 6, 0);
  writeUint16(ev, 8, entries.length);
  writeUint16(ev, 10, entries.length);
  writeUint32(ev, 12, centralData.length);
  writeUint32(ev, 16, localOffset);
  writeUint16(ev, 20, 0);

  return concatUint8([...localParts, centralData, endRecord]);
}

