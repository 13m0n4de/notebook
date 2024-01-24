# 第 6 章 机制：受限直接执行

这章是讲特权级机制和进程调度的，介绍虚拟化 CPU 过程中会遇到的问题以及解决方案，对应：

- [rCore-Tutorial-Book 特权级机制](https://rcore-os.cn/rCore-Tutorial-Book-v3/chapter2/1rv-privilege.html)
- [rCore-Tutorial-Book 多道程序与分时多任务](https://rcore-os.cn/rCore-Tutorial-Book-v3/chapter3/index.html)

## 6.1 基本技巧：受限直接执行

“受限”和“直接执行”。

直接执行指的是直接在 CPU 上运行程序。操作系统启动程序的时候创建一个进程，把程序的代码从磁盘加载到内存里，找到入口点，跳转进去运行。

| 操作系统                                                           | 程序                                    |
| :------------------------------------------------------------- | :------------------------------------ |
| 在进程列表上创建条目<br>为程序分配内存<br>将程序加载到内存中<br>根据 `argc` / `argv` 设置程序栈 |                                       |
| 清除寄存器<br>执行 `call main()` 方法                                   |                                       |
|                                                                | 执行 `main()`<br> 从 `main` 中执行 `return` |
| 释放进程的内存将进程从进程列表清除                                              |                                       |

这种方法在虚拟化 CPU 时会产生两个问题：

1. 怎么确保程序不做任何不希望它做的事，同时还能高效运行
1. 如何让进程停下来并切换到另一个进程

“受限”，就是为了解决这些问题的。

## 6.2 问题 1：受限制的操作

通过引入新的处理器模式，可以让进程在不同程度上受限。

比如在 **用户模式** 下进程不能发送 I/O 请求，会导致处理器引发异常，操作系统可能会终止进程。而 **内核模式** 可以做这些受限指令，操作系统内核就运行在内核模式下。

如果用户希望执行某种特权操作（如从磁盘读取），需要执行 **系统调用** ，这是内核向用户程序暴露的某些关键功能，譬如访问文件系统、创建销毁进程、与其他进程通信，以及分配更多内存。

如果要执行系统调用，需要执行特殊的指令，称为 陷入（Trap），它使程序控制流跳入内核并将特权级别提升到内核模式，如此一来就可以执行特权操作了，完成后再调用一个特殊的指令从陷入返回。

OSTEP 翻译为“陷阱”，rCore 翻译为“陷入”，总之...[*It's A Trap!*](https://www.youtube.com/watch?v=4F4qzPbcFiA)

> 硬件通过提供不同的执行模式来协助操作系统。在用户模式（user mode）下，应用程序不能完全访问硬件资源。在内核模式（kernel mode）下，操作系统可以访问机器的全部资源。还提供了陷入（trap）内核和从陷阱返回（return-from-trap）到用户模式程序的特别说明，以及一些指令，让操作系统告诉硬件陷阱表（trap table）在内存中的位置。

!!! note "补充：为什么系统调用看起来像过程调用"
    在 C 语言中 `open()`、`read()` 看起来完全是过程调用的形式，系统是如何知道它是一个系统调用的呢？<br>
    原因很简单，它就是一个过程调用，但隐藏在内部的是陷入指令。<br>
    当调用 `open()` 时正在执行对 C 库的过程调用，但在库函数中是手工编码的汇编指令，为了正确地系统调用。<br>
    所以，能直接调用库函数来陷入操作系统是因为有人已经为你写了汇编。

| 操作系统@启动（内核模式）                                                                     | 硬件                                  |                                     |
| :-------------------------------------------------------------------------------- | :---------------------------------- | :---------------------------------- |
| 初始化陷阱表                                                                            |                                     |                                     |
|                                                                                   | 记住系统调用处理程序的地址                       |                                     |
| **操作系统@运行（内核模式）**                                                                 | **硬件**                              | **程序（应用模式）**                        |
| 在进程列表上创建条目<br>为程序分配内存<br>将程序加载到内存中<br>根据 `argv` 设置程序栈<br>用寄存器/程序计数器填充内核栈<br>从陷阱返回 |                                     |                                     |
|                                                                                   | 从内核栈恢复寄存器<br>转向用户模式<br>跳到 `main`    |                                     |
|                                                                                   |                                     | 运行 `main`<br>……<br>调用系统调用<br>陷入操作系统 |
|                                                                                   | 将寄存器保存到内核栈<br>转向内核模式<br>跳到陷阱处理程序    |                                     |
| 处理陷阱<br>做系统调用的工作<br>从陷阱返回                                                         |                                     |                                     |
|                                                                                   | 从内核栈恢复寄存器<br>转向用户模式<br>跳到陷阱之后的程序计数器 |                                     |
|                                                                                   |                                     | ……从 `main` 返回   陷入（通过 `exit()`）     |
| 释放进程的内存将进程<br>从进程列表中清除                                                            |                                     |                                     |

## 6.3 问题 2：在进程之间切换

如果进程在 CPU 上运行，那操作系统就“没有运行”，如果操作系统没运行，它就没办法切换进程了，所以重点在于 **操作系统如何重新获得 CPU 的控制权**。

### 协作式调度：等待系统调用

协作式调度（Cooperative Scheduling）里，操作系统相信进程会合理运行，运行一段时间就通过 `yield` 主动把 CPU 交回操作系统。

如果某个进程无意或有意进入无限循环，不使用 `yield` ，也不进行系统调用让操作系统掌控主动权，那就我们就被永远地“困住”了。

（当然，还有万能地解决方式———重启）

### 非协作方式：操作系统进行控制

关于操作系统如何重获 CPU 的控制权，人们找到了一个答案：**时钟中断（timer interrupt）**。

时钟设备可以编程为每隔几毫秒产生一次中断，中断时当前正在运行的进程会被暂停，转而运行操作系统中预先配置的中断处理程序（interrupt handler），这样操作系统就重新获得了 CPU 的控制权。

### 保存和恢复上下文

> 既然操作系统已经重新获得了控制权，无论是通过系统调用协作，还是通过时钟中断更强制执行，都必须决定：是继续运行当前正在运行的进程，还是切换到另一个进程。这个决定是由调度程序（scheduler）做出的，它是操作系统的一部分。
>
> 如果决定进行切换，OS 就会执行一些底层代码，即所谓的上下文切换（context switch）。上下文切换在概念上很简单：操作系统要做的就是为当前正在执行的进程保存一些寄存器的值（例如，到它的内核栈），并为即将执行的进程恢复一些寄存器的值（从它的内核栈）。这样一来，操作系统就可以确保最后执行从陷阱返回指令时，不是返回到之前运行的进程，而是继续执行另一个进程。

| 操作系统@启动（内核模式）                                                                         | 硬件                                             |              |
| :------------------------------------------------------------------------------------ | :--------------------------------------------- | :----------- |
| 初始化陷阱表                                                                                |                                                |              |
|                                                                                       | 记住以下地址：<br>  系统调用处理程序<br>  时钟处理程序              |              |
| 启动中断时钟                                                                                |                                                |              |
|                                                                                       | 启动时钟<br>每隔 x ms 中断 CPU                         |              |
| **操作系统@运行（内核模式）**                                                                     | **硬件**                                         | **程序（应用模式）** |
|                                                                                       |                                                | 进程 A……       |
|                                                                                       | 时钟中断<br>将寄存器（A）保存到内核栈（A）<br>转向内核模式<br>跳到陷阱处理程序 |              |
| 处理陷阱<br>调用 `switch()` 例程<br>  将寄存器（A）保存到进程结构（A）<br>  将进程结构（B）恢复到寄存器（B）<br>从陷阱返回（进入 B） |                                                |              |
|                                                                                       | 从内核栈（B）恢复寄存器（B）<br>转向用户模式<br>跳到 B 的程序计数器       |              |
|                                                                                       |                                                | 进程 B……       |

## 对进程调度方式的总结

第四章作业中的 `process-run.py` 实现了一个协作式的进程调度框架，进程在执行一定数量的指令后主动让出 CPU ，或者在发起 I/O 操作后等待 I/O 完成。

协作式调度的特点是进程自愿地让出 CPU 控制权，在简单易用的同时也带来了一些问题：

- 一个进程崩溃或陷入无限循环可能会影响整个系统
- 不适合处理实时交互的任务

于是就衍生出了 **抢占式调度** ，运行一个进程一段时间，然后运行另一个进程，如此轮换。

实现起来会更加复杂，但拥有了更强的系统稳定性，更适合处理实时任务。

引用 [rCore-Tutorial-Book 分时多任务系统的背景](https://rcore-os.cn/rCore-Tutorial-Book-v3/chapter3/4time-sharing-system.html#id4) 的介绍：

> 从现在的眼光来看，当时的应用更多是一种 后台应用 (Background Application) ，在将它加入执行队列之后我们只需定期确认它的运行状态。<br>
> 而随着技术的发展，涌现了越来越多的 交互式应用 (Interactive Application) ，它们要达成的一个重要目标就是提高用户（应用的使用者和开发者）操作的响应速度，减少 延迟 （Latency），这样才能优化应用的使用体验和开发体验。<br>
>
> 对于这些应用而言，即使需要等待外设或某些事件，它们也不会倾向于主动 yield 交出 CPU 使用权，因为这样可能会带来无法接受的延迟。<br>
> 也就是说，应用之间更多的是互相竞争宝贵的硬件资源，而不是相互合作。
>
> 如果应用自己很少 yield ，操作系统内核就要开始收回之前下放的权力，由它自己对 CPU 资源进行集中管理并合理分配给各应用，这就是内核需要提供的任务调度能力。<br>
> 我们可以将多道程序的调度机制分类成
>
> - 协作式调度 (Cooperative Scheduling) ，因为它的特征是：只要一个应用不主动 yield 交出 CPU 使用权，它就会一直执行下去。
> - 与之相对， 抢占式调度 (Preemptive Scheduling) 则是应用 随时 都有被内核切换出去的可能。

## 作业

```c
#define _GNU_SOURCE
#include <assert.h>
#include <sched.h>
#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>

#define ITERATIONS 1000000.0

int main(void) {
    // system call
    struct timeval time_before, time_after;

    gettimeofday(&time_before, NULL);
    for (size_t i = 0; i < ITERATIONS; i++) {
        getpid();
    }
    gettimeofday(&time_after, NULL);

    double elapsed_time = (1000000 * time_after.tv_sec + time_after.tv_usec) -
                          (1000000 * time_before.tv_sec + time_before.tv_usec);
    printf("the average time of system call: %.2f us\n",
           elapsed_time / ITERATIONS * 1000);

    // context switch
    int first_pipe[2];
    int second_pipe[2];
    cpu_set_t cpu_set;
    CPU_ZERO(&cpu_set);
    CPU_SET(0, &cpu_set);

    assert(pipe(first_pipe) == 0);
    assert(pipe(second_pipe) == 0);

    pid_t pid = fork();
    assert(pid >= 0);

    if (pid == 0) {
        sched_setaffinity(getpid(), sizeof(cpu_set_t), &cpu_set);

        for (size_t i = 0; i < ITERATIONS; i++) {
            write(first_pipe[0], NULL, 0);
            read(second_pipe[1], NULL, 0);
        }
    } else {
        sched_setaffinity(getpid(), sizeof(cpu_set_t), &cpu_set);

        gettimeofday(&time_before, NULL);
        for (size_t i = 0; i < ITERATIONS; i++) {
            write(second_pipe[0], NULL, 0);
            read(first_pipe[1], NULL, 0);
        }
        gettimeofday(&time_after, NULL);

        double elapsed_time =
            (1000000 * time_after.tv_sec + time_after.tv_usec) -
            (1000000 * time_before.tv_sec + time_before.tv_usec);
        printf("the average time of context switch: %.2f us\n",
               elapsed_time / ITERATIONS * 1000);
    }

    return 0;
}
```

```title='gcc test.c -o test -Wall -Wextra && ./test'
the average time of system call: 128.36 us
the average time of context switch: 520.91 us
```

我也不知道这个数据对不对，GPT 说上下文切换基本在纳秒级，可能是对的吧。
