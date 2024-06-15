---
date: 2024-06-11
categories:
  - HackerRank
tags:
  - HackerRank
  - Racket
  - Lisp
  - Functional Programming
---

# HackerRank in Racket: Part 1

<!-- more -->

## 00-Solve Me First FP

使用 `read` 读取命令行输入的两个数字，相加之后使用 `display` 输出结果。

```racket title="solution"
#lang racket

(display (+ (read) (read)))
```

`read` 读取表达式并返回对应的值。

```racket
(read [in]) → any
  in : input-port? = (current-input-port)
```

## 01-Hello World

```racket title="solution"
#lang racket

(display "Hello World")
```

## 02-Hello World N Times

使用 `in-range` 创建一个长度为输入数值的序列，并在每次迭代它时输出 `Hello World\n`。

```racket title="solution"
#lang racket

(for ([_ (in-range (read))])
  (display "Hello World\n"))
```

## 03-List Replication

函数签名：

```racket
replicate-elements : Integer (Listof Integer) -> (Listof Integer)
```

利用 `append-map` 和 `make-list` 创建元素重复的新列表。

```racket title="solution"
#lang racket

;; replicate-elements : Integer (Listof Integer) -> (Listof Integer)
(define (replicate-elements n lst)
  (append-map (lambda (num) (make-list n num)) lst))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(let* ([input (read-list)]
       [n (car input)]
       [lst (cdr input)])
  (for-each displayln (replicate-elements n lst)))
```

（HackerRank 居然不支持 `typed/racket`）

## 04-Filter Array

函数签名：

```racket
filter-less-than : Integer (Listof Integer) -> (Listof Integer)
```

使用 `filter` 过滤出小于 `delim` 元素。

```racket title="solution"
#lang racket

;; filter-less-than : Integer (Listof Integer) -> (Listof Integer)
(define (filter-less-than delim lst)
  (filter (lambda (num) (< num delim)) lst))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(let* ([input (read-list)]
       [n (car input)]
       [lst (cdr input)])
  (for-each displayln (filter-less-than n lst)))
```

## 05-Filter Positions in a List

函数签名：

```racket
remove-odd : (Listof Integer) -> (Listof Integer)
```

`remove-odd-helper` 函数检测当前元素位置 `index` 是否为奇数：

- 如果是奇数，则不修改累加器 `acc`，直接递归调用 `remove-odd-helper`；
- 如果是偶数，则将当前元素加入累加器 `acc`，而后递归调用 `remove-odd-helper`。

列表处理完毕时，返回累加器 `acc` 的倒序。

```racket title="solution"
#lang racket

;; remove-odd : (Listof Integer) -> (Listof Integer)
(define (remove-odd lst)
  (let remove-odd-helper ([lst lst] [index 0] [acc '()])
    (cond
      [(empty? lst) (reverse acc)]
      [(odd? index) (remove-odd-helper (cdr lst) (+ index 1) acc)]
      [else (remove-odd-helper (cdr lst) (+ index 1) (cons (car lst) acc))])))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(let* ([input (read-list)]
       [lst (cdr input)])
  (for-each displayln (remove-odd lst)))
```

## 06-Array Of N Elements

`identity` 函数不做任何操作，只是将其参数原样返回，所以 `#!racket (build-list n identity)` 可以得到从 `0` 到 `n - 1` 的列表。

```racket title="solution" hl_lines="3-4"
#lang racket

(define (f n)
  (build-list n identity)）
  
(define n (string->number (read-line (current-input-port) 'any)))
(print (list(f n)))
```

我不喜欢它给我的代码模板。

## 07-Reverse a List

要求不能使用 `reverse` 函数。

函数签名：

```racket
reverse-list : (Listof Integer) -> (Listof Integer)
```

递归地从列表头部开始，每次将列表的第一个元素添加到累积结果的前面，直到列表为空，这样就实现了列表的翻转。

```racket title="solution"
#lang racket

;; reverse-list : (Listof Integer) -> (Listof Integer)
(define (reverse-list lst)
  (let reverse-list-helper ([lst lst] [acc '()])
    (cond
      [(empty? lst) acc]
      [else
       (reverse-list-helper
        (cdr lst)
        (cons (car lst) acc))])))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(for-each displayln (reverse-list (read-list)))
```

相当于使用 `foldl` + `cons`：

```racket title="solution"
(define (reverse-list lst)
  (foldl cons '() lst))
```

## 08-Sum of Odd Elements

函数签名：

```racket
sum-odd : (Listof Integer) -> Integer
```

手动递归版：

```racket title="solution"
#lang racket

;; sum-odd : (Listof Integer) -> Integer
(define (sum-odd lst)
  (let sum-odd-helper ([lst lst] [acc 0])
    (cond
      [(empty? lst) acc]
      [else
       (define x (car lst))
       (if (odd? x)
           (sum-odd-helper (cdr lst) (+ acc x))
           (sum-odd-helper (cdr lst) acc))])))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(displayln (sum-odd (read-list)))
```

使用 `apply` + `filter`：

```racket title="solution"
(define (sum-odd lst)
  (apply + (filter odd? lst)))
```

## 09-List Length

函数签名：

```racket
list-length (Listof Integer) -> Integer
```

```racket title="solution"
#lang racket

;; list-length (Listof Integer) -> Integer
(define (list-length lst)
  (let list-length-helper ([lst lst] [acc 0])
    (if (empty? lst)
        acc
        (list-length-helper (cdr lst) (+ acc 1)))))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(displayln (list-length (read-list)))
```

## 10-Update List

函数签名：

```racket
update-list : (Listof Integer) -> (Listof Integer)
```

`map` + `abs`。

```racket title="solution"
#lang racket

;; update-list : (Listof Integer) -> (Listof Integer)
(define (update-list lst)
  (map abs lst))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(for-each displayln (update-list (read-list)))
```
