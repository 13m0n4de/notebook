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

这里是使用 Racket 完成 HackerRank 函数式编程题目的第三章，包含函数关系和几何计算（22 - 26 题）。

<!-- more -->

仓库：[13m0n4de/HackerRank-FP-Solutions](https://github.com/13m0n4de/HackerRank-FP-Solutions)

- [Part 1: Problem 00 - 10](./hackerrank_in_racket_part1.md)
- [Part 2: Problem 11 - 21](./hackerrank_in_racket_part2.md)
- [Part 3: Problem 22 - 26](./hackerrank_in_racket_part3.md)

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

计算多边形面积的[鞋带公式 (Shoelace formula)](https://en.wikipedia.org/wiki/Shoelace_formula)：

$$
S={\frac {1}{2}}{\begin{vmatrix}x_{1}&x_{2}&x_{3}&{...}&x_{n}\\y_{1}&y_{2}&y_{3}&{...}&y_{n}\end{vmatrix}}={\frac {1}{2}}\left({\begin{vmatrix}x_{1}&x_{2}\\y_{1}&{y_{2}}\end{vmatrix}}+{\begin{vmatrix}x_{2}&x_{3}\\y_{2}&{y_{3}}\end{vmatrix}}+...+{\begin{vmatrix}x_{n-1}&x_{n}\\y_{n-1}&{y_{n}}\end{vmatrix}}+{\begin{vmatrix}x_{n}&x_{1}\\y_{n}&{y_{1}}\end{vmatrix}}\right)
$$

函数签名：

```racket
cross-product : (Listof Integer) (Listof Integer) -> Number
area : (Listof (Listof Integer)) -> Number
```

```racket title="solution"
#lang racket

;; cross-product : (Listof Integer) (Listof Integer) -> Number
(define (cross-product point-a point-b)
  (let ([ax (first point-a)]
        [ay (second point-a)]
        [bx (first point-b)]
        [by (second point-b)])
    (- (* ax by) (* bx ay))))

;; area : (Listof (Listof Integer)) -> Number
(define (area points)
  (define first-point (first points))
  (let shoelace ([acc 0.0]
                 [remaining-points (cdr points)]
                 [prev-point first-point])
    (if (empty? remaining-points)
        (/ (abs (+ acc (cross-product prev-point first-point))) 2)
        (shoelace (+ acc (cross-product prev-point (first remaining-points)))
                  (cdr remaining-points)
                  (first remaining-points)))))

(define (read-points)
  (for/list ([_ (in-range (read))])
    (list (read) (read))))

(displayln (area (read-points)))
```

和计算周长时差不多，在每次计算时更新前后点和剩余点，并保存第一个点用于最后一个叉乘项的计算。

## 25-Computing the GCD

改进版的欧几里得算法：[Euclidean_algorithm](https://en.wikipedia.org/wiki/Greatest_common_divisor?oldformat=true#Euclidean_algorithm)

函数签名：

```racket
gcd : Integer Integer -> Integer
```

```racket title="solution"
#lang racket

;; gcd : Integer Integer -> Integer
(define (gcd x y)
  (let [(r (remainder x y))]
    (if (= r 0)
        y
        (gcd y r))))

(displayln (gcd (read) (read)))
```

## 26-Fibonacci Numbers

函数签名：

```racket
fibonacci : Integer -> Integer
```

```racket title="solution"
#lang racket

;; fibonacci : Integer -> Integer
(define (fibonacci n)
  (define (fib-helper a b count)
    (if (= count 3)
        (+ a b)
        (fib-helper b (+ a b) (- count 1))))
  (cond
    [(= n 1) 0]
    [(= n 2) 1]
    [else (fib-helper 0 1 n)]))

(displayln (fibonacci (read)))
```
