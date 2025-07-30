# 第 17 章 空闲空间管理

上一章遇到了外部碎片的问题，这章介绍几个策略来尽可能减少碎片。

## 17.1 假设

1. 内存分配库的接口就像 `#!c malloc()` 和 `#!c free()` 提供的那样，分配时只传入大小，回收时只传入指针；
1. 不在意内部碎片（分配程序给出的内存块超出请求的大小）；
1. 内存被分配给用户，就不可以被重定位（不能进行紧凑空间的操作）；
1. 分配程序管理的是连续的一块字节区域。

空闲列表（free list）：在堆上管理空闲空间的数据结构，该结构包含了管理内存区域中所有空闲块的引用。

## 17.2 底层机制

分配程序采用的一些通用机制。

### 分割与合并

**分割（splitting）**

假设有下面的 30 字节的堆：

```
0      10     20     30
^      ^      ^      ^
+------+------+------+
| free | used | free |
```

这个堆对应的空闲列表会有两个元素，一个描述第一个 10 字节的空闲区域（字节 0 ~ 9），一个描述另一个空闲区域（字节 20 ~ 29）：

```mermaid
graph LR;
    HEAD --> A[addr: 0, len: 10]
    A --> B[addr: 20, len: 10]
    B --> NULL
```

此时任何大于 10 字节的分配请求都会失败（返回 NULL），但如果申请小于 10 字节的内存，分配程序会执行所谓的分割动作：找到一块可以满足请求的空闲空间，将其分割，第一块返回给用户，第二块留在空闲列表中。

假设申请 1 字节的请求，分配程序选择使用第二块空闲空间，对 `#!c malloc()` 的调用会返回 20（1 字节分配区域的地址），空闲列表会变成这样：

```mermaid
graph LR;
    HEAD --> A[addr: 0, len: 10]
    A --> B[addr: 21, len: 9]
    B --> NULL
```

---

**合并（coalescing）**

一开始的例子中，10 字节的空闲空间，10 字节的已分配空间，10 字节的空闲空间。

如果执行 `#!c free(10)`，归还堆中间的空间，可能得到如下结果：

```mermaid
graph LR;
    HEAD --> A[addr: 10, len: 10]
    A --> B[addr: 0, len: 10]
    B --> C[addr: 20, len: 10]
    C --> NULL
```

尽管整个堆完全空闲，但被分割成了三个 10 字节的区域，如果此时用户请求 20 字节的空间，简单遍历空闲空间会找不到这样的空闲块，因此返回失败。

为了避免这个问题，分配程序会在释放一块内存时合并可用空间。

在归还一块空闲内存时，如果新归还的空间与一个（或两个）原有空闲块相邻，就将它们合并为一个较大的空闲块。

最后得到这样的空闲列表：

```mermaid
graph LR;
    HEAD --> A[addr: 0, len: 30]
    A --> NULL
```

### 追踪已分配空间的大小

`#!c free(void *ptr)` 接口没有块大小的参数，因此它假定对于给定的指针，内存分配库可以很快确定要释放空间的大小。

大多数分配程序都会在头块（header）中保存一点额外信息，通常就放置在返回的内存块之前。

```c
typedef struct header_t {
    int size;
    int magic;
} header_t;
```

库会通过简单的指针运算得到头块的位置：

```c
void free(void *ptr) {
    header_t *hptr = (void *)ptr - sizeof(header_t);
}
```

```
hptr --> +----------------+ 
         | size:  20      |
         |----------------| Header Chunk
         | magic: 1234567 |
ptr  --> +----------------+ 
         |                | Data Chunk (20 byte)
         +----------------+
```

获得头块的指针后，库可以很容易地确定幻数是否符合预期的值，作为正常性检查（`#!c assert(hptr->magic == 1234567)`），并简单计算要释放的空间大小（即头块的大小加区域长度）。

如果用户请求 N 字节的内存，就不再是寻找大小为 N 的空闲块，而是寻找 N 加上头块大小的空闲块。

### 嵌入空闲列表

难过的事实：没法在创建空闲列表时使用 `#!c malloc`，尽管这是在内存分配库中。

假设需要管理一个 4096 字节的内存块（即堆是 4 KB）。

为了将它作为一个空闲列表来管理，首先需要初始化。

以下是节点定义：

```c
typedef struct node_t {
    int size;
    struct node_t *next;
} node_t;
```

使用 `#!c mmap` 系统调用，映射一片内存。

```c
void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
```

```c
node_t *head = mmap(NULL, 4096, PORT_READ | PORT_WRITE,
                    MAP_ANON | MAP_PRIVATE, -1, 0);
head->size = 4096 - sizeof(node_t);
head->next = NULL;
```

执行这段代码之后，列表只有一个条目，记录大小为 4088。

```
head --> +----------------+ [virtual address: 16 KB]
         | size:  4088    | Header: size field
         |----------------| 
         | next:  0       | Header: next field (NULL is 0)
         +----------------+ 
         |                |
         |                | the rest of the 4 KB chunk
         |                |
         +----------------+
```

假设有一个 100 字节的内存请求，库选中唯一的 4088 字节的块，将其分割。

```
         +----------------+ [virtual address: 16 KB]
         | size:  100     |
         |----------------| 
         | magic: 1234567 |
ptr  --> +----------------+ 
         |                |
         |                | The 100 bytes now allocated
         |                |
head --> +----------------+
         | size:  3980    |
         |----------------| 
         | next:  0       |
         +----------------+
         |                |
         |                | The free 3980 byte chunk
         |                |
         +----------------+
```

库从原有的一个空闲块中分配了 108 字节，返回指向它的一个指针 `ptr`，并在其之前连续的 8 字节中记录头块信息，供未来的 `#!c free` 函数使用，同时将列表中的空闲节点缩小为 3980 字节。

重复两次上述操作。

此时用户调用 `#!c free(16500)`，归还了中间的一块已分配空间（内存块的起始地址 16384 加上前一块 108 和这一块的头块的 8 字节，得到了 16500），这个值用 `#!c sptr` 表示。

```
         +----------------+ [virtual address: 16 KB]
         | size:  100     |
         |----------------| 
         | magic: 1234567 |
         +----------------+ 
         |                |
         |                | 100 bytes still allocated
         |                |
         +----------------+
         | size:  100     |
         |----------------| 
         | magic: 1234567 |
sptr --> +----------------+ 
         |                |
         |                | 100 bytes still allocated (but about to be freed)
         |                |
         +----------------+
         | size:  100     |
         |----------------| 
         | magic: 1234567 |
         +----------------+
         |                |
         |                | 100 bytes still allocated
         |                |
head --> +----------------+
         | size:  3764    |
         |----------------| 
         | next:  0       |
         +----------------+
         |                |
         |                | The free 3764-byte chunk 
         |                |
         +----------------+
```

库通过头块信息弄清楚了要释放的大小，并将空闲块加回空闲列表，假设将它插入空闲列表的头位置。

```
         +----------------+ [virtual address: 16 KB]
         | size:  100     |
         |----------------| 
         | magic: 1234567 |
         +----------------+ 
         |                |
         |                | 100 bytes still allocated
         |                |
head --> +----------------+
         | size:  100     |
         |----------------| 
         | magic: 16708   | --------------------------------+
sptr --> +----------------+                                 |
         |                |                                 |
         |                | (now a free chunk of memory)    |
         |                |                                 |
         +----------------+                                 |
         | size:  100     |                                 |
         |----------------|                                 |
         | magic: 1234567 |                                 |
         +----------------+                                 |
         |                |                                 |
         |                | 100 bytes still allocated       |
         |                |                                 |
         +----------------+ <-------------------------------+
         | size:  3764    |
         |----------------| 
         | next:  0       |
         +----------------+
         |                |
         |                | The free 3764-byte chunk 
         |                |
         +----------------+
```

是的，它不会“销毁”任何内容，只是在空闲列表中将它认为是“空闲的”，原有的数据还在。

假设剩余的两块已分配空间也被释放，没有合并，空闲列表将非常破碎：

```
         +----------------+ <-------------------------------+
         | size:  100     |                                 |
         |----------------|                                 |
         | magic: 1234567 | ------------------------------+ |
         +----------------+                               | |
         |                |                               | |
         |                | (now a free chunk of memory)  | |
         |                |                               | |
         +----------------+ <-----------------------------+ |
         | size:  100     |                                 |
         |----------------|                                 |
         | magic: 16708   | --------------------------------|-+
         +----------------+                                 | |
         |                |                                 | |
         |                | (now a free chunk of memory)    | |
         |                |                                 | |
head --> +----------------+                                 | |
         | size:  100     |                                 | |
         |----------------|                                 | |
         | magic: 16384   | --------------------------------+ |
         +----------------+                                   |
         |                |                                   |
         |                | (now a free chunk of memory)      |
         |                |                                   |
         +----------------+ <---------------------------------+
         | size:  3764    |
         |----------------| 
         | next:  0       |
         +----------------+
         |                |
         |                | The free 3764-byte chunk 
         |                |
         +----------------+
```

解决方案很简单：遍历列表，合并相邻块，完成之后，堆又成了一个整体。

### 让堆增长

如果堆中的内存耗尽，可以使用 sbrk 系统调用增加堆的大小，这样用户的请求就不会是直接返回 NULL 了。

## 17.3 基本策略

### 最优匹配（best-fit）

遍历整个空闲列表，找到大小符合的空闲块，然后返回其中最小的一块，所以它也可以被称为最小匹配。

遍历查找正确空闲块时，要付出较高性能代价。

### 最差匹配（worst-fit）

尝试找到最大块，分割并将剩余的块加入空闲列表。

最差匹配尝试在空闲列表中保留较大的块，以此来尝试不留下难以利用的小块。

但它同样需要遍历整个空闲列表，并且大多数研究表明它的表现非常差，导致过量的碎片，同时还有很高的开销。

### 首次匹配（first-fit）

找到第一个足够大的块就分割给用户。

首次匹配有速度优势，不需要遍历空闲块，但有时会让空闲列表开头的部分有很多小块。

因此，分配程序如何管理空闲列表的顺序就变得很重要。一种方式是基于地址排序。通过保持空闲块按内存地址有序，合并操作会很容易，从而减少了内存碎片。

### 下次匹配（next-fit）

下次匹配多维护一个指针，指向上次查找结束的位置。

其想法是将对空闲空间的查找操作扩散到整个列表中去，避免对列表开头频繁的分割。

这种策略的性能与首次匹配很接它，同样避免了遍历查找。

### 例子

```mermaid
graph LR;
    HEAD --> A[10]
    A --> B[30]
    B --> C[20]
    C --> NULL
```

假设此时有个 15 字节的内存请求，最优匹配会遍历整个空闲列表，发现 20 字节是最优匹配，结果空闲列表变为：

```mermaid
graph LR;
    HEAD --> A[10]
    A --> B[30]
    B --> C[50]
    C --> NULL
```

本例中发生的情况，在最优匹配中常常发生，现在留下了一个小空闲块。

最差匹配类似，但会选择最大的空闲块进行分割，在本例中是 30。结果空闲列表变为：

```mermaid
graph LR;
    HEAD --> A[10]
    A --> B[15]
    B --> C[20]
    C --> NULL
```

在这个例子中，首次匹配会和最差匹配一样，也发现满足请求的第一个空闲块。不同的是查找开销，最优匹配和最差匹配都需要遍历整个列表，而首次匹配只找到第一个满足需求的块即可，因此减少了查找开销。

## 17.4 其他方式

### 分离空闲列表（segregated list）

如果某个应用程序经常申请一种（或几种）大小的内存空间，那就用一个独立的列表，只管理这样大小的对象。其他大小的请求都一给更通用的内存分配程序。

通过拿出一部分内存专门满足某种大小的请求，碎片就不再是问题了。而且，由于没有复杂的列表查找过程，这种特定大小的内存分配和释放都很快。

但是这种方式引入了新的复杂性：应该拿出多少内存来专门为某种大小的请求服务，同时剩余的内存还能用来满足一般请求？

!!! quote "Solaris 系统内核的厚块分配程序（slab allocator）的解决方案"

    具体来说，在内核启动时，它为可能频繁请求的内核对象创建一些对象缓存（object cache），如锁和文件系统 inode 等。这些的对象缓存每个分离了特定大小的空闲列表，因此能够很快地响应内存请求和释放。

    如果某个缓存中的空闲空间快耗尽时，它就向通用内存分配程序申请一些内存厚块（slab）（总量是页大小和对象大小的公倍数）。

    相反，如果给定厚块中对象的引用计数变为 0，通用的内存分配程序可以从专门的分配程序中回收这些空间，这通常发生在虚拟内存系统需要更多的空间的时候。

    厚块分配程序比大多数分离空闲列表做得更多，它将列表中的空闲对象保持在预初始化的状态。

    Bonwick 指出，数据结构的初始化和销毁的开销很大。通过将空闲对象保持在初始化状态，厚块分配程序避免了频繁的初始化和销毁，从而显著降低了开销。

### 伙伴系统（buddy allocator）

**二分伙伴分配程序**，空闲空间被看成为 $ 2^{N} $ 的大空间，当有内存分配请求时，空闲空间被递归地一分为二，直到刚好可以满足请求大小。

```
+-------------------------------------------------------+
|                         64 KB                         |
+-------------------------------------------------------+
              |                           |
+---------------------------+---------------------------+
|           32 KB           |           32 KB           |
+---------------------------+---------------------------+
       |             |
+-------------+-------------+
|    16 KB    |    16 KB    |
+-------------+-------------+
   |      |
+------+------+
| 8 KB | 8 KB |
+------+------+
```

这种分配策略只允许 分配 2 的整数次幂大小的空闲块，因此会有内部碎片（internal fragment）的麻烦。

伙伴系统释放时会检查“伙伴” 8 KB 是否空闲，如果是就合二为一，变成 16 KB 的块，然后检查这个 16 KB 块的伙伴是否空闲，如此递归上溯，直到合并整个内存区域，或者某个块的伙伴还没有被释放。

伙伴系统运转良好的原因，在于很容易确定某个块的伙伴，每对互为伙伴的块只有一位不同。也正是这一位决定了它们在整个伙伴树中的层次。

| Block   | Binary Representation of Address   | Size   | Note                                   |
| ------- | ---------------------------------- | ------ | -------------------------------------- |
| A       | 0000 0000 0000 0000                | 4KB    |                                        |
| B       | 0001 0000 0000 0000                | 4KB    | A 和 B 互为伙伴，第 13 位不同          |
| ------- | ---------------------------------- | ------ | -------------------------------------- |
| C       | 0000 0000 0000 0000                | 2KB    | 从 A 分割而来                          |
| D       | 0000 1000 0000 0000                | 2KB    | C 和 D 互为伙伴，第 12 位不同          |
| ------- | ---------------------------------- | ------ | -------------------------------------- |
| E       | 0001 0000 0000 0000                | 2KB    | 从 B 分割而来                          |
| F       | 0001 1000 0000 0000                | 2KB    | E 和 F 互为伙伴，第 12 位不同          |

### 其他想法

上面提到的众多方法都有一个重要的问题，缺乏可扩展性（scaling）。

具体来说，就是查找列表可能很慢。因此，更先进的分配程序采用更复杂的数据结构来优化这个开销，牺牲简单性来换取性能。例子包括平衡二叉树、伸展树和偏序树。

## 作业

!!! question

    1．首先运行 -n 10 -H 0 -p BEST -s 0 来产生一些随机分配和释放。你能预测 malloc()/free()会返回什么吗？你可以在每次请求后猜测空闲列表的状态吗？随着时间的推移，你对空闲列表有什么发现？

!!! note "Answer"

    内存被分为更细小的碎块留在靠前的位置。

    ```title="./malloc.py -n 10 -H 0 -p BEST -s 0 -c"
    ptr[0] = Alloc(3) returned 1000 (searched 1 elements)
    Free List [ Size 1 ]: [ addr:1003 sz:97 ]

    Free(ptr[0])
    returned 0
    Free List [ Size 2 ]: [ addr:1000 sz:3 ][ addr:1003 sz:97 ]

    ptr[1] = Alloc(5) returned 1003 (searched 2 elements)
    Free List [ Size 2 ]: [ addr:1000 sz:3 ][ addr:1008 sz:92 ]

    Free(ptr[1])
    returned 0
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:92 ]

    ptr[2] = Alloc(8) returned 1008 (searched 3 elements)
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1016 sz:84 ]

    Free(ptr[2])
    returned 0
    Free List [ Size 4 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[3] = Alloc(8) returned 1008 (searched 4 elements)
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1016 sz:84 ]

    Free(ptr[3])
    returned 0
    Free List [ Size 4 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[4] = Alloc(2) returned 1000 (searched 4 elements)
    Free List [ Size 4 ]: [ addr:1002 sz:1 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[5] = Alloc(7) returned 1008 (searched 4 elements)
    Free List [ Size 4 ]: [ addr:1002 sz:1 ][ addr:1003 sz:5 ][ addr:1015 sz:1 ][ addr:1016 sz:84 ]
    ```

---

!!! question

    2．使用最差匹配策略搜索空闲列表（-p WORST）时，结果有何不同？什么改变了？

!!! note "Answer"

    内存被分割为更多的碎片，搜索了更多元素。

    ```title="./malloc.py -n 10 -H 0 -p WORST -s 0 -c"
    ptr[0] = Alloc(3) returned 1000 (searched 1 elements)
    Free List [ Size 1 ]: [ addr:1003 sz:97 ]

    Free(ptr[0])
    returned 0
    Free List [ Size 2 ]: [ addr:1000 sz:3 ][ addr:1003 sz:97 ]

    ptr[1] = Alloc(5) returned 1003 (searched 2 elements)
    Free List [ Size 2 ]: [ addr:1000 sz:3 ][ addr:1008 sz:92 ]

    Free(ptr[1])
    returned 0
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:92 ]

    ptr[2] = Alloc(8) returned 1008 (searched 3 elements)
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1016 sz:84 ]

    Free(ptr[2])
    returned 0
    Free List [ Size 4 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[3] = Alloc(8) returned 1016 (searched 4 elements)
    Free List [ Size 4 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1024 sz:76 ]

    Free(ptr[3])
    returned 0
    Free List [ Size 5 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:8 ][ addr:1024 sz:76 ]

    ptr[4] = Alloc(2) returned 1024 (searched 5 elements)
    Free List [ Size 5 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:8 ][ addr:1026 sz:74 ]

    ptr[5] = Alloc(7) returned 1026 (searched 5 elements)
    Free List [ Size 5 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:8 ][ addr:1033 sz:67 ]
    ```

---

!!! question

    3．如果使用首次匹配（-p FIRST）会如何？使用首次匹配时，什么变快了？

!!! note "Answer"

    搜索的元素更少。

    ```title="./malloc.py -n 10 -H 0 -p FIRST -s 0 -c"
    ptr[0] = Alloc(3) returned 1000 (searched 1 elements)
    Free List [ Size 1 ]: [ addr:1003 sz:97 ]

    Free(ptr[0])
    returned 0
    Free List [ Size 2 ]: [ addr:1000 sz:3 ][ addr:1003 sz:97 ]

    ptr[1] = Alloc(5) returned 1003 (searched 2 elements)
    Free List [ Size 2 ]: [ addr:1000 sz:3 ][ addr:1008 sz:92 ]

    Free(ptr[1])
    returned 0
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:92 ]

    ptr[2] = Alloc(8) returned 1008 (searched 3 elements)
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1016 sz:84 ]

    Free(ptr[2])
    returned 0
    Free List [ Size 4 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[3] = Alloc(8) returned 1008 (searched 3 elements)
    Free List [ Size 3 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1016 sz:84 ]

    Free(ptr[3])
    returned 0
    Free List [ Size 4 ]: [ addr:1000 sz:3 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[4] = Alloc(2) returned 1000 (searched 1 elements)
    Free List [ Size 4 ]: [ addr:1002 sz:1 ][ addr:1003 sz:5 ][ addr:1008 sz:8 ][ addr:1016 sz:84 ]

    ptr[5] = Alloc(7) returned 1008 (searched 3 elements)
    Free List [ Size 4 ]: [ addr:1002 sz:1 ][ addr:1003 sz:5 ][ addr:1015 sz:1 ][ addr:1016 sz:84 ]
    ```

---

!!! question

    4．对于上述问题，列表在保持有序时，可能会影响某些策略找到空闲位置所需的时间。使用不同的空闲列表排序（-l ADDRSORT，-l SIZESORT +，-l SIZESORT-）查看策略和列表排序如何相互影响。

!!! note "Answer"

    对于最优匹配，按照地址和按照大小排序没有区别，搜索次数和碎块数量都不变。

    对于最差匹配也一样。

    首次匹配时，将最大块放在最前面可以保证没有多次搜索的成本，反之，会拥有最多的搜索次数。

---

!!! question

    5．合并空闲列表可能非常重要。增加随机分配的数量（比如说-n 1000）。随着时间的推移，大型分配请求会发生什么？在有和没有合并的情况下运行（即不用和采用-C 标志）。你看到了什么结果差异？每种情况下的空闲列表有多大？在这种情况下，列表的排序是否重要？

!!! note "Answer"

    只考虑块大小时，按地址排序更好，尤其在启用合并后。

    With out `-C`:

    - `ADDRSORT`:
        - `BEST`: 31
        - `WORST`: 100
        - `FIRST`: 51
    - `SIZESORT+`:
        - `BEST`: 31
        - `WORST`: 100
        - `FIRST`: 31
    - `SIZESORT-`:
        - `BEST`: 31
        - `WORST`: 100
        - `FIRST`: 100

    With `-C`:

    - `ADDRSORT`:
        - `BEST`: 1
        - `WORST`: 1
        - `FIRST`: 1
    - `SIZESORT+`:
        - `BEST`: 28
        - `WORST`: 100
        - `FIRST`: 28
    - `SIZESORT-`:
        - `BEST`: 33
        - `WORST`: 100
        - `FIRST`: 98

---

!!! question

    6．将已分配百分比-P 改为高于 50，会发生什么？它接近 100 时分配会怎样？接近 0 会怎样？

!!! note "Answer"

    ```
    ./malloc.py -c -n 1000 -P 100
    ./malloc.py -c -n 1000 -P 1
    ```

    非常靠近 0 的时候，没有更多空间可以分配，所有指针都返回 `#!c NULL`。

---

!!! question

    7．要生成高度碎片化的空闲空间，你可以提出怎样的具体请求？使用-A 标志创建碎片化的空闲列表，查看不同的策略和选项如何改变空闲列表的组织。

!!! note

    来自 [github.com/xxyzz/ostep-hw/tree/master/17](https://github.com/xxyzz/ostep-hw/tree/master/17)

    ```
    $ ./malloc.py -c -A +20,+20,+20,+20,+20,-0,-1,-2,-3,-4
    $ ./malloc.py -c -A +20,+20,+20,+20,+20,-0,-1,-2,-3,-4 -C
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -l SIZESORT-
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -l SIZESORT- -C
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p FIRST -l SIZESORT+
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p FIRST -l SIZESORT+ -C
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p FIRST -l SIZESORT-
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p FIRST -l SIZESORT- -C
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p WORST -l SIZESORT+
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p WORST -l SIZESORT+ -C
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p WORST -l SIZESORT-
    $ ./malloc.py -c -A +10,-0,+20,-1,+30,-2,+40,-3 -p WORST -l SIZESORT- -C
    ```
