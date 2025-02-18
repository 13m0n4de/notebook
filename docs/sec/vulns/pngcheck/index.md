---
tags: [Out-of-bounds Read, Null-pointer dereference]
---

# pngcheck

[pngcheck](http://www.libpng.org/pub/png/apps/pngcheck.html) 是一个用于验证 PNG / JNG / MNG 文件格式的命令行工具。本系列文章记录了对 pngcheck 不同版本历史漏洞的分析。

POC 仓库：[github.com/13m0n4de/pngcheck-vulns](https://github.com/13m0n4de/pngcheck-vulns/)

## CVE 漏洞

| CVE ID         | CWE ID  | 漏洞类型           | 分析文章                      |
| -------------- | ------- | ------------------ | ----------------------------- |
| CVE-2020-35511 | CWE-126 | Buffer Over-read   | [详细分析](cve-2020-35511.md) |
| CVE-2020-27818 | CWE-125 | Out-of-bounds Read | [详细分析](cve-2020-27818.md) |

## 其他漏洞

### pngcheck 2.4.0

- 多处 Out-of-bounds Read 漏洞（MNG 块处理）
    - 受影响的 MNG 块: DBYK, DISC, DROP, LOOP, nEED, ORDR, PAST, PPLT, SAVE, SEEK
- NULL 指针解引用漏洞（sCAL 块处理）

[详细分析](./vulns-2.4.0.md)

### pngcheck 3.0.0

- Out-of-bounds Read 漏洞（MNG PPLT 块处理）

[详细分析](./vulns-3.0.0.md)

### pngcheck 3.0.1

- Out-of-bounds Read 漏洞（MNG LOOP 块处理）

[详细分析](./vulns-3.0.1.md)
