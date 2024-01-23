# 通过 HTTPS 包含头文件

这篇文章会实现以下效果，让 C 语言可以从互联网上 `#!c #include` 头文件。

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

## 起因

[@rexim](https://github.com/rexim) 2021 年的时候发了一个视频：[Including C File Over HTTPS](https://www.youtube.com/watch?v=4vSyqK3SK-0) ，他通过修改 TinyCC 编译器完成了上述效果。但是现在 TCC 有一些变化，他的补丁不能用了。

我试着重新分析了 TCC 的源码，写了份新的 Patch ，这篇文章用于记录具体实现过程。

## WIP...

## 参阅

- TinyCC Wiki page: [https://en.wikipedia.org/wiki/Tiny\_C\_Compiler](https://en.wikipedia.org/wiki/Tiny\_C\_Compiler)
- TinyCC Git Repo (GitHub): [https://github.com/TinyCC/tinycc](https://github.com/TinyCC/tinycc)
- STB libs: [https://github.com/nothings/stb](https://github.com/nothings/stb)
- libcurl HTTPS example: [https://curl.se/libcurl/c/https.html](https://curl.se/libcurl/c/https.html)
- libcurl URL parseing example: [https://curl.se/libcurl/c/parseurl.html](https://curl.se/libcurl/c/parseurl.html)
- @rexim's Patch: [https://gist.github.com/rexim/a6636976d12f67ea530ece118a700317](https://gist.github.com/rexim/a6636976d12f67ea530ece118a700317)
- @rexim's Video: [https://www.youtube.com/watch?v=4vSyqK3SK-0](https://www.youtube.com/watch?v=4vSyqK3SK-0)
- My Patch: [https://gist.github.com/13m0n4de/84912522cce6db31da069baf1add04f8](https://gist.github.com/13m0n4de/84912522cce6db31da069baf1add04f8)

