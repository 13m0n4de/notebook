---
date: 2026-02-28
categories:
  - Programming Language
tags:
  - Programming Language
  - Compiler
  - QBE
  - SSA
---

# Saya Lang: Loop Break Value

给 [Saya](https://github.com/13m0n4de/saya) 实现些新特性，让 `loop { ... }` 表达式可以通过 `break my_value;` 表达式返回一个值。

<!-- more -->

## Loop Break Value

这个特性参考自 Rust 的 [RFC 1624](https://rust-lang.github.io/rfcs/1624-loop-break-value.html)：

```rust
let x: i64 = loop {
    break 42;
};
```

`loop { ... }` 表达式的类型由 `break` 决定：

- `break value`：loop 类型 = break 值的类型
- `break`：loop 类型 = `()`
- 没有 `break`（无限循环）：loop 类型 = `!`

`while` 不支持带值的 `break`，因为 `while` 条件变 `false` 时自然退出，该返回什么没法确定。只有 `loop` 能保证退出路径全部经过 `break`，类型才能完全由 `break` 决定。

下面的例子中三条路都汇入 `loop` 的结束点，`x` 的值取决于走了哪条路：

```rust
let x: i64 = loop {
    if cond_a { break 1; }
    if cond_b { break 2; }
    if cond_c { break 3; }
};
```

这是 SSA 里 `Phi` 指令的经典场景，同一个变量，来自不同前驱块：

```
@loop.0.end
    %x =l phi @if.1.then 1, @if.2.then 2, @if.3.then 3
```

`break` 可以出现任意多次，`Phi` 的前驱数量不固定。而 [qbe-rs](https://github.com/garritfra/qbe-rs/) 的 `Phi` 指令只支持恰好两个前驱，需要先解决这个限制。

## 让 qbe-rs 支持多前驱的 Phi 指令

也就是说，要提一个 [PR](https://github.com/garritfra/qbe-rs/pull/48)。它以前的 `Instr::Phi` 只支持两个前驱（predecessor），我从 `Phi(String, Value, String, Value),` 改成了 `Phi(Vec<String, Value>)`：

```diff
index 6d5dffa..28612fd 100644
--- a/src/lib.rs
+++ b/src/lib.rs
@@ -303,7 +303,7 @@ pub enum Instr<'a> {
 
     // Phi instruction
     /// Selects value based on the control flow path into a block.
-    Phi(String, Value, String, Value),
+    Phi(Vec<(String, Value)>),
 
     // Program termination
     /// Terminates the program with an error
@@ -417,11 +417,13 @@ impl fmt::Display for Instr<'_> {
             Self::Ultof(val) => write!(f, "ultof {val}"),
             Self::Vastart(val) => write!(f, "vastart {val}"),
             Self::Vaarg(ty, val) => write!(f, "vaarg{ty} {val}"),
-            Self::Phi(label_1, val_if_label_1, label_2, val_if_label_2) => {
-                write!(
-                    f,
-                    "phi @{label_1} {val_if_label_1}, @{label_2} {val_if_label_2}"
-                )
+            Self::Phi(args) => {
+                let formatted_args = args
+                    .iter()
+                    .map(|(label, value)| format!("@{label} {value}"))
+                    .collect::<Vec<String>>()
+                    .join(", ");
+                write!(f, "phi {formatted_args}")
             }
             Self::Hlt => write!(f, "hlt"),
         }
```

## 类型检查

对于 `loop` 表达式，需要推断它的类型，也就是收集所有 `break` 的类型。

`ScopeKind` 里加了 `Loop` 类别：

```rust
pub enum ScopeKind {
    Loop {
        break_type: Option<TypeId>,
        allows_break_value: bool,
    },
}
```

`break_type` 初始为 `None`，每遇到一个带值的 `break`，就把值的类型写进去；第二个 `break` 时类型必须一致，否则报错：

```rust
match *break_type {
    None => *break_type = Some(val_type),
    Some(existing) if existing != val_type => {
        return Err(TypeError::new(
            format!(
                "break value type mismatch: expected {}, found {}",
                self.types.type_name(existing),
                self.types.type_name(val_type),
            ),
            expr.span,
        ));
    }
    _ => {}
}
```

离开 loop 作用域时，把 `break_type` 作为整个表达式的类型。没有 `break` 的无限循环类型为 `!`：

```rust
type_id: break_type.unwrap_or(TypeId::NEVER),
```

`allows_break_value` 用于区分 `while` 和 `loop`。`while` 创建时 `allows_break_value` 为 `false`，`loop` 创建时 `allows_break_value` 为 `true`。带值的 `break` 出现在 `while` 里会报错。

## 代码生成

`LoopContext` 新增 `break_values` 字段，在遍历循环体时收集每个前驱块和对应值：

```rust
struct LoopContext {
    continue_label: String,
    break_label: String,
    break_values: Vec<(String, qbe::Value)>,
}
```

生成 `break value` 时，记录当前块的标签作为前驱：

```rust
let predecessor = qfunc
    .blocks
    .last()
    .expect("...")
    .label
    .clone();

self.loops
    .last_mut()
    .expect("...")
    .break_values
    .push((predecessor, val.into()));
```

遍历完循环体，把收集到的 `break_values` 整体变成一条 `Phi` 指令：

```rust
qbe::Instr::Phi(loop_ctx.break_values.clone())
```

对应前面三个 `break` 的例子，生成的 QBE IL 如下：

```
	jmp @loop.0.body
@loop.0.body

@if.1.cond
	%temp.0 =w loadub %cond_a
	jnz %temp.0, @if.1.then, @if.1.end
@if.1.then
	jmp @loop.0.end
@never.2

@if.1.end

@if.3.cond
	%temp.1 =w loadub %cond_b
	jnz %temp.1, @if.3.then, @if.3.end
@if.3.then
	jmp @loop.0.end
@never.4

@if.3.end

@if.5.cond
	%temp.2 =w loadub %cond_c
	jnz %temp.2, @if.5.then, @if.5.end
@if.5.then
	jmp @loop.0.end
@never.6

@if.5.end
	jmp @loop.0.body
@loop.0.end
	%temp.3 =l phi @if.1.then 1, @if.3.then 2, @if.5.then 3
	storel %temp.3, %x
```

每个 `break` 所在块跳转到 `@loop.0.end`，`Phi` 根据来自哪个前驱选出对应的值。

（也许我得给每种块单独的计数器，`if` 序号不是连续的……）

## 参考

- [Rust RFC 1624 loop_break_value](https://rust-lang.github.io/rfcs/1624-loop-break-value.html)
