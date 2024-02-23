---
date: 2024-02-18
categories:
  - Programming Language
---

# Exploring the Hare Programming Language: Part 1

这篇依旧是跟屁虫系列。

Tsoding Daily 的新视频：[Hare Programming Language](https://www.youtube.com/watch?v=2E3E_Rh3mvw)

我决定先自己探索一遍再看。

<!-- more -->

## 关于

!!! quote "https://harelang.org/"
    Hare is a systems programming language designed to be simple, stable, and robust. Hare uses a static type system, manual memory management, and a minimal runtime. It is well-suited to writing operating systems, system tools, compilers, networking software, and other low-level, high performance tasks.

作者是 [Drew DeVault](https://drewdevault.com/)，Sway 的开发者。

描述中强调它 **简单**、**稳定** 和 **健壮**，适合编写操作系统、系统工具、编译器、网络软件和其他低级高性能任务。

拥有以下特性：

- 静态类型
- 手动内存管理
- 最小运行时

给我的初印象类似“现代 C 语言”。

## 安装

AUR 容易把人惯坏，`paru -S hare` 或 `paru -S hare-git` 就装好了。

这次我想手动编译，并且不把它们安装到系统环境里去。

安装比较有意思，需要三个阶段。

目录结构安排：

```
Hare/
├── hare    # The Hare programming language
├── harec   # Hare bootstrap compiler
├── qbe     # compiler backend
├── scdoc   # man page generator
└── usr     # storage for installed tools, similar to system's /usr/.
```

### Step 0: Pre-requisites

- 支持 C11 的编译器
- [QBE](https://c9x.me/compile/)
- [scdoc](https://sr.ht/~sircmpwn/scdoc)

QBE 是一个编译器后端，旨在用 10% 的代码提供 工业优化编译器 70% 的性能。

不同于其他“现代 C 语言”，Hare 可能真的想 Simple 到底。（Zig 使用了 LLVM，但它们正在迁移，想要摆脱 LLVM）

如果我以后又想造点什么玩具，也会优先考虑 QBE 的。

Hare 特意说明需要使用 QBE `master` 分支上的最新版本，而不是最新的 release。

克隆仓库，并安装到 `../usr/local`

```
git clone git://c9x.me/qbe.git --depth=1
make PREFIX=../usr/local
make install PREFIX=../usr/local
```

scdoc 是个简单轻量的 man page 生成器，也是 Drew DeVault 写的。

克隆仓库，并安装到 `../usr/local`

```
git clone https://git.sr.ht/~sircmpwn/scdoc --depth=1
make DESTDIR=..
make install DESTDIR=..
```

因为 Makefile 中写的是 `$(DESTDIR)/$(BINDIR)` 而不是 `$(DESTDIR)$(BINDIR)`，所以这里改 `PREFIX` 没用，得设置 `DESTDIR=..`。

### Step 1: Building the bootstrap compiler

克隆仓库，并安装到 `../usr/local`

```
git clone https://git.sr.ht/~sircmpwn/harec --depth=1
cp configs/linux.mk config.mk
sed -i 's|PREFIX = /usr/local|PREFIX = ../usr/local|' config.mk
make && make install
```

### Step 2: Building the build driver & standard library

克隆仓库，并安装到 `../usr/local`

```
git clone https://git.sr.ht/~sircmpwn/hare --depth=1
cp configs/linux.mk config.mk
sed -i 's|PREFIX = /usr/local|PREFIX = ../usr/local|' config.mk
make && make install
```

临时设置环境变量 `PATH` 和 `HAREPATH`，后者是标准库和第三方库的位置，编译的时候需要用到。

```fish
set -gx PATH $PWD/usr/local/bin/ $PATH
set -gx HAREPATH $PWD/usr/local/src/hare/stdlib:$PWD/usr/local/src/hare/third-party
```

## 从 Hello world! 开始

官方给了个教程：[https://harelang.org/tutorials/introduction](https://harelang.org/tutorials/introduction)

官方示例：

```hare title="hello.ha"
use fmt;

export fn main() void = {
    fmt::println("Hello world!")!;
};
```

这个拓展名还挺有意思的，「哈！」，很多个文件就是「哈哈哈哈哈哈哈」。

我的 nvim 自动识别到了 `hare`，看上去官方推荐缩进用 TAB （一股 Go 味），每个 TAB 八空格（？？？）。

到底是谁在用八空格？？？

```title="hare run hello.ha"
97/97 tasks completed (100%)
Hello world!
```

再次运行的时候就没有 `tasks` 进度了，应该是有改动才会再次编译。

## 编译缓存

看起来编译文件是有缓存这么一说的，但当前目录下什么也没生成。

通过搜索 `cache` 发现名叫 `hare-cache` 的手册

```title="fd cache"
hare/cmd/hare/cache.ha
hare/docs/hare-cache.1.scd
hare/hare/module/cache.ha
usr/local/share/man/man1/hare-cache.1           <----
usr/local/src/hare/stdlib/hare/module/cache.ha
```

```title="man hare-cache"
hare-cache(1)                                           General Commands Manual                                           hare-cache(1)

NAME
       hare cache - inspect and manage the build cache

SYNOPSIS
       hare cache [-hc]

DESCRIPTION
       hare  cache  provides  tools  to  manage  the  build cache. If no options are supplied, the path and disk usage of the cache are
       printed.

OPTIONS
       -h
           Print the help text.

       -c
           Clear the cache.

ENVIRONMENT
       The following environment variables affect hare cache's execution:

       HARECACHE   The path to the build cache. Defaults to $XDG_CACHE_HOME/hare, or ~/.cache/hare if $XDG_CACHE_HOME isn't set.
```

我没有设置 `HARECACHE` 和 `XDG_CACHE_HOME`，所以它给我放在了 `~/.cache/hare`，直接输入 `hare cache` 也能看到。

这下面的目录结构就是源代码的路径结构，比如源代码在 `/home/13m0n4de/Code/Hare/hello.ha`，缓存目录下的文件就会是：

```title="/home/13m0n4de/.cache/hare/"
home/
└── 13m0n4de
    └── Code
        └── Hare
            └── hello.ha
                ├── 278f991c88b8d7c6dc83d6259a3abc2b47b99d22e00354f2da6c9a1d6d512919.s
                ├── 278f991c88b8d7c6dc83d6259a3abc2b47b99d22e00354f2da6c9a1d6d512919.s.lock
                ├── 278f991c88b8d7c6dc83d6259a3abc2b47b99d22e00354f2da6c9a1d6d512919.s.log
                ├── 278f991c88b8d7c6dc83d6259a3abc2b47b99d22e00354f2da6c9a1d6d512919.s.txt
                ├── 6caa6d8dd4d8d9fcb6e47a54bc0a25b6fb88276c8ce8f3e2e787c2252638e7dc.td
                ├── 7f10f81946d21e37e6bc4a05efed5f541c449e5e23a9f451b282f7c144b32e1e.bin
                ├── 7f10f81946d21e37e6bc4a05efed5f541c449e5e23a9f451b282f7c144b32e1e.bin.lock
                ├── 7f10f81946d21e37e6bc4a05efed5f541c449e5e23a9f451b282f7c144b32e1e.bin.log
                ├── 7f10f81946d21e37e6bc4a05efed5f541c449e5e23a9f451b282f7c144b32e1e.bin.txt
                ├── 932ff2196cd983391326e8f5fbbb81a6785e1f4cffaf943f1f5e351d385bac47.o
                ├── 932ff2196cd983391326e8f5fbbb81a6785e1f4cffaf943f1f5e351d385bac47.o.lock
                ├── 932ff2196cd983391326e8f5fbbb81a6785e1f4cffaf943f1f5e351d385bac47.o.log
                ├── 932ff2196cd983391326e8f5fbbb81a6785e1f4cffaf943f1f5e351d385bac47.o.txt
                ├── deps.txt
                ├── ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa
                ├── ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa.lock
                ├── ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa.log
                ├── ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa.td
                └── ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa.txt
```

一共有六种文件，`.s`、`.bin`、`.td`、`.o`、`.ssa`、`deps.txt`。

其中 `.s`、`.bin`、`.ssa` 每个都还有 `.lock`、`.log`、`.tmp`、`.txt` 几种文件。

`.lock`：防止文件被同时访问

`.log`：日志，只有失败的时候才有内容，可能它只是错误日志，日志内容与编译器输出报错信息一致（带有色彩控制字符）

```txt title="*.ssa.log"
/home/13m0n4de/Code/Hare/hello.ha:4:21: error: Cannot ignore error here

4 |		fmt::println("Hello world!");
  |	                    [31m^[0m
```

`.tmp`：输出缓存，比如 `qbe` 先把结果输出到 `.s.tmp`

`.txt`：详细命令，比如 `qbe -t 'xxx' -o xxx.s.tmp xxx.ssa`

### `.s` 汇编文件

??? note "文件内容"
    ```asm title="*.s" hl_lines="5 22"
    .file 1 "<unknown>"
    .section ".data.strdata.1"
    .balign 8
    strdata.1:
        .ascii "/home/13m0n4de/Code/Hare/hello.ha"
    /* end data */

    .section ".data.strliteral.0"
    .balign 8
    strliteral.0:
        .quad strdata.1+0
        .quad 32
        .quad 32
    /* end data */

    .section ".data.strdata.33"
    .balign 8
    strdata.33:
        .ascii "Hello world!"
    /* end data */

    .file 2 "/home/13m0n4de/Code/Hare/hello.ha"
    .section ".data.strliteral.32"
    .balign 8
    strliteral.32:
        .quad strdata.33+0
        .quad 12
        .quad 12
    /* end data */

    .section ".text.main","ax"
    .globl main
    main:
        pushq %rbp
        movq %rsp, %rbp
        subq $112, %rsp
        .loc 2 3 25
        .loc 2 4 38
        .loc 2 4 21
        .loc 2 4 21
        .loc 2 4 35
        movl $2206074632, -32(%rbp)
        .loc 2 4 35
        leaq strliteral.32(%rip), %rax
        addq $0, %rax
        movq (%rax), %rax
        movq %rax, -24(%rbp)
        leaq strliteral.32(%rip), %rax
        addq $8, %rax
        movq (%rax), %rax
        movq %rax, -16(%rbp)
        leaq strliteral.32(%rip), %rax
        addq $16, %rax
        movq (%rax), %rax
        movq %rax, -8(%rbp)
        leaq -32(%rbp), %rax
        movq %rax, -56(%rbp)
        movq $1, -48(%rbp)
        movq $1, -40(%rbp)
        subq $32, %rsp
        movq %rsp, %rcx
        movq -56(%rbp), %rax
        movq %rax, 0(%rcx)
        movq -48(%rbp), %rax
        movq %rax, 8(%rcx)
        movq -40(%rbp), %rax
        movq %rax, 16(%rcx)
        leaq -104(%rbp), %rdi
        callq fmt.println
        subq $-32, %rsp
        movl (%rax), %eax
        cmpl $2843771249, %eax
        jz .Lbb3
        .loc 2 4 38
        movl $7, %ecx
        movl $38, %edx
        movl $4, %esi
        leaq strliteral.0(%rip), %rdi
        callq rt.abort_fixed
        ud2
    .Lbb3:
        leave
        ret
    .type main, @function
    .size main, .-main
    /* end function main */

    .section .note.GNU-stack,"",@progbits
    ```

高亮行是源代码的路径，看来编译器会自动添加它。

```title="*.s.txt"
qbe -t 'amd64_sysv' -o /home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/hello.ha/278f991c88b8d7c6dc83d6259a3abc2b47b99d22e00354f2da6c9a1d6d512919.s.tmp /home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/hello.ha/ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa
```

使用 `qbe` 编译 `.ssa` 文件，输出到 `.s.tmp`

所以说，Hare 可能是使用外部进程的方式来调用 QBE。

这个 `.ssa` 文件很可能来自 `harec`。

### `.td` 类型定义文件

```title="*.td"
use fmt;
export @symbol("main") fn main() void;
6caa6d8dd4d8d9fcb6e47a54bc0a25b6fb88276c8ce8f3e2e787c2252638e7dc
```

根据文件内容猜测是类型定义 (Type Definition) 文件，导出了主函数。

### `.bin` 可执行文件

这个文件和 `hare build` 出来的文件一样，静态链接的可执行文件，默认带有调试符号（所以之前的源代码路径是调试符号在的原因？）。

```title="file *.bin"
7f10f81946d21e37e6bc4a05efed5f541c449e5e23a9f451b282f7c144b32e1e.bin: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, with debug_info, not stripped
```

`*.bin.txt` 中是一大长串使用 `ld` 链接目标文件的命令，把标准库中的一些内容链接进去了。

### `.o` 目标文件

由 `.s` 文件编译而来的目标文件。

命令：

```title="*.o.txt"
as -o /home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/hello.ha/932ff2196cd983391326e8f5fbbb81a6785e1f4cffaf943f1f5e351d385bac47.o.tmp /home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/hello.ha/278f991c88b8d7c6dc83d6259a3abc2b47b99d22e00354f2da6c9a1d6d512919.s
```

### `deps.txt` 依赖文件

```title="deps.txt"
fmt
```

在 Hello world! 示例中就只有 `fmt` 一个依赖。

经过测试，它按行分割，且会按照字母顺序排列。

比如这样的代码：

```hare
use fmt;
use net;
use crypto;
```

会生成：

```
crypto
fmt
net
```

（其实官方推荐 `use` 语句按字母顺序排列，但不强制）

就算没有用到，只是 `use` 了，依然会编译并链接进二进制文件。

### `.ssa` 中间语言文件

这是 QBE 使用的基于 [SSA](https://en.wikipedia.org/wiki/Static_single-assignment_form) 的中间语言。

??? note "文件内容"
    ```
    bgfile "<unknown>"
    section ".data.strdata.1"
    data $strdata.1 = { b "/home/13m0n4de/Code/Hare/hello.ha" }

    dbgfile "<unknown>"
    section ".data.strliteral.0"
    data $strliteral.0 = { l $strdata.1, l 29, l 29 }

    dbgfile "<unknown>"
    # [24]u8 [id: 3457361888; size: 24]
    type :type.13 = align 1 { b 24 }

    dbgfile "<unknown>"
    # !struct { strerror: *fn(*errors::opaque_data) const str, data: errors::opaque_data, } [id: 4125378837; size: 32]
    type :type.12 = align 8 { l 1, :type.13 1 }

    dbgfile "<unknown>"
    type :values.align8.11 = { { :type.12 1 } { l 1 } }

    dbgfile "<unknown>"
    type :tagged.align8.14 = { w 1, :values.align8.11 1 }

    dbgfile "<unknown>"
    # !(!errors::unsupported | !errors::overflow | !errors::again | !errors::nomem | !errors::invalid | !errors::opaque_ | !errors::refused | !errors::cancelled | !errors::noaccess | !io::underread | !errors::noentry | !errors::interrupted | !errors::timeout | !errors::exists | !errors::busy) [id: 1589175157; size: 40]
    type :type.10 = align 8 { { :tagged.align8.14 1 } { w 1 } }

    dbgfile "<unknown>"
    type :values.align8.9 = { { l 1 } { :type.10 1 } }

    dbgfile "<unknown>"
    type :tagged.align8.15 = { w 1, :values.align8.9 1 }

    dbgfile "<unknown>"
    # (size | !io::error) [id: 1998184497; size: 48]
    type :type.8 = align 8 { { :tagged.align8.15 1 } }

    dbgfile "<unknown>"
    # []fmt::formattable [id: 2967698318; size: 24]
    type :type.17 = align 8 { l 3 }

    dbgfile "<unknown>"
    type :values.align1.21 = { { b 1 } { b 1 } { b 1 } }

    dbgfile "<unknown>"
    type :tagged.align1.22 = { w 1, :values.align1.21 1 }

    dbgfile "<unknown>"
    type :values.align2.23 = { { h 1 } { h 1 } }

    dbgfile "<unknown>"
    type :tagged.align2.24 = { w 1, :values.align2.23 1 }

    dbgfile "<unknown>"
    type :values.align4.25 = { { w 1 } { w 1 } { w 1 } { w 1 } { w 1 } { s 1 } }

    dbgfile "<unknown>"
    type :tagged.align4.26 = { w 1, :values.align4.25 1 }

    dbgfile "<unknown>"
    # str [id: 2206074632; size: 24]
    type :type.28 = align 8 { l 3 }

    dbgfile "<unknown>"
    type :values.align8.27 = { { l 1 } { d 1 } { l 1 } { l 1 } { :type.28 1 } { l 1 } { l 1 } }

    dbgfile "<unknown>"
    type :tagged.align8.29 = { w 1, :values.align8.27 1 }

    dbgfile "<unknown>"
    # (bool | i16 | u8 | i64 | f64 | rune | u64 | nullable *opaque | i32 | str | uintptr | int | size | uint | i8 | u32 | void | f32 | u16) [id: 3683259087; size: 32]
    type :type.20 = align 8 { { :tagged.align1.22 1 } { :tagged.align2.24 1 } { :tagged.align4.26 1 } { :tagged.align8.29 1 } { w 1 } }

    dbgfile "<unknown>"
    # [1]fmt::formattable [id: 1080674779; size: 32]
    type :type.19 = align 8 { :type.20 1 }

    dbgfile "<unknown>"
    section ".data.strdata.33"
    data $strdata.33 = { b "Hello world!" }

    dbgfile "/home/13m0n4de/Code/Hare/hello.ha"
    section ".data.strliteral.32"
    data $strliteral.32 = { l $strdata.33, l 12, l 12 }

    dbgfile "/home/13m0n4de/Code/Hare/hello.ha"
    section ".text.main" "ax" export
    function $main() {
    @start.2
        %object.16 =l alloc8 24
        %object.18 =l alloc8 32
        %binding.43 =l alloc8 8
    @body.3
        dbgloc 3, 25
        dbgloc 4, 38
        dbgloc 4, 21
        dbgloc 4, 21
        # gen lowered cast
        dbgloc 4, 35
        %item.30 =l add %object.18, 0
        # gen lowered cast
        storew 2206074632, %item.30
        %.31 =l add %item.30, 8
        dbgloc 4, 35
        blit $strliteral.32, %.31, 24
        storel %object.18, %object.16
        %.34 =l add %object.16, 8
        storel 1, %.34
        %.34 =l add %.34, 8
        storel 1, %.34
        %returns.7 =:type.8 call $fmt.println(:type.17 %object.16)
        %tag.35 =l loaduw %returns.7
        %subval.39 =l copy %returns.7
        %.40 =w ceqw %tag.35, 2843771249
        jnz %.40, @subtype.42, @next.38
    @subtype.42
        jmp @matches.37
    @matches.37
        %.44 =l add %returns.7, 8
        %.45 =l loadl %.44
        storel %.45, %binding.43
        %.46 =l loadl %binding.43
        %.6 =l copy %.46
        jmp @.36
    @next.38
        dbgloc 4, 38
        call $rt.abort_fixed(l $strliteral.0, l 4, l 38, l 7)
        hlt
    @.47
    @.36
        jmp @.4
    @.48
    @.4
        ret
    }
    ```

从中间语言中看到了一些亲切的东西：

- `u8`、`f64` 和 Rust 很像的类型名称
- `errors::unsupported` 像是错误处理用的

```title="*.ssa.txt"
# HARE_TD_fmt=/home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/usr/local/src/hare/stdlib/fmt/60d472e1243334af6cf3c4165412b40e1f8ae51d534ef26a4f19624efa4c22a1.td
harec -M /home/13m0n4de/Code/Hare/hello.ha/ -o /home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/hello.ha/ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa.tmp -t /home/13m0n4de/.cache/hare/home/13m0n4de/Code/Hare/hello.ha/ee744b05753cb66d0c9c91a6572eb5f38e926c3b9c2b7666dd58dcbb39e60fc7.ssa.td.tmp /home/13m0n4de/Code/Hare/hello.ha
```

`harec` 从源代码中生成了中间语言 `*.ssa.tmp` 和类型定义 `*.ssa.tmp.td` 文件。

最终，在某个操作后，这个类型定义文件存到了 `*.td`。

## 编译流程

整理一下编译流程：

1. 使用 `harec` 生成中间语言文件 `.ssa`
1. 使用 `qbe` 通过中间语言生成汇编语言文件 `.s`
1. 使用 `as` 将汇编生成目标机器代码文件 `.o`
1. 使用 `ld` 链接所有的目标文件，生成二进制文件 `.bin`

关于文件名我不太清楚，好像依赖变动了会重新生成一套 `.ssa`、`.s`、`.o`、`.bin`、`.td`，只要依赖不变，变动代码也不会改变这套文件名。

在我修改 `println` 输出内容后，只有四个 `task`，应该就对应了上面的四个吧。

## 可执行文件特征

首先，静态链接，这和官网宣传地一致，默认不链接 LIBC。

```title="file hello"
hello: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, with debug_info, not stripped
```

pwn checksec 检测结果：

```title="pwn checksec hello"
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      No PIE (0x7fff000)
    Stack:    Executable
    RWX:      Has RWX segments
```

感觉不对，NX 像是识别问题，而且 RWX 的段理应没有才对。

### NX ?

`*.bin.txt` 中链接命令使用了 `-z noexecstack` 选项，栈应该是不可执行。

查看段信息，发现只剩下 `.note.gnu.property`，没有 `GNU-stack`。

```title="readelf -W -S *.bin"
[Nr] Name              Type            Address          Off    Size   ES Flg Lk Inf Al
[ 0]                   NULL            0000000000000000 000000 000000 00      0   0  0
[ 1] .text             PROGBITS        0000000008000000 001000 02ec17 00  AX  0   0  1
[ 2] .note.gnu.property NOTE            000000000802ec18 02fc18 000030 00   A  0   0  8
[ 3] .data             PROGBITS        0000000080000000 030000 006020 00  WA  0   0  8
[ 4] .init_array       INIT_ARRAY      0000000080006020 036020 000030 08  WA  0   0  8
[ 5] .fini_array       FINI_ARRAY      0000000080006050 036050 000020 08  WA  0   0  8
[ 6] .bss              NOBITS          0000000080008000 036070 00c2a0 00  WA  0   0 16384
[ 7] .debug_line       PROGBITS        0000000000000000 036070 01de14 00      0   0  1
[ 8] .debug_info       PROGBITS        0000000000000000 053e84 0065d2 00      0   0  1
[ 9] .debug_abbrev     PROGBITS        0000000000000000 05a456 00049c 00      0   0  1
[10] .debug_aranges    PROGBITS        0000000000000000 05a900 0044d0 00      0   0 16
[11] .debug_str        PROGBITS        0000000000000000 05edd0 003bf0 01  MS  0   0  1
[12] .debug_ranges     PROGBITS        0000000000000000 0629c0 004470 00      0   0 16
[13] .symtab           SYMTAB          0000000000000000 066e30 007488 18     14 1016  8
[14] .strtab           STRTAB          0000000000000000 06e2b8 004514 00      0   0  1
[15] .shstrtab         STRTAB          0000000000000000 0727cc 0000a5 00      0   0  1
```

奇怪的是明明在之前看到汇编中看到有 `GNU-stack`。

查看 `hello.ha` 的目标文件的段信息：

```title="readelf -W -S *.o" hl_lines="14"
[Nr] Name              Type            Address          Off    Size   ES Flg Lk Inf Al
[ 0]                   NULL            0000000000000000 000000 000000 00      0   0  0
[ 1] .text             PROGBITS        0000000000000000 000040 000000 00  AX  0   0  1
[ 2] .data             PROGBITS        0000000000000000 000040 000000 00  WA  0   0  1
[ 3] .bss              NOBITS          0000000000000000 000040 000000 00  WA  0   0  1
[ 4] .data.strdata.1   PROGBITS        0000000000000000 000040 00001d 00  WA  0   0  8
[ 5] .data.strliteral.0 PROGBITS        0000000000000000 000060 000018 00  WA  0   0  8
[ 6] .rela.data.strliteral.0 RELA            0000000000000000 0004b0 000018 18   I 22   5  8
[ 7] .data.strdata.33  PROGBITS        0000000000000000 000078 00000c 00  WA  0   0  8
[ 8] .data.strliteral.32 PROGBITS        0000000000000000 000088 000018 00  WA  0   0  8
[ 9] .rela.data.strliteral.32 RELA            0000000000000000 0004c8 000018 18   I 22   8  8
[10] .text.main        PROGBITS        0000000000000000 0000a0 0000b0 00  AX  0   0  1
[11] .rela.text.main   RELA            0000000000000000 0004e0 000090 18   I 22  10  8
[12] .note.GNU-stack   PROGBITS        0000000000000000 000150 000000 00      0   0  1
[13] .note.gnu.property NOTE            0000000000000000 000150 000030 00   A  0   0  8
[14] .debug_line       PROGBITS        0000000000000000 000180 000071 00      0   0  1
[15] .rela.debug_line  RELA            0000000000000000 000570 000018 18   I 22  14  8
[16] .debug_info       PROGBITS        0000000000000000 0001f8 000036 00   C  0   0  8
[17] .rela.debug_info  RELA            0000000000000000 000588 0000f0 18   I 22  16  8
[18] .debug_abbrev     PROGBITS        0000000000000000 00022e 000028 00      0   0  1
[19] .debug_aranges    PROGBITS        0000000000000000 000258 00002f 00   C  0   0  8
[20] .rela.debug_aranges RELA            0000000000000000 000678 000030 18   I 22  19  8
[21] .debug_str        PROGBITS        0000000000000000 000287 000032 01  MS  0   0  1
[22] .symtab           SYMTAB          0000000000000000 0002c0 000198 18     23  14  8
[23] .strtab           STRTAB          0000000000000000 000458 000051 00      0   0  1
[24] .shstrtab         STRTAB          0000000000000000 0006a8 000100 00      0   0  1
```

它是有的，并且 checksec 也正确识别：

```title="pwn checksec *.o"
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x0)
```

所以说，是在最后一步使用 `ld` 链接的时候去掉了这个段。

`*.bin.txt` 中显示，链接用了 `--gc-sections`、`-z noexecstack`、`-T hare.sc` 三个选项。

我检查了一下，所有链接的 `.o` 文件都有 `.note.GNU-stack`，而这三个选项都对这个段不直接影响。

我只能理解为：「链接器认为不需要标注了，去掉这个空段减少文件大小」。

---

那么，它实际有执行权限吗？

写一个执行栈上 ShellCode 的代码测试一下：

```hare title="shellcode.ha"
export fn main() void = {
	const shellcode: []u8 = [0x90, 0x90, 0x90, 0xC3];
	let func: *fn() void = &shellcode: *fn() void;
	func();
};
```

```title="hare run shellcode.ha"
Stack overflow (invalid permissions for mapped object) at address 0x7ffd8bbc3498
/home/13m0n4de/Code/Hare/rt/+linux/start.ha:13:13 rt::start_ha+0xe [0x8003901]

/home/13m0n4de/Code/Hare/rt/+linux/platformstart-libc.ha:8:17 rt::start_linux+0x3a [0x8003ae8]

fish: Job 1, 'hare run shellcode.ha' terminated by signal SIGABRT (Abort)
```

提示 `0x7ffd8bbc3498` 位置的权限错误，这是栈上的地址。

调试，断在 `call rax` 前：

```asm title="gdb shellcode"
gef➤  disassemble main
Dump of assembler code for function main:
   0x000000000802eae1 <+0>:	push   rbp
   0x000000000802eae2 <+1>:	mov    rbp,rsp
   0x000000000802eae5 <+4>:	sub    rsp,0x20
   0x000000000802eae9 <+8>:	mov    BYTE PTR [rbp-0x1c],0x90
   0x000000000802eaed <+12>:	mov    BYTE PTR [rbp-0x1b],0x90
   0x000000000802eaf1 <+16>:	mov    BYTE PTR [rbp-0x1a],0x90
   0x000000000802eaf5 <+20>:	mov    BYTE PTR [rbp-0x19],0xc3
   0x000000000802eaf9 <+24>:	lea    rax,[rbp-0x1c]
   0x000000000802eafd <+28>:	mov    QWORD PTR [rbp-0x18],rax
   0x000000000802eb01 <+32>:	mov    QWORD PTR [rbp-0x10],0x4
   0x000000000802eb09 <+40>:	mov    QWORD PTR [rbp-0x8],0x4
   0x000000000802eb11 <+48>:	lea    rax,[rbp-0x18]
   0x000000000802eb15 <+52>:	call   rax
   0x000000000802eb17 <+54>:	leave
   0x000000000802eb18 <+55>:	ret
End of assembler dump.
gef➤  b *0x000000000802eb15
Breakpoint 1 at 0x802eb15: file /home/13m0n4de/Code/Hare/shellcode.ha, line 4.
```

`vmmap` 显示栈上没有执行权限：

```asm
gef➤  vmmap
[ Legend:  Code | Heap | Stack ]
Start              End                Offset             Perm Path
0x00000007fff000 0x0000000802f000 0x00000000000000 r-x /home/13m0n4de/Code/Hare/shellcode
0x00000080000000 0x00000080007000 0x00000000030000 rw- /home/13m0n4de/Code/Hare/shellcode
0x00000080007000 0x00000080015000 0x00000000000000 rw- [heap]
0x007ffff7ff4000 0x007ffff7ff9000 0x00000000000000 rw-
0x007ffff7ff9000 0x007ffff7ffd000 0x00000000000000 r-- [vvar]
0x007ffff7ffd000 0x007ffff7fff000 0x00000000000000 r-x [vdso]
0x007ffffffde000 0x007ffffffff000 0x00000000000000 rw- [stack]
0xffffffffff600000 0xffffffffff601000 0x00000000000000 --x [vsyscall]
```

所以它确实是 **没有执行权限**。

也有个 ticket 问到 *Are we actually using an executable stack?*，开发者回复说不是。

[~sircmpwn/hare#748: Resolve .note.GNU-stack warning emitted by GNU ld](https://todo.sr.ht/~sircmpwn/hare/748)

---

顺带一提，[github.com/slimm609/checksec.sh](https://github.com/slimm609/checksec.sh) 只检测 `GNU_STACK` 而不检测 `GNU-stack`：

[https://github.com/slimm609/checksec.sh/blob/36a67b388193d26289773f4153cb3b9f5bf5c9ec/src/functions/filecheck.sh#L27-L39](https://github.com/slimm609/checksec.sh/blob/36a67b388193d26289773f4153cb3b9f5bf5c9ec/src/functions/filecheck.sh#L27-L39)

pwntools 可以检测 `GNU-stack`。

### 调试信息

我把源代码移到了 `Hare/mycode/shellcode.ha`

```title="strings hello | rg 13m0n4de"
/home/13m0n4de/Code/Hare/mycode
/home/13m0n4de/Code/Hare
/home/13m0n4de/Code/Hare/mycode
```

这是之前就提到的文件路径，`harec` 默认生成，它们在 `strip` 之后就没有了，说明是调试信息。

去除之后，原本的报错信息会变成 `(unknown)`：

```title="strip hello && ./hello"
Stack overflow (invalid permissions for mapped object) at address 0x7ffe297d0568
(unknown) [0x8003901]
(unknown) [0x8003ae8]
fish: Job 1, './hello' terminated by signal SIGABRT (Abort)
```

通过 `-R` 选项编译 Release 模式的文件还是会带有调试信息的：

```title="hare build -R -o shellcode shellcode.ha && file shellcode"
shellcode: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, with debug_info, not stripped
```

但是就没有那么详尽的报错了：

```title="./shellcode"
fish: Job 1, './shellcode' terminated by signal SIGSEGV (Address boundary error)
```

release + strip，这个文件只有不到 11 KB，挺好。

### 默认编译文件名

我在 `mycode/` 下编译 `hello.ha`，如果不指定 `-o` 选项，默认给我了一个 `mycode` 可执行文件。

所以源码所在目录是某种类似 Module 的东西？如果 build 会默认以它作为文件名？

---

看完视频后：

这也许就是为什么视频中他遇到了 `Error: Output path 'hare' already exists, but isn't an executable file`

## 参考

- Hare: [harelang.org](https://harelang.org/)
- Hare .note.GNU-stack ticket: [~sircmpwn/hare#748](https://todo.sr.ht/~sircmpwn/hare/748)
