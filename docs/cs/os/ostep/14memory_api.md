# 第 14 章 插叙：内存操作 API

上次插叙是 [5.Process API](./05process_api.md)，写了好多无聊的代码，好累。

## 14.1 内存类型

**栈内存** 和 **堆内存**。

```c
void func() {
    int x; // declares an integer on the stack
}
```

编译器负责确保在进入 `func` 函数的时候向栈上开辟空间，并在函数退出时释放内存。

需要内存长期存在，则需要把它们存在堆（heap）上，其中所有的申请和释放操作都由程序员显式完成。这不但麻烦，还危险。

```c
void func() {
    int *x = (int *) malloc(sizeof(int));
}
```

栈和堆的分配都发生在同一行，编译器首先看见 `#!c int *x` 时，知道为一个整型指针分配栈空间，随后当程序调用 `#!c malloc(sizeof(int))` 时，它会在堆上请求 `int` 大小的空间，返回此空间的地址，最终将此地址存在栈上。

## 14.2 malloc() 调用

```c
#include <stdlib.h>

void *malloc(size_t size);
```

关于参数：

- 尽量不要手动计算填写字面值（魔法数字），使用 `#!c sizeof` 或定义常量来代替；
- 特殊的内存大小，使用位运算来更清晰地表示，比如 1 KB 使用 `1 << 10`，2.5 MB 使用 `2 << 20 + 1 << 19`。

关于 `#!c sizeof`：

- 指针与所指内容大小不是一回事。使用 `#!c sizeof` 于指针时，得到的是指针本身的大小，而不是指针所指向的内存区域的大小；
- 用于结构体时，返回值包括对齐添加的填充字节大小；
- 用于字符串时，仔细斟酌是需要整个字符数组的大小，还是字符串的实际长度，前者使用 `#!c sizeof`，后者使用 `#!c strlen(c) + 1`。

## 14.3 free() 调用

```c
#include <stdlib.h>

void free(void *_Nullable ptr);
```

只需传入 `malloc()` 返回的指针，分配区域的大小不会也不该由用户传入，必须由内存分配库来记录追踪。

**如何** 释放并不难，**何时** 释放才是头疼的事情。

## 14.4 常见错误

### 忘记分配内存

```c
char *src = "hello";
char *dst; // oops! unallocated
strcpy(dst, src); // segfault and die
```

以上会引发段错误，正确版本：

```c
char *src = "hello";
char *dst = (char *) malloc(strlen(src) + 1);
strcpy(dst, src); // work properly
```

使用 `strdup`：

```c
char *src = "hello";
char *dst = strdup(src); // duplicates the string
```

### 没有分配足够的内存

缓冲区溢出 (buffer overflow)。

```c
char *src = "hello";
char *dst = (char *) malloc(strlen(src)); // too small!
strcpy(dst, src); // work properly
```

代码虽然能运行，但会在超过分配空间的末尾处写入一个字节。

### 忘记初始化分配的内存

正确地调用 `malloc()`，但忘记在新分配的数据类型中填写一些初始值，就会导致程序从堆里读到一些未知的东西。

内存的世界是混乱的，不走运的话，读到一些随机和有害的东西也是常事。

### 忘记释放内存

内存泄漏（memory leak），如果忘记释放内存，它就会一直留在那里，直到程序结束。

如果你的程序是一个需要长久运行的服务器呢？它不断地、缓慢地泄漏内存，最终在某个时刻把系统的内存占满，服务崩溃了。

带有垃圾回收（GC）的语言没什么帮助，如果仍然对某块内存存在引用，垃圾收集器就不会释放它。

### 在用完之前释放内存

悬挂指针（dangling pointer），释放后再使用那些地址的内存，称为 Use-After-Free，简称 UAF，是很严重的漏洞。

CTF 时间到……

[ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/use-after-free/](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/use-after-free/)

### 反复释放内存

重复释放（double free），同样是很严重的漏洞，会破坏内存管理数据结构，导致程序崩溃或者更严重的后果。

CTF 时间到……

[ir0nstone.gitbook.io/notes/types/heap/double-free](https://ir0nstone.gitbook.io/notes/types/heap/double-free)

### 错误地调用 free()

无效释放（invalid free），传入其他值（不是 `malloc` 的返回值）时，也可能被恶意利用。

!!! quote "补充：为什么在你的进程退出时没有内存泄露"

    当你编写一个短时间运行的程序时，可能会使用 malloc()分配一些空间。程序运行并即将完成：是否需要在退出前调用几次 free()？虽然不释放似乎不对，但在真正的意义上，没有任何内存会“丢失”。

    原因很简单：系统中实际存在两级内存管理。

    - 第一级是由操作系统执行的内存管理，操作系统在进程运行时将内存交给进程，并在进程退出（或以其他方式结束）时将其回收。
    - 第二级管理在每个进程中，例如在调用 malloc()和 free()时，在堆内管理。

    即使你没有调用 free()（并因此泄露了堆中的内存），操作系统也会在程序结束运行时，收回进程的所有内存（包括用于代码、栈，以及相关堆的内存页）。
    无论地址空间中堆的状态如何，操作系统都会在进程终止时收回所有这些页面，从而确保即使没有释放内存，也不会丢失内存。

## 14.5 底层操作系统支持

`malloc` 和 `free` 只是库调用，其中封装的是系统调用 `brk`。它用来改变程序分断（break）的位置：堆结束的位置。

`mmap` 调用可以从操作系统获取内存。通过传入正确的参数，`mmap` 可以在程序中创建一个匿名（anonymous）内存区域——这个区域不与任何特定文件相关联，而是与交换空间（swap space）相关联。

## 14.6 其他调用

- `calloc`: 分配的同时将其置零
- `realloc`: 创建一个新的更大的内存区域，将旧区域复制到其中

## 作业

!!! question

    1．首先，编写一个名为 null.c 的简单程序，它创建一个指向整数的指针，将其设置为 NULL，然后尝试对其进行释放内存操作。把它编译成一个名为 null 的可执行文件。当你运行这个程序时会发生什么？

!!! note "Answer"

    和别人答案不同，我认为这个操作是不会引发段错误的。

    ```c title="null.c"
    #include <stdlib.h>

    int main() {
        int* x = (int*)malloc(sizeof(int));
        x = NULL;
        free(x);
        return 0;
    }
    ```

    因为在大多数现代操作系统和 C 标准库实现中，释放 `NULL` 指针是安全的，不会有任何操作。至于一些答案给出的段错误，可能是尝试打印了 `*x`。

!!! question

    2. 接下来，编译该程序，其中包含符号信息（使用-g 标志）。这样做可以将本多信息放入可执行文件中，使调试器可以但问有关变量名称等的本多有用信息。通过输入 gdb null，在调试器下运行该程序，然后，一旦 gdb 运行，输入 run。gdb 显示什么信息？

!!! note "Answer"

    我的程序直接退出了，没有额外信息。如果加上 `#!c printf("%d\n", *x);` 就会停在段错误的地方：

    ```c
    ────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:64 ────
       0x55555555516b <main+18>        mov    QWORD PTR [rbp-0x8], rax
       0x55555555516f <main+22>        mov    QWORD PTR [rbp-0x8], 0x0
       0x555555555177 <main+30>        mov    rax, QWORD PTR [rbp-0x8]
     → 0x55555555517b <main+34>        mov    eax, DWORD PTR [rax]
       0x55555555517d <main+36>        mov    esi, eax
       0x55555555517f <main+38>        lea    rax, [rip+0xe7e]        # 0x555555556004
       0x555555555186 <main+45>        mov    rdi, rax
       0x555555555189 <main+48>        mov    eax, 0x0
       0x55555555518e <main+53>        call   0x555555555040 <printf@plt>
    ────────────────────────────────────────────────────────────────────────────────────────────────── source:null.c+7 ────
          2  #include <stdlib.h>
          3  
          4  int main() {
          5      int* x = (int*)malloc(sizeof(int));
          6      x = NULL;
                 // x=0x007fffffffe1a8  →  0x0000000000000000
     →    7      printf("%d\n", *x);
          8      free(x);
          9      return 0;
         10  }
    ────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
    [#0] Id 1, Name: "null", stopped 0x55555555517b in main (), reason: SIGSEGV
    ──────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
    [#0] 0x55555555517b → main()
    ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    ```

!!! question

    3．最后，对这个程序使用 valgrind 工具。我们将使用属于 valgrind 的 memcheck 工具来分析发生的情况。输入以下命令来运行程序：valgrind --leak-check=yes null。当你运行它时会发生什么？你能解释工具的输出吗？

!!! note "Answer"

    我没法正常使用 `valgrind`，排查了 `debuginfod`、环境变量等可能原因，还是没解决，换用 Docker 镜像运行也出了其他问题，我不想在这上面消太多时间了。

    以下是 [xxxyzz 的作业](https://github.com/xxyzz/ostep-hw/blob/master/14/README.md)：

    !!! quote

        ```
        ==25687== Invalid read of size 4
        ==25687==    at 0x104D4: main (null.c:7)
        ==25687==  Address 0x0 is not stack'd, malloc'd or (recently) free'd

        ==25687== Process terminating with default action of signal 11 (SIGSEGV)
        ==25687==  Access not within mapped region at address 0x0
        ==25687==    at 0x104D4: main (null.c:7)

        ==25687== HEAP SUMMARY:
        ==25687==     in use at exit: 4 bytes in 1 blocks
        ==25687==   total heap usage: 1 allocs, 0 frees, 4 bytes allocated
        ==25687== 
        ==25687== 4 bytes in 1 blocks are definitely lost in loss record 1 of 1
        ==25687==    at 0x4849CE0: calloc (vg_replace_malloc.c:711)
        ==25687==    by 0x104BF: main (null.c:5)
        ```

        `x` is at the address 0x0, it's not belong to the program.

!!! question

    4．编写一个使用 malloc()来分配内存的简单程序，但在退出之前忘记释放它。这个程序运行时会发生什么？你可以用 gdb 来查找它的任何问题吗？用 valgrind 那（再次使用 --leak-check=yes 标志）？

!!! note "Answer"

    ```c
    #include <stdio.h>
    #include <stdlib.h>

    int main() {
        int *x = (int *) malloc(sizeof(int));
        *x = 1;
        printf("%d\n", *x);
        return 0;
    }
    ```

    正常运行，正常退出，GDB 啥也没有。

    `valgrind` 的输出依旧来自 [xxxyzz 的作业](https://github.com/xxyzz/ostep-hw/blob/master/14/README.md)

    !!! quote

        ```
        ==26394== HEAP SUMMARY:
        ==26394==     in use at exit: 4 bytes in 1 blocks
        ==26394==   total heap usage: 2 allocs, 1 frees, 1,028 bytes allocated
        ==26394== 
        ==26394== 4 bytes in 1 blocks are definitely lost in loss record 1 of 1
        ==26394==    at 0x4847568: malloc (vg_replace_malloc.c:299)
        ==26394==    by 0x1048B: main (forget_free.c:5)
        ```

!!! question

    5．编写一个程序，使用 malloc 创建一个名为 data、大小为 100 的整数数组。然后，将 data[100]设置为 0。当你运行这个程序时会发生什么？当你使用 valgrind 运行这个程序时会发生什么？程序是否正确？

!!! note "Answer"

    ```c
    #include <stdlib.h>

    int main() {
        int* data = (int*)malloc(100 * sizeof(int));
        data[100] = 0;
        free(data);
        return 0;
    }
    ```

    什么也不会发生。

    `valgrind` 的输出依旧来自 [xxxyzz 的作业](https://github.com/xxyzz/ostep-hw/blob/master/14/README.md)

    !!! quote

        ```
        ==26677== Invalid write of size 4
        ==26677==    at 0x1086B1: main (size_100.c:6)
        ==26677==  Address 0x52381d0 is 0 bytes after a block of size 400 alloc'd
        ==26677==    at 0x4C330C5: malloc (vg_replace_malloc.c:442)
        ==26677==    by 0x1086A2: main (size_100.c:5)
        ```

        No. `data[100] = 0;` attempts to store the value 0 in the 101st element of the array. However, since the array was allocated for only 100 integers (indices 0 to 99). Accessing the 101st element lead to memory corruption.

    `data[100]` 赋值操作越界了。

!!! question

    6．创建一个分配整数数组的程序（如上所述），释放它们，然后尝试打印数组中某个元素的值。程序会运行吗？当你使用 valgrind 时会发生什么？

!!! note "Answer"

    ```c
    #include <stdio.h>
    #include <stdlib.h>

    int main() {
        int* data = (int*)malloc(100 * sizeof(int));
        free(data);
        printf("%d\n", data[0]);
        return 0;
    }
    ```

    运行后会打印不确定的内容。

    ```
    $ gcc -Wall -Wextra null.c -o null
    $ ./null && ./null && ./null
    1640640178
    1492092983
    1603621367
    ```

!!! question

    7．现在传递一个有趣的值来释放（例如，在上面分配的数组中间的一个指针）。会发生什么？你是否需要工具来找到这种类型的问题？

!!! note "Answer"

    ```c
    #include <stdlib.h>

    int main() {
        int* data = (int*)malloc(100 * sizeof(int));
        free(&data[1]);
        return 0;
    }
    ```

    ```
    $ gcc -Wall -Wextra null.c -o null && ./null
    null.c: 在函数‘main’中:
    null.c:5:5: 警告：‘free’ called on pointer ‘data’ with nonzero offset 4 [-Wfree-nonheap-object]
        5 |     free(&data[1]);
          |     ^~~~~~~~~~~~~~
    null.c:4:23: 附注：returned from ‘malloc’
        4 |     int* data = (int*)malloc(100 * sizeof(int));
          |                       ^~~~~~~~~~~~~~~~~~~~~~~~~
    free(): invalid pointer
    fish: Job 1, './null' terminated by signal SIGABRT (Abort)
    ```

!!! question

    8．尝试一些其他接口来分配内存。例如，创建一个简单的向量似的数据结构，以及使用 realloc()来管理向量的相关函数。使用数组来存储向量元素。当用户在向量中添加条目时，请使用 realloc()为其分配本多空间。这样的向量表现如何？它与链表相比如何？使用 valgrind来帮助你发现错误。

!!! note "Answer"

    代码是一点也不想写了。

    Dynamic array 与 Linked list 比的话，见 [en.wikipedia.org/wiki/Dynamic_array#Performance](https://en.wikipedia.org/wiki/Dynamic_array#Performance)

!!! question

    9．花本多时间阅读有关使用 gdb 和 valgrind 的信息。了解你的工具至关重要，花时间学习如何成为 UNIX 和 C 环境中的调试器专家。

!!! note "Answer"

    对不起，做不到。
