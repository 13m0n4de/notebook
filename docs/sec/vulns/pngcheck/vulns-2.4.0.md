---
categories: [pngcheck, Vulns, Security]
tags: [Out-of-bounds Read, Null-pointer dereference]
---

# Vulns in pngcheck 2.4.0

## 漏洞概要

- 多处缓冲区越界读取（处理多个 MNG 块 (DBYK, DISC, DROP, LOOP, nEED, ORDR, PAST, PPLT, SAVE, SEEK) 时）
- NULL 指针解引用（处理 sCAL 块时）

## 漏洞原理

源码地址：[http://www.libpng.org/pub/png/src/pngcheck-2.4.0.zip](http://www.libpng.org/pub/png/src/pngcheck-2.4.0.zip)

### Out-of-bounds read

基本都是因为没有校验块大小 `sz` 或可以通过 `-f` 选项强制继续执行。

例如 DISC 块：

```c title="pngcheck.c" linenums="4224"
} else if (strcmp(chunkid, "DISC") == 0) {
  if (png || jng) {
    printf("%s  DISC not defined in %cNG\n", verbose? ":":fname,
      png? 'P':'J');
    set_err(kMinorError);
  } else if (sz & 1) {
    printf("%s  invalid %slength\n",
      verbose? ":":fname, verbose? "":"DISC ");
    set_err(kMajorError);
  }
  if (verbose && no_err(kMinorError)) {
    if (sz == 0) {
      printf("\n    discard all nonzero objects%s\n",
        have_SAVE? " except those before SAVE":"");
    } else {
      uch *buf = buffer;
      int bytes_left = sz;

      printf(": %ld objects\n", sz >> 1);
      while (bytes_left > 0) {
        printf("    discard ID = %u\n", SH(buf));
        buf += 2;
        bytes_left -= 2;
      }
    }
  }
  last_is_IDAT = last_is_JDAT = 0;
```

当 `sz` 非常大时，会超过缓冲区 `buf` 的范围。

当遇到 `if (no_err(kMinorError))` 判断时，可以通过 `-f` 选项强制执行：

```c title="pngcheck.c" linenums="244"
#define no_err(x)   (global_error < (x) || (force && global_error == (x)))
```

### Null-pointer dereference

```c title="pngcheck.c" linenums="2707" hl_lines="3 26-30 40"
} else if (strcmp(chunkid, "sCAL") == 0) {
  int unittype = buffer[0];
  uch *pPixwidth = buffer+1, *pPixheight=NULL;

  if (!mng && have_sCAL) {
    printf("%s  multiple sCAL not allowed\n", verbose? ":":fname);
    set_err(kMinorError);
  } else if (!mng && (have_IDAT || have_JDAT)) {
    printf("%s  %smust precede %cDAT\n",
           verbose? ":":fname, verbose? "":"sCAL ", have_IDAT? 'I':'J');
    set_err(kMinorError);
  } else if (sz < 4) {
    printf("%s  invalid %slength\n",
           verbose? ":":fname, verbose? "":"sCAL ");
    set_err(kMinorError);
  } else if (unittype < 1 || unittype > 2) {
    printf("%s  invalid %sunit specifier (%d)\n",
           verbose? ":":fname, verbose? "":"sCAL ", unittype);
    set_err(kMinorError);
  } else {
    uch *qq;
    for (qq = pPixwidth;  qq < buffer+sz;  ++qq) {
      if (*qq == 0)
        break;
    }
    if (qq == buffer+sz) {
      printf("%s  missing %snull separator\n",
             verbose? ":":fname, verbose? "":"sCAL ");
      set_err(kMinorError);
    } else {
      pPixheight = qq + 1;
      if (pPixheight == buffer+sz || *pPixheight == 0) {
        printf("%s  missing %spixel height\n",
               verbose? ":":fname, verbose? "":"sCAL ");
        set_err(kMinorError);
      }
    }
    if (no_err(kMinorError)) {
      for (qq = pPixheight;  qq < buffer+sz;  ++qq) {
        if (*qq == 0)
          break;
      }
      if (qq != buffer+sz) {
        printf("%s  extra %snull separator (warning)\n",
               verbose? ":":fname, verbose? "":"sCAL ");
        set_err(kWarning);
      }
      if (*pPixwidth == '-' || *pPixheight == '-') {
        printf("%s  invalid negative %svalue(s)\n",
               verbose? ":":fname, verbose? "":"sCAL ");
        set_err(kMinorError);
      } else if (check_ascii_float(pPixwidth, pPixheight-pPixwidth-1,
                                   chunkid, fname) ||
                 check_ascii_float(pPixheight, buffer+sz-pPixheight,
                                   chunkid, fname))
      {
        set_err(kMinorError);
      }
    }
  }
  if (verbose && no_err(kMinorError)) {
    if (sz >= BS)
      sz = BS-1;
    buffer[sz] = '\0';
    printf(": image size %s x %s %s\n", pPixwidth, pPixheight,
           (unittype == 1)? "meters":"radians");
  }
  have_sCAL = 1;
  last_is_IDAT = last_is_JDAT = 0;
```

2709 行 `pPixheight` 在初始时被定义为 `NULL`，如果 2732 行 `qq == buffer+sz` 判断成功，`pPixheight` 将不会被再次赋值，直到 2746 行对为空指针的 `pPixheight` 进行解引用，触发段错误。

## 漏洞复现

- POC 代码：[poc.py](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc.py)
- POC 图片（越界读取）：
    - [poc-dbyk.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-loop.mng)
    - [poc-disc.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-disc.mng)
    - [poc-drop.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-drop.mng)
    - [poc-loop.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-loop.mng)
    - [poc-need.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-need.mng)
    - [poc-ordr.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-ordr.mng)
    - [poc-past.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-past.mng)
    - [poc-pplt.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-pplt.mng)
    - [poc-save.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-save.mng)
    - [poc-seek.mng](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-seek.mng)
- POC 图片（空指针解引用）：
    - [poc-scal.png](https://github.com/13m0n4de/pngcheck-vulns/blob/main/vulns-2.4.0/poc-scal.png)

```
$ python poc.py all

$ pngcheck -f poc-dbyk.mng
$ pngcheck -v poc-disc.mng
$ pngcheck poc-drop.mng
$ pngcheck -v poc-loop.mng
$ pngcheck -v poc-need.mng
$ pngcheck poc-ordr.mng
$ pngcheck -f poc-past.mng
$ pngcheck poc-pplt.mng
$ pngcheck -v poc-save.mng
$ pngcheck -v poc-seek.mng
$ pngcheck -f poc-scal.png
```

## 漏洞修复

官方在 v3.0.0 的修复方案是，全部添加 `sz > BS` 判断，并完全删除 `-f` 选项。

```diff
@@ -4230,8 +4277,13 @@
         printf("%s  invalid %slength\n",
           verbose? ":":fname, verbose? "":"DISC ");
         set_err(kMajorError);
+      } else if (sz > BS) {
+	/* FIXME: large DISC chunks should be supported */
+        printf("%s  checking large %schunk not currently supported\n",
+               verbose? ":":fname, verbose? "":"DISC ");
+        set_err(kMinorError);
       }
-      if (verbose && no_err(kMinorError)) {
+      if (verbose && no_err(kMinorError) && sz <= BS) {
         if (sz == 0) {
           printf("\n    discard all nonzero objects%s\n",
             have_SAVE? " except those before SAVE":"");
```

## 参考资料

- [pngcheck Home Page](http://www.libpng.org/pub/png/apps/pngcheck.html)
- [Portable Network Graphics (PNG) Specification and Extensions](http://www.libpng.org/pub/png/spec)
- [MNG (Multiple-image Network Graphics) Format](http://www.libpng.org/pub/mng/spec)
