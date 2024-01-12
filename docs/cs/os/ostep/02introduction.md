# 第 2 章 操作系统介绍

图 2.3 的程序有点问题，`malloc` 之后没有释放，`%08x` 不如使用 `%p`，强制转换 `(unsigned) p` 也没有必要。

改了一下，顺便把自定义的 `Spin` 函数换成了 `sleep` 。

```c title='mem.c'
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  int *p = malloc(sizeof(int)); // a1
  assert(p != NULL);
  printf("(%d) memory address of p: %p\n", getpid(), p); // a2
  *p = 0;                                                // a3
  for (int i = 0; i < 5; i++) {
    sleep(1);
    *p = *p + 1;
    printf("(%d) p: %d\n", getpid(), *p); // a4
  }
  free(p);
  return 0;
}
```

如果要得到和书中一样的效果，还需要关闭 ASLR 地址空间随机化，不然就算是虚拟内存，每次分配的地址也不固定。

```shell
$ echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

如果编译时关掉 PIE ，得到的地址会更“好看”些，更接近书中内容。

```shell
$ gcc mem.c -o mem -no-pie
```

```shell
$ ./mem &; ./mem & # (1)!
(63585) memory address of p: 0x4052a0
(63586) memory address of p: 0x4052a0
(63585) p: 1
(63586) p: 1
(63585) p: 2
(63586) p: 2
(63586) p: 3
(63585) p: 3
(63586) p: 4
(63585) p: 4
(63586) p: 5
(63585) p: 5
```

1. `&` 符号用于在 Unix-like 系统中后台运行进程，它会启动命令然后立即返回到命令行提示符，而不是挂起直到命令完成。不同的 shell 可能实现方式不同，但行为基本一致。最终的效果就是同时运行两个 `mem` 程序。

实验完尽快把 ASLR 改回去，以免对系统安全造成影响，现代 Linux 系统中 `/proc/sys/kernel/randomize_va_space` 内容一般都是 `2` ，意为更强的随机化。

```shell
$ echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
```

