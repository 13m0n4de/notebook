---
date: 2024-06-15
categories:
  - HackerRank
tags:
  - HackerRank
  - Racket
  - Lisp
  - Functional Programming
---

# HackerRank in Racket: Part 3

<!-- more -->

## 22-Functions or Not?

数学中函数的定义为：

> 对于每个定义域中的元素（x 值），有唯一的值域元素（y 值）与之对应。

如果测试用例中所有 x 值都唯一地映射到 y 值，那么这些关系可以代表一个有效的函数。

函数签名：

```racket
valid-function? : Listof(Integer) -> Boolean
```

```racket title="solution"
#lang racket

;; valid-function? : Listof(Integer) -> Boolean
(define (valid-function? pairs)
  (define mapping (make-vector 501 -1))
  (for/and ([pair pairs])
    (match-let ([(list x y) pair])
      (let ([mapped-y (vector-ref mapping x)])
        (cond
          [(= mapped-y -1)
           (vector-set! mapping x y)
           #t]
          [(= mapped-y y) #t]
          [else #f])))))

(define (read-test-case)
  (for/list ([_ (in-range (read))])
    (list (read) (read))))

(define (read-test-cases)
  (for/list ([_ (in-range (read))])
    (read-test-case)))

(define test-cases (read-test-cases))
(for ([test-case test-cases])
  (if (valid-function? test-case)
      (displayln "YES")
      (displayln "NO")))
```

`for/and` 会在条件失败时短路。

读取时用 `read-line` 会比较麻烦，因为测试用例中带有 `\r`，需要指定 `'return-linefeed`。用 `read` 简单些。
