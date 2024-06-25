---
date: 2024-06-16
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

## 23-Compute the Perimeter of a Polygon

函数签名：

```racket
distance : (Listof Integer) (Listof Integer) -> Number
perimeter : (Listof (Listof Integer)) -> Number
```

依次计算每个边的长度（两点距离），加在一起就是周长。

```racket title="solution"
#lang racket

;; distance : (Listof Integer) (Listof Integer) -> Number
(define (distance point-a point-b)
  (let ([ax (first point-a)]
        [ay (second point-a)]
        [bx (first point-b)]
        [by (second point-b)])
    (sqrt (+ (expt (- bx ax) 2)
             (expt (- by ay) 2)))))

;; perimeter : (Listof (Listof Integer)) -> Number
(define (perimeter points)
  (define first-point (first points))
  (let perimeter-helper ([acc 0.0]
                         [remaining-points (cdr points)]
                         [prev-point first-point])
    (if (empty? remaining-points)
        (+ acc (distance prev-point first-point))
        (perimeter-helper (+ acc (distance prev-point (first remaining-points)))
                          (cdr remaining-points)
                          (first remaining-points)))))

(define (read-points)
  (for/list ([_ (in-range (read))])
    (list (read) (read))))

(displayln (perimeter (read-points)))
```

## 24-Compute the Area of a Polygon

$$
S={\frac {1}{2}}{\begin{vmatrix}x_{1}&x_{2}&x_{3}&{...}&x_{n}\\y_{1}&y_{2}&y_{3}&{...}&y_{n}\end{vmatrix}}={\frac {1}{2}}\left({\begin{vmatrix}x_{1}&x_{2}\\y_{1}&{y_{2}}\end{vmatrix}}+{\begin{vmatrix}x_{2}&x_{3}\\y_{2}&{y_{3}}\end{vmatrix}}+...+{\begin{vmatrix}x_{n-1}&x_{n}\\y_{n-1}&{y_{n}}\end{vmatrix}}+{\begin{vmatrix}x_{n}&x_{1}\\y_{n}&{y_{1}}\end{vmatrix}}\right)
$$
