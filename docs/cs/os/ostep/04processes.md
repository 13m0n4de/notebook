# 第 4 章 抽象：进程

这章介绍了进程的概念，为了虚拟化 CPU 做铺垫。

进程是一个正在运行的程序，既然正在运行，那就肯定有状态，包括程序的寄存器值以及用到的内存值，操作系统需要分配一些内存将它们需要保存下来。

保存是为了切换，切换是因为需要调度，调度是为了最大化利用系统资源。

章节末尾习题实现的是类似“多道程序”的调度方法。

摘一下 [rCore 多道程序与协作式调度](https://rcore-os.cn/rCore-Tutorial-Book-v3/chapter3/3multiprogramming.html) 的内容：

> 多道程序的思想在于：内核同时管理多个应用。<br>
> 如果外设处理 I/O 的时间足够长，那我们可以先进行任务切换去执行其他应用；在某次切换回来之后，应用再次读取设备寄存器，发现 I/O 请求已经处理完毕了，那么就可以根据返回的 I/O 结果继续向下执行了。<br>
> 这样的话，只要同时存在的应用足够多，就能一定程度上隐藏 I/O 外设处理相对于 CPU 的延迟，保证 CPU 不必浪费时间在等待外设上，而是几乎一直在进行计算。

为了实现任意切换的“无限”多 CPU 的假象，我们需要 **虚拟化 CPU** 和 **上下文切换** 。

## 作业

!!! question
    1．用以下标志运行程序：./process-run.py -l 5:100,5:100。CPU 利用率（CPU 使用时间的百分比）应该是多少？为什么你知道这一点？利用 -c 标记查看你的答案是否正确。

!!! note
    `5` 是指令数量，`100` 是 **不切换** IO 的机率，所以这是两个五条指令的纯 CPU 程序，它们应该会一直使用 CPU ，利用率为 100% 。

    ```title='python process-run.py -l 5:100,5:100 -c'
    Time        PID: 0        PID: 1           CPU           IOs
      1        RUN:cpu         READY             1
      2        RUN:cpu         READY             1
      3        RUN:cpu         READY             1
      4        RUN:cpu         READY             1
      5        RUN:cpu         READY             1
      6           DONE       RUN:cpu             1
      7           DONE       RUN:cpu             1
      8           DONE       RUN:cpu             1
      9           DONE       RUN:cpu             1
     10           DONE       RUN:cpu             1
    ```

!!! question
    2．现在用这些标志运行：./process-run.py -l 4:100,1:0。这些标志指定了一个包含 4 条指令的进程（都要使用 CPU），并且只是简单地发出 I/O 并等待它完成。完成这两个进程需要多长时间？利用-c 检查你的答案是否正确。

!!! note
    IO 操作时长默认值是 `5` ，所以一共需要 `4 + 7 = 11` 个时间单位，因为 `io` 和 `io_done` 操作也占用时间，所以是 `7` 不是 `5` 。

    ```title='python process-run.py -l 4:100,1:0 -c'
    Time        PID: 0        PID: 1           CPU           IOs
      1        RUN:cpu         READY             1
      2        RUN:cpu         READY             1
      3        RUN:cpu         READY             1
      4        RUN:cpu         READY             1
      5           DONE        RUN:io             1
      6           DONE       BLOCKED                           1
      7           DONE       BLOCKED                           1
      8           DONE       BLOCKED                           1
      9           DONE       BLOCKED                           1
     10           DONE       BLOCKED                           1
     11*          DONE   RUN:io_done             1
    ```

!!! question
    3．现在交换进程的顺序：./process-run.py -l 1:0,4:100。现在发生了什么？交换顺序是否重要？为什么？同样，用-c 看看你的答案是否正确。

!!! note
    如果先 `RUN:io` 的话，就会节省很多时间，因为之前程序 0 结束了才开始 IO ，浪费了一些。

    ```title='python process-run.py -l 1:0,4:100 -c'
    Time        PID: 0        PID: 1           CPU           IOs
      1         RUN:io         READY             1
      2        BLOCKED       RUN:cpu             1             1
      3        BLOCKED       RUN:cpu             1             1
      4        BLOCKED       RUN:cpu             1             1
      5        BLOCKED       RUN:cpu             1             1
      6        BLOCKED          DONE                           1
      7*   RUN:io_done          DONE             1
    ```

!!! question
    4．现在探索另一些标志。一个重要的标志是-S，它决定了当进程发出 I/O 时系统如何反应。将标志设置为 SWITCH_ON_END，在进程进行 I/O 操作时，系统将不会切换到另一个进程，而是等待进程完成。当你运行以下两个进程时，会发生什么情况？一个执行 I/O，另一个执行 CPU 工作。（-l 1:0,4:100 -c -S SWITCH_ON_END）

!!! note
    如果在 IO 操作的程序不让出 CPU 的话，其他程序只能一直等待了。

    ```title='python process-run.py -l 1:0,4:100 -c -S SWITCH_ON_END'
    Time        PID: 0        PID: 1           CPU           IOs
      1         RUN:io         READY             1
      2        BLOCKED         READY                           1
      3        BLOCKED         READY                           1
      4        BLOCKED         READY                           1
      5        BLOCKED         READY                           1
      6        BLOCKED         READY                           1
      7*   RUN:io_done         READY             1
      8           DONE       RUN:cpu             1
      9           DONE       RUN:cpu             1
     10           DONE       RUN:cpu             1
     11           DONE       RUN:cpu             1
    ```

!!! question
    5．现在，运行相同的进程，但切换行为设置，在等待 I/O 时切换到另一个进程（-l 1:0,4:100-c -S SWITCH_ON_IO）。现在会发生什么？利用-c 来确认你的答案是否正确。

!!! note
    `SWITCH_ON_IO` 就是默认的参数，所以和上上次运行结果不会有差别。

    ```title='python process-run.py -l 1:0,4:100 -c -S SWITCH_ON_IO'
    Time        PID: 0        PID: 1           CPU           IOs
      1         RUN:io         READY             1
      2        BLOCKED       RUN:cpu             1             1
      3        BLOCKED       RUN:cpu             1             1
      4        BLOCKED       RUN:cpu             1             1
      5        BLOCKED       RUN:cpu             1             1
      6        BLOCKED          DONE                           1
      7*   RUN:io_done          DONE             1
    ```

!!! question
    6．另一个重要的行为是 I/O 完成时要做什么。利用-I IO_RUN_LATER，当 I/O 完成时，发出它的进程不一定马上运行。相反，当时运行的进程一直运行。当你运行这个进程组合时会发生什么？（./process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_LATER -c -p）系统资源是否被有效利用？

!!! note
    程序 0 运行完不会立马运行，会切到 `READY` 状态，等待其他程序交出 CPU 使用权。<br>
    浪费了一些系统资源，程序 2 和 3 一直占用着 CPU 导致程序 1 没法进行下一个 IO 操作，如果 IO 操作 与 CPU 操作一起执行就会更节省。

    ```title='python process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_LATER -c -p'
    Time        PID: 0        PID: 1        PID: 2        PID: 3           CPU           IOs
      1         RUN:io         READY         READY         READY             1
      2        BLOCKED       RUN:cpu         READY         READY             1             1
      3        BLOCKED       RUN:cpu         READY         READY             1             1
      4        BLOCKED       RUN:cpu         READY         READY             1             1
      5        BLOCKED       RUN:cpu         READY         READY             1             1
      6        BLOCKED       RUN:cpu         READY         READY             1             1
      7*         READY          DONE       RUN:cpu         READY             1
      8          READY          DONE       RUN:cpu         READY             1
      9          READY          DONE       RUN:cpu         READY             1
     10          READY          DONE       RUN:cpu         READY             1
     11          READY          DONE       RUN:cpu         READY             1
     12          READY          DONE          DONE       RUN:cpu             1
     13          READY          DONE          DONE       RUN:cpu             1
     14          READY          DONE          DONE       RUN:cpu             1
     15          READY          DONE          DONE       RUN:cpu             1
     16          READY          DONE          DONE       RUN:cpu             1
     17    RUN:io_done          DONE          DONE          DONE             1
     18         RUN:io          DONE          DONE          DONE             1
     19        BLOCKED          DONE          DONE          DONE                           1
     20        BLOCKED          DONE          DONE          DONE                           1
     21        BLOCKED          DONE          DONE          DONE                           1
     22        BLOCKED          DONE          DONE          DONE                           1
     23        BLOCKED          DONE          DONE          DONE                           1
     24*   RUN:io_done          DONE          DONE          DONE             1
     25         RUN:io          DONE          DONE          DONE             1
     26        BLOCKED          DONE          DONE          DONE                           1
     27        BLOCKED          DONE          DONE          DONE                           1
     28        BLOCKED          DONE          DONE          DONE                           1
     29        BLOCKED          DONE          DONE          DONE                           1
     30        BLOCKED          DONE          DONE          DONE                           1
     31*   RUN:io_done          DONE          DONE          DONE             1

    Stats: Total Time 31
    Stats: CPU Busy 21 (67.74%)
    Stats: IO Busy  15 (48.39%)
    ```

!!! question
    7．现在运行相同的进程，但使用-I IO_RUN_IMMEDIATE 设置，该设置立即运行发出I/O 的进程。这种行为有何不同？为什么运行一个刚刚完成 I/O 的进程会是一个好主意？

!!! note
    I/O 完成，一般意味着进程已经获得了执行所需的资源。立即运行这样的进程可以减少在准备状态下的等待时间。<br>
    当然这里因为它只有 IO 操作，所以一直运行它总没错。

    ```title='python process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_IMMEDIATE -c -p'
    Time        PID: 0        PID: 1        PID: 2        PID: 3           CPU           IOs
      1         RUN:io         READY         READY         READY             1
      2        BLOCKED       RUN:cpu         READY         READY             1             1
      3        BLOCKED       RUN:cpu         READY         READY             1             1
      4        BLOCKED       RUN:cpu         READY         READY             1             1
      5        BLOCKED       RUN:cpu         READY         READY             1             1
      6        BLOCKED       RUN:cpu         READY         READY             1             1
      7*   RUN:io_done          DONE         READY         READY             1
      8         RUN:io          DONE         READY         READY             1
      9        BLOCKED          DONE       RUN:cpu         READY             1             1
     10        BLOCKED          DONE       RUN:cpu         READY             1             1
     11        BLOCKED          DONE       RUN:cpu         READY             1             1
     12        BLOCKED          DONE       RUN:cpu         READY             1             1
     13        BLOCKED          DONE       RUN:cpu         READY             1             1
     14*   RUN:io_done          DONE          DONE         READY             1
     15         RUN:io          DONE          DONE         READY             1
     16        BLOCKED          DONE          DONE       RUN:cpu             1             1
     17        BLOCKED          DONE          DONE       RUN:cpu             1             1
     18        BLOCKED          DONE          DONE       RUN:cpu             1             1
     19        BLOCKED          DONE          DONE       RUN:cpu             1             1
     20        BLOCKED          DONE          DONE       RUN:cpu             1             1
     21*   RUN:io_done          DONE          DONE          DONE             1

    Stats: Total Time 21
    Stats: CPU Busy 21 (100.00%)
    Stats: IO Busy  15 (71.43%)
    ```

!!! question
    8．现在运行一些随机生成的进程，例如-s 1 -l 3:50,3:50, -s 2 -l 3:50,3:50, -s 3 -l 3:50,3:50。看看你是否能预测追踪记录会如何变化？当你使用-I IO_RUN_IMMEDIATE 与-I IO_RUN_LATER 时会发生什么？当你使用-S SWITCH_ON_IO 与-S SWITCH_ON_END 时会发生什么？

!!! note
    累了，测不动了。
