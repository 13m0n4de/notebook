# 第 2 章 操作系统介绍

这章引入了课程的三个主题，也是操作系统的三个重要功能：

1. 虚拟化
1. 并发
1. 持久性

作者介绍的时候用了一些代码示例，其中许多函数都被刻意包装了一层，我不太喜欢，而且一开始我也不知道有附录代码，就全都重新改了一遍。

附录代码：[github.com/remzi-arpacidusseau/ostep-code/](https://github.com/remzi-arpacidusseau/ostep-code/)

## 2.1 虚拟化 CPU

```c title='cpu.c' hl_lines='3 11 12'
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  if (argc != 2) {
    fprintf(stderr, "usage: cpu <string>\n");
    exit(1);
  }
  char *str = argv[1];
  for (int i = 0; i < 5; i++) {
    sleep(1);
    printf("%s\n", str);
  }
}
```

```shell
$ ./cpu A & ; ./cpu B & ; ./cpu C & ; ./cpu D &
```

就能看到程序在“同时运行”的假象。

## 2.2 虚拟化内存

```c title='mem.c' hl_lines='4 9 11 12 16'
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

如果要得到和书中一样的效果，还需要关闭 ASLR 地址空间随机化，不然就算是虚拟内存，每次分配的地址也是不固定的。

```shell
$ echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```

如果编译时关掉 PIE，得到的地址会更“好看”些，更接近书中内容。

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

实验完尽快把 ASLR 改回去，以免对系统安全造成影响，现代 Linux 系统中 `/proc/sys/kernel/randomize_va_space` 内容一般都是 `2`，意为更强的随机化。

```shell
$ echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
```

!!! question "关键问题：如何将资源虚拟化"

    我们将在本书中回答一个核心问题：操作系统如何将资源虚拟化？这是关键问题。<br>
    为什么操作系统这样做？这不是主要问题，因为答案应该很明显：它让系统更易于使用。<br>
    因此，我们关注如何虚拟化：

    1. 操作系统通过哪些机制和策略来实现虚拟化？
    1. 操作系统如何有效地实现虚拟化？
    1. 需要哪些硬件支持？

## 2.3 并发

```c title='threads.c' hl_lines="1 25-28"
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

volatile int counter = 0;
int loops;

void *worker(void *arg) {
  int i;
  for (i = 0; i < loops; i++) {
    counter++;
  }
  return NULL;
}

int main(int argc, char *argv[]) {
  if (argc != 2) {
    fprintf(stderr, "usage: threads <value>\n");
    exit(1);
  }
  loops = atoi(argv[1]);
  pthread_t p1, p2;
  printf("Initial value : %d\n", counter);

  pthread_create(&p1, NULL, worker, NULL);
  pthread_create(&p2, NULL, worker, NULL);
  pthread_join(p1, NULL);
  pthread_join(p2, NULL);
  printf("Final value : %d\n", counter);
  return 0;
}
```

```shell
$ ./threads 100000
Initial value : 0
Final value : 140997
$ ./threads 100000
Initial value : 0
Final value : 119700
$ ./threads 100000
Initial value : 0
Final value : 129215
```

!!! question "关键问题：如何构建正确的并发程序"

    如果同一个内存空间中有很多并发执行的线程，如何构建一个正确工作的程序？

    1. 操作系统需要什么原语？
    1. 硬件应该提供哪些机制？
    1. 我们如何利用它们来解决并发问题？

## 2.4 持久性

其实就是文件系统。

```c title='io.c'
#include <assert.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
  int fd = open("/tmp/file", O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);
  assert(fd > -1);
  int rc = write(fd, "hello world\n", 13);
  assert(rc == 13);
  close(fd);
  return 0;
}
```

!!! question "关键问题：如何持久地存储数据"

    文件系统是操作系统的一部分，负责管理持久的数据。

    1. 持久性需要哪些技术才能正确地实现？
    1. 需要哪些机制和策略才能高性能地实现？
    1. 面对硬件和软件故障，可靠性如何实现？

## 2.6 简单历史

操作系统发展历史：

- 函数库
- 批处理系统
- 特权级和系统调用
- 多道程序
- 分时多任务
- 内存保护
- 并发
- ...
