---
date: 2026-01-23
categories:
  - Programming Language
tags:
  - Programming Language
  - Compiler
  - QBE
  - SSA
---

# Hello, Saya Lang

```rust
extern fn puts(s: *u8) -> i64;

pub fn main() -> i64 {
    puts(c"Hello, Saya!");
    0
}
```

我真正意义上的第一个编译型玩具语言，编译到 [QBE IL](https://c9x.me/compile/)。

语法和关键字与 Rust 差不太多，基于表达式。编译器内部结构参考了 [Hare](https://harelang.org/) 语言的编译器 [harec](https://git.sr.ht/~sircmpwn/harec/)，一些数据结构设计参考了 [rustc](https://github.com/rust-lang/rust/tree/main/compiler)。

Saya 是圣诞节项目，想当做某种礼物送给自己，后来拖延成了跨年项目，再最后，要变成新年项目了……

总之，向您送出诚挚的圣诞祝福。

仓库：[github.com/13m0n4de/saya](https://github.com/13m0n4de/saya)

<!-- more -->

## 语法定义

Saya 的 ABNF 在：[saya.abnf](https://github.com/13m0n4de/saya/blob/main/docs/saya.abnf)。

与 Rust 不同的地方是，`extern` 作为函数修饰符而不是块修饰符，模块也不用 `mod` 定义。

```rust
extern fn DrawText(text: *u8, posX: i64, posY: i64, fontSize: i64, color: Color);
```

顺带我发现，[Rust 还没有 BNF 定义](https://users.rust-lang.org/t/bnf-syntax-diagram-for-rust/126712)，也许是太复杂了？

## 解析器

解析器部分选择手写递归下降解析器，用了 [Pratt Parsing](https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html) 处理表达式优先级。

给每个运算符定义 binding power，数字越大优先级越高：

```rust
fn infix_binding_power(token: &TokenKind) -> Option<(u8, u8)> {
    let bp = match token {
        TokenKind::OrOr => (10, 11),                 // ||
        TokenKind::AndAnd => (20, 21),               // &&
        TokenKind::Or => (30, 31),                   // |
        TokenKind::And => (40, 41),                  // &
        TokenKind::EqEq | TokenKind::Ne => (50, 51), // == !=
        TokenKind::Lt | TokenKind::Le | TokenKind::Gt | TokenKind::Ge => (60, 61), // < <= > >=
        TokenKind::Plus | TokenKind::Minus => (70, 71), // + -
        TokenKind::Star | TokenKind::Slash | TokenKind::Percent => (80, 81), // * / %
        _ => return None,
    };
    Some(bp)
}
```

返回的元组 `(left, right)` 用于处理结合性，左结合用 `left < right`。

```rust
fn parse_expr_bp(&mut self, min_bp: u8) -> Result<Expr, ParseError> {
    // ...
    if let Some((left_bp, right_bp)) = Self::infix_binding_power(op_token) {
        if left_bp < min_bp {
            break; // 优先级不够，停止解析为 Binary 表达式
        }

        let op = match op_token {
            TokenKind::Plus => BinaryOp::Add,
            // ...
            _ => unreachable!(),
        };

        let span = lhs.span;
        self.advance()?;
        let rhs = self.parse_expr_bp(right_bp)?; // 用 right_bp 递归解析右侧

        lhs = Expr {
            kind: ExprKind::Binary(op, Box::new(lhs), Box::new(rhs)),
            span,
        };

        continue;
    }
}
```

## 类型检查器

类型检查器接收 AST，输出 HIR（High-level IR）。虽然叫 HIR，但并不像 Rust 的 HIR 那样接近机器表示，更像是经过语义分析的 AST。

HIR 不只是给 AST 节点附加类型信息，还完成了：

- 名称解析：将 `Path` 解析为具体的 `Place`
- 常量求值：将编译期表达式折叠为字面量
- 去语法糖：`Use` 和 `StructDef` 被消化进类型系统

AST 和 HIR 的结构大体相似（`Expr`、`Stmt`、`Block` 等），主要区别在于类型信息和一些语义处理。用 [Tree that Grow](https://www.microsoft.com/en-us/research/uploads/prod/2016/11/trees-that-grow.pdf) 模式可以让两者共享结构定义，只在类型参数上有所不同。Rust 可以用 Trait + 关联类型模拟，但实现起来泛型传染严重，不如分开定义清晰。

Tree that Grow in Rust 相关项目：

- [github.com/guygastineau/rust-trees-that-grow](https://github.com/guygastineau/rust-trees-that-grow)
- [github.com/enklht/trees_that_grow_rs](https://github.com/enklht/trees_that_grow_rs)

## 代码生成

### QBE

QBE 是一个轻量级的编译器后端，[一年前](./exploring_the_hare_part1.md)从 Hare 那认识的，它的中间语言长这样：

```
function w $add(w %a, w %b) {          # Define a function add
@start
    %c =w add %a, %b                   # Adds the 2 arguments
    ret %c                             # Return the result
}
export function w $main() {            # Main function
@start
    %r =w call $add(w 1, w 1)          # Call add(1, 1)
    call $printf(l $fmt, ..., w %r)    # Show the result
    ret 0
}
data $fmt = { b "One and one make %d!\n", b 0 }
```

### 类型映射

Saya 类型映射到 QBE 类型：

- `i64`, `pointer` -> long (`l`)
- `u8`, `bool` -> word (`w`) / byte(`b`)
- `struct` / `array` -> aggregate type

`u8` 和 `bool` 比较特殊：QBE 的函数参数、返回值和临时变量只能是 word 或 long，不支持 byte。所以这两个类型在大多数场景用 word，只有 `load` / `store` 指令才用 byte 来确保只读写一个字节。

### 聚合类型

标量类型（`i64`、`bool`、指针等）可以直接用 `load` / `store` 操作整个值，但聚合类型（`struct`、`array`、`slice`）不行——它们按地址传递，赋值时需要逐字段复制。

```rust
fn load_value(
    &mut self,
    qfunc: &mut qbe::Function<'static>,
    addr: qbe::Value,
    type_id: TypeId,
) -> GenValue {
    if self.types.get(type_id).is_aggregate() {
        // 聚合类型：直接返回地址，不生成 load
        match addr {
            qbe::Value::Temporary(name) => GenValue::Temp(name, type_id),
            qbe::Value::Global(name) => GenValue::Global(name, type_id),
            qbe::Value::Const(_) => unreachable!("cannot load from a constant address"),
        }
    } else {
        // 标量类型：生成 load 指令
        let load_type = self.qbe_load_type(type_id);
        self.assign_to_temp(qfunc, type_id, qbe::Instr::Load(load_type, addr))
    }
}

fn store_value(
    &mut self,
    qfunc: &mut qbe::Function<'static>,
    dest_addr: qbe::Value,
    src: GenValue,
    type_id: TypeId,
) {
    if self.types.get(type_id).is_aggregate() {
        // 聚合类型：根据具体类型展开复制
        self.copy_aggregate(qfunc, dest_addr, src.into(), type_id);
    } else {
        // 标量类型：生成 store 指令
        let store_type = self.qbe_store_type(type_id);
        qfunc.add_instr(qbe::Instr::Store(store_type, dest_addr, src.into()));
    }
}
```

### 控制流

if-else 表达式需要合并两个分支的值，用了 QBE 的 `phi` 指令：

```rust
let zero: i64 = if true { 0 } else { 1 };
```

生成：

```
    %zero =l alloc8 8
@if.0.cond
    jnz 1, @if.0.then, @if.0.else
@if.0.then
    jmp @if.0.end
@if.0.else
    jmp @if.0.end
@if.0.end
    %temp.0 =l phi @if.0.then 0, @if.0.else 1
    storel %temp.0, %zero
```

QBE IL 生成用了 [qbe-rs](https://github.com/garritfra/qbe-rs) crate，它的 phi 只支持两个节点，但我手写 IL 测试出 QBE 是支持多 phi 节点的。

如果未来要实现 `match` 或 `loop` + 多个 `break value` 的话，可能要给 qbe-rs 提个 PR。不过目前够用，`else if` 会解析成嵌套的 `if`，每层只需要两个 phi 节点。

### 短路求值

`&&` 和 `||` 需要短路求值——左侧结果确定时不求值右侧。不能用简单的位运算实现，得用控制流。

```rust
let t: bool = true;
let f: bool = false;
let result: bool = t && f;
```

生成：

```
    %t =l alloc4 1
    storeb 1, %t
    %f =l alloc4 1
    storeb 0, %f
    %result =l alloc4 1
    %temp.0 =w loadub %t
    jnz %temp.0, @land.0.rhs, @land.0.false
@land.0.rhs
    %temp.1 =w loadub %f
    %temp.2 =w copy %temp.1
    jmp @land.0.end
@land.0.false
    %temp.3 =w copy 0
    jmp @land.0.end
@land.0.end
    %temp.4 =w phi @land.0.rhs %temp.2, @land.0.false %temp.3
    storeb %temp.4, %result
```

## 模块

Saya 的模块系统照抄了 Hare，`use` 只导入类型信息，实际链接交给链接器。

```rust
use vec2;

pub fn main() {
    let a: vec::Vec2 = vec2::new(1, 2);
}
```

编译时用 `-M` 指定模块的类型定义文件：

```
saya main.saya -M vec2=build/vec2.td
```

typedef 文件（`.td`）由编译器用 `-t` 和 `-N` 参数生成：

```
saya vec2.saya -o build/vec2.ssa -t build/vec2.td -N vec2
```

typedef 实际就是合法的 Saya 源码，只包含公开的类型、函数签名：

```rust
pub struct vec2::Vec2 {
    x: i64,
    y: i64,
} // size: 16, align: 8
pub fn vec2::new(x: i64, y: i64) -> vec2::Vec2;
pub fn vec2::add(a: *vec2::Vec2, b: *vec2::Vec2) -> vec2::Vec2;
pub fn vec2::dot(a: *vec2::Vec2, b: *vec2::Vec2) -> i64;
```

## 接下来

### 自举

想要舒服地自举还需要一些语言特性，不想这么快。

### 构建工具

Hare 做了一个构建工具来简化和加速模块编译过程，但我想参考 [nob.h](https://github.com/tsoding/nob.h/) 和 `build.zig`，至少在用户层面上使用 Saya 语言来自己完成构建工作。

### Raylib Speedrun

完成了，或者说很早就完成了，用 [Raylib](https://github.com/raysan5/raylib) 写了个贪吃蛇：[github.com/13m0n4de/snake-saya](https://github.com/13m0n4de/snake-saya)。

实际上，Saya 参考 [北大编译实践在线文档](https://pku-minic.github.io/online-doc/) 的目录顺序实现了前期的功能，之后就一直以运行 Raylib 为目标。

## 哦……

写完整理参考资料时，才回想起 Saya 最开始的意义——为了做 [Reflections on Trusting Trust](https://www.cs.cmu.edu/~rdriley/487/papers/Thompson_1984_ReflectionsonTrustingTrust.pdf) 的实验，我准备造一个编译型语言……然后再自举……再插入后门……再……。

跳入了深不见底的兔子洞。

## 参考

- [https://astexplorer.net/](https://astexplorer.net/)
- [https://dontcallmedom.github.io/rfcref/abnf/web/](https://dontcallmedom.github.io/rfcref/abnf/web/)
- [https://git.sr.ht/~sircmpwn/harec/](https://git.sr.ht/~sircmpwn/harec/)
- [https://doc.rust-lang.org/beta/nightly-rustc/rustc_ast/ast/](https://doc.rust-lang.org/beta/nightly-rustc/rustc_ast/ast/)
- [https://pku-minic.github.io/online-doc/#/](https://pku-minic.github.io/online-doc/#/)
- [https://www.reddit.com/r/Compilers/comments/11vhl8r/storing_type_information/](https://www.reddit.com/r/Compilers/comments/11vhl8r/storing_type_information/)
- [https://www.microsoft.com/en-us/research/uploads/prod/2016/11/trees-that-grow.pdf](https://www.microsoft.com/en-us/research/uploads/prod/2016/11/trees-that-grow.pdf)
- [https://github.com/garritfra/qbe-rs](https://github.com/garritfra/qbe-rs)
