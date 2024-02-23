# 第 18 章 分页：介绍

十六章尝试使用分段来解决空间管理问题，十七章尝试使用各种空闲空间管理策略来减少分段带来的碎片问题。

另一种方式叫做 **分页 (Paging)** ，采用了固定长度的分片，从根本上避免了碎片（外部碎片）。

## 18.1 一个简单例子

以下例子展示了一个只有 64 字节的小地址空间，有 4 个 16 字节的页。

```
 0 +------------+
   |            | page 0 of the address space
16 +------------+
   |            | page 1
32 +------------+
   |            | page 2
48 +------------+
   |            | page 3
64 +------------+
```

物理内存也由一组固定大小的槽子块组成吗，下面的例子中有 8 个 页帧，虚拟地址空间的页放在物理内存的不同位置。

```
 0  +-----------------+
    | reserved for OS | page frame 0 of physical memory
16  +-----------------+
    |     (unused)    | page frame 1
32  +-----------------+
    |   page 3 of AS  | page frame 2
48  +-----------------+
    |   page 0 of AS  | page frame 3
64  +-----------------+
    |     (unused)    | page frame 4
80  +-----------------+
    |   page 2 of AS  | page frame 5
96  +-----------------+
    |     (unused)    | page frame 6
112 +-----------------+
    |   page 1 of AS  | page frame 7
128 +-----------------+
```

分页有许多有点，最大的改进就是 **灵活性**：通过完善的分页方法，操作系统能够高效地提供地址空间的抽象，不管进程如何使用地址空间。例如，我们不会假定堆和栈的增长方向，以及它们如何使用。

另一个优点是 **空闲空间管理的简单性**，如果操作系统希望将 64 字节的小地址空间放到 8 页的物理地址空间中，它只要找到 4 个空闲页。

为了记录地址空间的每个虚拟页放在物理内存中的位置，操作系统通常为 **每个进程** 保存一个数据结构，称为 **页表 (pasge table)**。

页表的作用是为地址空间的每个虚拟页面保存地址转换 (address translation)，从而让我们知道每个页在物理内存中的位置。

在上面的例子中，页表具有以下条目：

- VP 0 -> PF 3 (Virtual Page 0 -> Physical Frame 3)
- VP 1 -> PF 7
- VP 2 -> PF 5
- VP 3 -> PF 2

假设此时该进程正在访问内存：

```asm
movl <virtual address>, %eax
```

为了转换该虚拟地址，必须首先将它分为两个组件：

- 虚拟页面号 (virtual page number, VPN)
- 页内偏移量 (offset)

对于这个例子，因为进程的虚拟地址空间是 64 字节，我们的虚拟地址总共需要 6 位 ($ 2^{6} = 64 $)：

```
+-----+-----+-----+-----+-----+-----+
| Va5 | Va4 | Va3 | Va2 | Va1 | Va0 |
+-----+-----+-----+-----+-----+-----+
```

其中 `Va5` 是虚拟地址的最高位，`Va0` 是最低位。因为我们知道页的大小（16 字节），所以可以进一步划分虚拟地址：

```
     VPN                OFFSET
      |                   |
+-----+-----+ +-----+-----+-----+-----+
| Va5 | Va4 | | Va3 | Va2 | Va1 | Va0 |
+-----+-----+ +-----+-----+-----+-----+
```

页面大小为 16 字节，位于 64 字节的地址空间，因此需要四个虚拟页面号。

地址的前两位表示虚拟页面号，后四位表示该页的偏移量。

假设刚刚的汇编加载的是虚拟地址 `21`：

```asm
movl 21, %eax
```

将 `21` 的二进制形式 `010101`：

```

   VPN          OFFSET
    |             |
+---+---+ +---+---+---+---+
| 0 | 1 | | 0 | 1 | 0 | 1 |
+---+---+ +---+---+---+---+
```

虚拟地址 `21` 在虚拟页 `01` 的第五 `0101` 个字节处。

我们先通过 VPN 找到虚拟页 1 所在物理帧，在上面的例子中，物理帧号 (PFN) 为 7（二进制 `111`）。

通过将 VPN 替换为 PFN 来转换虚拟地址：

```
        +---+---+---+---+---+---+
VA      | 0 | 1 | 0 | 1 | 0 | 1 |
        +---+---+---+---+---+---+
          |   |   |   |   |   |
   +-------------+|   |   |   |
   |   Address   ||   |   |   |
   | Translation ||   |   |   |
   +-------------+|   |   |   |
      |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+
PA  | 1 | 1 | 1 | 0 | 1 | 0 | 1 |
    +---+---+---+---+---+---+---+
```

得到最终的物理地址 `11110101` 十进制 `117`。

## 18.2 页表存在哪里

页表可以存储在操作系统的虚拟内存中：

```
 0  +-----------------+
    |    page table   | page frame 0 of physical memory
    |     3 7 5 2     |
16  +-----------------+
    |     (unused)    | page frame 1
32  +-----------------+
    |   page 3 of AS  | page frame 2
48  +-----------------+
    |   page 0 of AS  | page frame 3
64  +-----------------+
    |     (unused)    | page frame 4
80  +-----------------+
    |   page 2 of AS  | page frame 5
96  +-----------------+
    |     (unused)    | page frame 6
112 +-----------------+
    |   page 1 of AS  | page frame 7
128 +-----------------+
```

但这种简单结构的页表可能会非常大，让操作系统占用巨大的内存。

!!! quote
    例如，想象一个典型的 32 位地址空间，带有 4KB 的页。这个虚拟地址分成 20 位的 VPN 和 12 位的偏移量（回想一下，1KB 的页面大小需要 10 位，只需增加两位即可达到 4KB）。

    一个 20 位的 VPN 意味着，操作系统必须为每个进程管理 $ 2^{20} $ 个地址转换（大约一百万）。

    假设每个页表格条目（PTE）需要 4 个字节，来保存物理地址转换和任何其他有用的东西，每个页表就需要巨大的 4MB 内存！这非常大。

    现在想象一下有 100 个进程在运行：这意味着操作系统会需要 400MB 内存，只是为了所有这些地址转换！

## 18.3 页表中究竟有什么

页表可以是很多数据结构，最简单的形式成为线性页表，就是一个数组。

这是 x86 的示例页表项 (PTE)：

```
+-----------+-----------+---+-----+---+---+-----+-----+-----+-----+---+
| 31.....12 | 11......9 | 8 |  7  | 6 | 5 |  4  |  3  |  2  |  1  | 0 |
+-----------+-----------+---+-----+---+---+-----+-----+-----+-----+---+
|    PFN    | Available | G | PAT | D | A | PCD | PWT | U/S | R/W | P |
+-----------+-----------+---+-----+---+---+-----+-----+-----+-----+---+
```

- 31.....12 - PFN (Page Frame Number)：页面帧号，表示物理内存中页面的实际地址。
- 11......9 - Available：这些位未被硬件使用，可以由操作系统用于其他目的。
- 8 - G (Global)：全局页标志，如果设置，表明该页表项对所有进程都是可见的，可以避免在任务切换时清除TLB。
- 7 - PAT (Page Attribute Table)：页属性表，与PWT和PCD位结合使用，提供更详细的内存缓存控制。
- 6 - D (Dirty)：脏位，如果设置，表示该页已被写入，即页面内容已被修改。
- 5 - A (Accessed)：访问位，如果设置，表示该页已被访问或读取。
- 4 - PCD (Page Cache Disable)：禁用页缓存，如果设置，表示不缓存该页面的内容。
- 3 - PWT (Page Write Through)：写通位，控制页面的写缓存策略。
- 2 - U/S (User / Supervisor)：用户/超级用户位，决定页面是否可以被用户模式的进程访问。
- 1 - R/W (Read / Write)：读/写位，如果设置，页面可以被读写；否则，页面仅为只读。
- 0 - P (Present)：存在位，如果设置，表示页面在物理内存中；否则，表示页面不在物理内存中，可能触发页面错误。

## 18.4 分页：也很慢

页表不但可能变很大，还可能会让速度变慢。

`#!asm movl 21, %eax` 的例子中，系统必须从进程的页表中提取适当的页表项，执行转换，将虚拟地址 `21` 转换为正确的物理地址 `117`。

为此，硬件必须知道进程页表的位置。现在假设一个页表基址寄存器 (page-table base register) 包含页表的起始位置的物理地址，为了找到想要的 PTE，硬件将执行以下操作：

```c
// Extract the VPN from the virtual address
VPN = (VirtualAddress & VPN_MASK) >> SHIFT

// Form the address of the page-table entry (PTE)
PTEAddr = PTBR + (VPN * sizeof(PTE))

// Fetch the PTE
PTE = AccessMemory(PTEAddr)

// Check if process can access the page
if (PTE.Valid == False)
    RaiseException(SEGMENTATION_FAULT)
else if (CanAccess(PTE.ProtectBits) == False)
    RaiseException(PROTECTION_FAULT)
else
    // Access OK: form physical address and fetch it
    offset = VirtualAddress & OFFSET_MASK
    PhysAddr = (PTE.PFN << PFN_SHIFT) | offset
    Register = AccessMemory(PhysAddr)
```

对于每个内存引用，分页都需要我们执行两个内存引用：

- 一个到页表查找指令所在的物理帧
- 另一个到指令本身将其获取到 CPU 进行处理

## 作业

!!! question
    1．在做地址转换之前，让我们用模拟器来研究线性页表在给定不同参数的情况下如何改变大小。在不同参数变化时，计算线性页表的大小。一些建议输入如下，通过使用-v 标志，你可以看到填充了多少个页表项。

    首先，要理解线性页表大小如何随着地址空间的增长而变化：

    ```
    paging-linear-translate.py -P 1k -a 1m -p 512m -v -n 0
    paging-linear-translate.py -P 1k -a 2m -p 512m -v -n 0
    paging-linear-translate.py -P 1k -a 4m -p 512m -v -n 0
    ```

    然后，理解线性页面大小如何随页大小的增长而变化：

    ```
    paging-linear-translate.py -P 1k -a 1m -p 512m -v -n 0
    paging-linear-translate.py -P 2k -a 1m -p 512m -v -n 0
    paging-linear-translate.py -P 4k -a 1m -p 512m -v -n 0
    ```

    在运行这些命令之前，请试着想想预期的趋势。页表大小如何随地址空间的增长而改变？随着页大小的增长呢？为什么一般来说，我们不应该使用很大的页呢？

!!! note "Answer"
    `page-table size = address space / page size`

    使用很大的页的话，会产生较大的内部碎片，同时页无法细致地控制内存分配。

---

!!! question
    2．现在让我们做一些地址转换。从一些小例子开始，使用-u 标志更改分配给地址空间的页数。例如：

    ```
    paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 0
    paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 25
    paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 50
    paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 75
    paging-linear-translate.py -P 1k -a 16k -p 32k -v -u 100
    ```

    如果增加每个地址空间中的页的百分比，会发生什么？

!!! note "Answer"
    更多被利用的页，空闲空间越来越少。

---

!!! question
    3．现在让我们尝试一些不同的随机种子，以及一些不同的（有时相当疯狂的）地址空间参数：

    ```
    paging-linear-translate.py -P 8 -a 32 -p 1024 -v -s 1
    paging-linear-translate.py -P 8k -a 32k -p 1m -v -s 2
    paging-linear-translate.py -P 1m -a 256m -p 512m -v -s 3
    ```

    哪些参数组合是不现实的？为什么？

!!! note "Answer"
    第三个页表太大。

---

!!! question
    4．利用该程序尝试其他一些问题。你能找到让程序无法工作的限制吗？例如，如果地址空间大小大于物理内存，会发生什么情况？

!!! note "Answer"
    该程序在以下情况下不起作用：

    - 物理内存大小 > 地址空间大小；
    - 页大小 > 地址空间大小；
    - 地址空间不是页大小的倍数；
    - 大小为零或为负。
