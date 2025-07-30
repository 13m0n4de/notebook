# 第 16 章 分段

之前一直将所有进程的地址空间完整地加载到内存中，栈和堆之间，有一大块“空闲”空间。

另外，如果剩余的物理内存无法提供连续区域来放置完整的地址空间，进程便无法运行。

这章讲的就是如何使用 **分段（Segmentation）** 解决它们。

## 16.1 分段：泛化的基址/界限

分段（segmentation）指的是将地址空间分为多个逻辑段（segment），给每个逻辑段都引入一对基址/界限寄存器。

一个段只是地址空间里的一个 **连续定长** 的区域，在典型的地址空间中有三个逻辑不同的段：代码、栈和堆。（实际更多）

| Virtual Address | Data    |
| --------------- | ------- |
| 0 KB - 2 KB     | Code    |
| 2 KB - 4 KB     | (free)  |
| 4 KB - 7 KB     | Heap ↓  |
| 7 KB - 14 KB    | (free)  |
| 14 KB - 16 KB   | Stack ↑ |

| Physics Address | Data         |
| --------------- | ------------ |
| 0 KB - 16 KB    | OS           |
| 16 KB - 26 KB   | (not in use) |
| 26 KB - 28 KB   | Stack ↑      |
| 28 KB - 32 KB   | (not in use) |
| 32 KB - 34 KB   | Code         |
| 34 KB - 37 KB   | Heap ↓       |
| 37 KB - 64 KB   | (not in use) |

| Segment | Base  | Size |
| ------- | ----- | ---- |
| Code    | 32 KB | 2 KB |
| Heap    | 34 KB | 3 KB |
| Stack   | 28 KB | 2 KB |

假设现在要引用虚拟地址 100（在代码段中），MMU 将基址值加上偏移量（100）得到实际的物理地址：100 + 32 KB = 32868。

然后它会检查该地址是否在界限内（100 小于 2 KB），发现是的，于是发起对物理地址 32868 的引用。

如果是虚拟地址 4200，它在堆上，不应该用它直接加上基址 34 KB，而是应该首先减去堆的偏移量，即该地址指的是这个段中的哪个字节。

因为堆从虚拟地址 4 K (4096) 开始，4200 的偏移量实际上是 4200 - 4096 = 104，然后用这个偏移量 (104)，加上基址寄存器中的物理地址（34 KB），得到真正的物理地址 34920。

## 16.2 我们引用哪个段

硬件在地址转换时使用段寄存器。

- 它如何知道段内的偏移量？
- 它如何知道地址引用哪个段？

显式（explicit）方式：用虚拟地址的开头几位标识不同的段。

```
13 12 11 10 09 08 07 06 05 04 03 02 01 00
^   ^ ^                                 ^
+---+ +---------------------------------+
  段                偏移量
```

在之前的例子中，如果前两位是 `00` 硬件就知道是属于代码段的地址，如果前两位是 `01` 则是堆地址。

虚拟地址 4200 的二进制形式如下：

```
13 12 11 10 09 08 07 06 05 04 03 02 01 00
 0  1  0  0  0  0  0  1  1  0  1  0  0  0
 ^  ^  ^                                ^
 +--+  +--------------------------------+
  段                偏移量
```

隐式（implicit）方式：硬件通过地址产生的方式来确定段。例如，地址由程序计数产生，那么它在代码段。如果是基于栈或基址指针，它一定在栈段。其他地址则在堆段。

听着就好不靠谱啊。

## 16.3 栈怎么办

栈比较特殊，它反向增长，硬件需要额外保存段的增长方向。

| Segment    | Base  | Size (max 4 K) | Grows Positive? |
| ---------- | ----- | -------------- | --------------- |
| Code `00`  | 32 KB | 2 KB           | 1               |
| Heap `01`  | 34 KB | 3 KB           | 1               |
| Stack `11` | 28 KB | 2 KB           | 0               |

假设要访问虚拟地址 15 KB，它应该映射到物理地址 27 KB。

该虚拟地址的二进制形式是：`11 1100 0000 0000`。

前两位 `11` 指定栈段，后几位 `1100 0000 0000` 指定偏移量 3 KB。

为了得到正确的反向偏移，需要用 3 KB 减去最大段地址 4 KB，得到反向偏移量 -1 KB。

再用反向偏移量加上基址，得到正确的物理地址 -1 KB + 28 KB = 27 KB。

## 16.4 支持共享

在一些地址空间之间共享某些内存段可以节省内存。

为了支持共享，需要添加新的功能，保护位（protection bit），用于标识程序能否读写该段，或执行其中代码。

通过将代码段标记为可读可执行，同样的代码可以被多个进程共享，而不用担心破坏隔离。

| Segment    | Base  | Size (max 4 K) | Grows Positive? | Protection  |
| ---------- | ----- | -------------- | --------------- | ----------- |
| Code `00`  | 32 KB | 2 KB           | 1               | Read-Excute |
| Heap `01`  | 34 KB | 3 KB           | 1               | Read-Write  |
| Stack `11` | 28 KB | 2 KB           | 0               | Read-Write  |

现在，除了需要检查虚拟地址是否越界，还需要检查特定访问是否允许（符合权限）。

## 16.5 细粒度与粗粒度的分段

!!! quote

    目前为止，我们的例子大多针对只有很少的几个段的系统（即代码、栈、堆）。
    我们可以认为这种分段是粗粒度的（coarse-grained），因为它将地址空间分成较大的、粗粒度的块。
    但是，一些早期系统（如 Multics）更灵活，允许将地址空间划分为大量较小的段，这被称为细粒度（fine-grained）分段。

    支持许多段需要进一步的硬件支持，并在内存中保存某种段表（segment table）。
    这种段表通常支持创建非常多的段，因此系统使用段的方式，可以比之前讨论的方式更灵活。
    例如，像 Burroughs B5000 这样的早期机器可以支持成千上万的段，有了操作系统和硬件的支持，编译器可以将代码段和数据段划分为许多不同的部分。
    当时的考虑是，通过更细粒度的段，操作系统可以更好地了解哪些段在使用哪些没有，从而可以更高效地利用内存。

## 16.6 操作系统支持

分段给操作系统带来了一些新任务：

- 在上下文切换时需要保存各个段寄存器内容；
- 管理物理内存的空闲空间，操作系统需要为新建的地址空间找到物理内存中的空闲位置。

第二个任务会遇到一个问题：物理内存很快就充满了许多空闲空间的小洞，因而很难分配给新的段，或扩大已有的段。这种问题被称为外部碎片（external fragmentation）。

非紧凑物理内存：

| Address       | Data         |
| ------------- | ------------ |
| 0 kB - 16 kB  | OS           |
| 16 kB - 24 kB | (not in use) |
| 24 kB - 32 kB | Allocated    |
| 32 kB - 40 kB | (not in use) |
| 40 kB - 48 kB | Allocated    |
| 48 kB - 56 kB | (not in use) |
| 56 kB - 64 kB | Allocated    |

紧凑物理内存：

| Address       | Data         |
| ------------- | ------------ |
| 0 kB - 16 kB  | OS           |
| 16 kB - 40 kB | Allocated    |
| 40 kB - 64 kB | (not in use) |

紧凑物理内存会重新安排原有的段，终止相关进程，再将它们的数据复制到连续的内存区域中去，改变它们的段寄存器中的值，指向新的物理地址。

但是内存紧凑成本很高，因为拷贝段是内存密集型的，会占用大量的处理器时间。

一种更简单的做法是利用空闲列表管理算法，试图保留大的内存块用于分配。

相关算法有成百上千种：

- best-fit
- worst-fit
- first-fit
- buddy

!!! quote "提示：如果有一千个解决方案，就没有特别好的"

    存在如此多不同的算法来尝试减少外部碎片，正说明了解决这个问题没有最好的办法。
    因此我们满足于找到一个合理的足够好的方案。
    唯一真正的解决办法就是（我们会在后续章节看到），完全避免这个问题，永远不要分配不同大小的内存块。

## 作业

!!! question

    1．先让我们用一个小地址空间来转换一些地址。这里有一组简单的参数和几个不同的随机种子。你可以转换这些地址吗？

    ```
    segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 0
    segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 1
    segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 2
    ```

!!! note "Answer"

    ```title="./segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 0"
    ARG seed 0
    ARG address space size 128
    ARG phys mem size 512

    Segment register information:

      Segment 0 base  (grows positive) : 0x00000000 (decimal 0)
      Segment 0 limit                  : 20

      Segment 1 base  (grows negative) : 0x00000200 (decimal 512)
      Segment 1 limit                  : 20

    Virtual Address Trace
      VA  0: 0x0000006c (decimal:  108) --> PA or segmentation violation?
      VA  1: 0x00000061 (decimal:   97) --> PA or segmentation violation?
      VA  2: 0x00000035 (decimal:   53) --> PA or segmentation violation?
      VA  3: 0x00000021 (decimal:   33) --> PA or segmentation violation?
      VA  4: 0x00000041 (decimal:   65) --> PA or segmentation violation?
    ```

    `0x0000006c` -> `1101100`，最高位为 `1`，128 - 108 = 20，20 = 20，正好在界限内，所以 VA 0 合法。
    `0x00000061` -> `1100001`，最高位为 `1`，128 - 97 = 23，23 > 20，超过了界限，VA 1 不合法。
    `0x00000035` -> `0110101`，最高位为 `0`，53 > 20，超过了界限，VA 2 不合法。

    以此类推。

---

!!! question

    1. 现在，让我们看看是否理解了这个构建的小地址空间（使用上面问题的参数）。段 0中最高的合法虚拟地址是什么？段 1 中最低的合法虚拟地址是什么？在整个地址空间中，最低和最高的非法地址是什么？最后，如何运行带有-A 标志的 segmentation.py 来测试你是否正确？

!!! note "Answer"

    基于上题第一条命令，段 0 最高合法虚拟地址是 `0x19`，段 1 最低合法虚拟地址是 `0x6c`

    ```title="./segmentation.py -a 128 -p 512 -b 0 -l 20 -B 512 -L 20 -s 1 -A 19,108,20,107 -c"
    ARG seed 1
    ARG address space size 128
    ARG phys mem size 512

    Segment register information:

      Segment 0 base  (grows positive) : 0x00000000 (decimal 0)
      Segment 0 limit                  : 20

      Segment 1 base  (grows negative) : 0x00000200 (decimal 512)
      Segment 1 limit                  : 20

    Virtual Address Trace
      VA  0: 0x00000013 (decimal:   19) --> VALID in SEG0: 0x00000013 (decimal:   19)
      VA  1: 0x0000006c (decimal:  108) --> VALID in SEG1: 0x000001ec (decimal:  492)
      VA  2: 0x00000014 (decimal:   20) --> SEGMENTATION VIOLATION (SEG0)
      VA  3: 0x0000006b (decimal:  107) --> SEGMENTATION VIOLATION (SEG1)
    ```

---

!!! question

    3．假设我们在一个 128 字节的物理内存中有一个很小的 16 字节地址空间。你会设置什么样的基址和界限，以便让模拟器为指定的地址流生成以下转换结果：有效，有效，违规，违反，有效，有效？假设用以下参数：

    ```
    segmentation.py -a 16 -p 128
    -A 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    --b0 ? --l0 ? --b1 ? --l1 ?
    ```

!!! note "Answer"

    ```title="./segmentation.py -a 16 -p 128 -A 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 --b0 0 --l0 2 --b1 16 --l1 2 -c"
    ARG seed 0
    ARG address space size 16
    ARG phys mem size 128

    Segment register information:

      Segment 0 base  (grows positive) : 0x00000000 (decimal 0)
      Segment 0 limit                  : 2

      Segment 1 base  (grows negative) : 0x00000010 (decimal 16)
      Segment 1 limit                  : 2

    Virtual Address Trace
      VA  0: 0x00000000 (decimal:    0) --> VALID in SEG0: 0x00000000 (decimal:    0)
      VA  1: 0x00000001 (decimal:    1) --> VALID in SEG0: 0x00000001 (decimal:    1)
      VA  2: 0x00000002 (decimal:    2) --> SEGMENTATION VIOLATION (SEG0)
      VA  3: 0x00000003 (decimal:    3) --> SEGMENTATION VIOLATION (SEG0)
      VA  4: 0x00000004 (decimal:    4) --> SEGMENTATION VIOLATION (SEG0)
      VA  5: 0x00000005 (decimal:    5) --> SEGMENTATION VIOLATION (SEG0)
      VA  6: 0x00000006 (decimal:    6) --> SEGMENTATION VIOLATION (SEG0)
      VA  7: 0x00000007 (decimal:    7) --> SEGMENTATION VIOLATION (SEG0)
      VA  8: 0x00000008 (decimal:    8) --> SEGMENTATION VIOLATION (SEG1)
      VA  9: 0x00000009 (decimal:    9) --> SEGMENTATION VIOLATION (SEG1)
      VA 10: 0x0000000a (decimal:   10) --> SEGMENTATION VIOLATION (SEG1)
      VA 11: 0x0000000b (decimal:   11) --> SEGMENTATION VIOLATION (SEG1)
      VA 12: 0x0000000c (decimal:   12) --> SEGMENTATION VIOLATION (SEG1)
      VA 13: 0x0000000d (decimal:   13) --> SEGMENTATION VIOLATION (SEG1)
      VA 14: 0x0000000e (decimal:   14) --> VALID in SEG1: 0x0000000e (decimal:   14)
      VA 15: 0x0000000f (decimal:   15) --> VALID in SEG1: 0x0000000f (decimal:   15)
    ```

---

!!! question

    4．假设我们想要生成一个问题，其中大约 90%的随机生成的虚拟地址是有效的（即不产生段异常）。你应该如何配置模拟器来做到这一点？哪些参数很重要？

!!! note "Answer"

    界限调整到地址空间的 90%：`-l` = 0.9 * `-a`。

---

!!! question

    5．你可以运行模拟器，使所有虚拟地址无效吗？怎么做到？

!!! note "Answer"

    把界限调成 0，`-l 0 -L 0`
