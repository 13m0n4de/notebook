---
date: 2024-02-17
categories:
  - Programming Language
---

# 通过 HTTPS 包含头文件

实现了一个有意思的效果，让 C 语言可以从互联网上 `#!c #include` 头文件。

```c title='include_files_from_internet.c'
#define STB_SPRINTF_IMPLEMENTATION
#include <https://raw.githubusercontent.com/nothings/stb/master/stb_sprintf.h> // <- look at this 
#include <stdio.h>

int main() {
    char buffer[20];

    // Using functions defined by stb_sprintf.h
    stbsp_sprintf(buffer, "Hello %s", "NAVI");
    puts(buffer);

    return 0;
}
```

你知道的，4202 年，Everything Over HTTPS（笑）。

- My TinyCC Patch: [https://gist.github.com/13m0n4de/84912522cce6db31da069baf1add04f8](https://gist.github.com/13m0n4de/84912522cce6db31da069baf1add04f8)
- My Chibicc Patch: [https://gist.github.com/13m0n4de/f2b4b8e71ce6a93530cbe9e4e45cbe71](https://gist.github.com/13m0n4de/f2b4b8e71ce6a93530cbe9e4e45cbe71)

<!-- more -->

起因是 [@rexim](https://github.com/rexim) 2021 年的时候发了一个视频：[Including C File Over HTTPS](https://www.youtube.com/watch?v=4vSyqK3SK-0) ，他通过修改 TinyCC 编译器完成了上述效果。但是现在 TCC 有一些变化，他的补丁不能用了。

我试着重新分析了 TCC 的源码，写了份新的 Patch。

本想着记录分析过程，想了想也没什么值得记的，放在笔记本里不合适，就挪到这儿来了。

而且还顺带给 chibicc 也写了份。

不过 chibicc tokenize 的时候会把 `//` 之后的内容全部视为注释忽略掉，包括 `<>` 之间的内容，要改动的东西会比较多，就设计为把 HTTPS 链接放在双引号里：

```c
#include "https://raw.githubusercontent.com/nothings/stb/master/stb_sprintf.h"
```

比起视频中的补丁，还额外添加了个一厢情愿的功能：让头文件下载到源码目录下，而不是当前目录（执行命令时的目录）下。

```
$ tcc /path/to/source/include_files_from_internet.c
$ chibicc /path/to/source/include_files_from_internet.c
```

文件将被下载到 `/path/to/source/stb_sprintf.h`

结束后的感想，chibicc 比 TCC 的代码直观得多，注释也更全，感觉就像「我写大概也会是这样吧」，有种默契感。

## 参考

- TinyCC: [https://bellard.org/tcc/](https://bellard.org/tcc/)
- TinyCC git repo: [https://repo.or.cz/tinycc.git](https://repo.or.cz/tinycc.git)
- chibicc git repo: [https://github.com/rui314/chibicc](https://github.com/rui314/chibicc)
- STB libs: [https://github.com/nothings/stb](https://github.com/nothings/stb)
- libcurl HTTPS example: [https://curl.se/libcurl/c/https.html](https://curl.se/libcurl/c/https.html)
- libcurl URL parseing example: [https://curl.se/libcurl/c/parseurl.html](https://curl.se/libcurl/c/parseurl.html)
- @rexim's Patch: [https://gist.github.com/rexim/a6636976d12f67ea530ece118a700317](https://gist.github.com/rexim/a6636976d12f67ea530ece118a700317)
- @rexim's Video: [https://www.youtube.com/watch?v=4vSyqK3SK-0](https://www.youtube.com/watch?v=4vSyqK3SK-0)
- My TinyCC Patch: [https://gist.github.com/13m0n4de/84912522cce6db31da069baf1add04f8](https://gist.github.com/13m0n4de/84912522cce6db31da069baf1add04f8)
- My Chibicc Patch: [https://gist.github.com/13m0n4de/f2b4b8e71ce6a93530cbe9e4e45cbe71](https://gist.github.com/13m0n4de/f2b4b8e71ce6a93530cbe9e4e45cbe71)
