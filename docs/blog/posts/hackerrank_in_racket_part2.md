---
date: 2024-06-13
categories:
  - HackerRank
tags:
  - HackerRank
  - Racket
  - Lisp
  - Functional Programming
---

# HackerRank in Racket: Part 2

<!-- more -->

## 11-Evaluating e^x

函数签名：

```racket
factorial : Integer -> Integer
eval-ex : Real -> Real
```

```racket title="solution"
#lang racket

;; factorial : Integer -> Integer
(define (factorial n)
  (let factorial-helper ([acc 1] [n n])
    (if (= n 0)
        acc
        (factorial-helper (* acc n) (- n 1)))))

;; eval-ex : Real -> Real
(define (eval-ex x)
  (let eval-ex-helper ([acc 0] [y 0])
    (if (= y 10)
        acc
        (eval-ex-helper
         (+ acc (/ (expt x y) (factorial y)))
         (+ y 1)))))

(define (read-list)
  (let read-list-helper ([acc '()])
    (let ([x (read)])
      (if (eof-object? x)
          (reverse acc)
          (read-list-helper (cons x acc))))))

(let* ([input (read-list)]
       [lst (cdr input)])
  (for-each (lambda (x)
              (displayln (eval-ex x)))
            lst))
```

## 12-Area Under Curves and Volume of Revolving a Curve

使用定积分计算曲线下面积和旋转曲线的体积。

函数签名：

```racket
polynomial : Real (Listof Real) (Listof Real) -> Real
integrate : Real Real Real (Listof Real) (Listof Real) (Real Real -> Real) -> Real
trapezoidal-area : Real Real Real (Listof Real) (Listof Real) -> Real
disk-method-volume : Real Real Real (Listof Real) (Listof Real) -> Real
```

计算多项式：

$$
(a_1)x^{b_1} + (a_2)x^{b_2} + (a_3)x^{b_3} + \ldots + (a_n)x^{b_n}
$$

```racket
(define (polynomial x coefficients powers)
  (for/fold ([acc 0])
            ([coefficient coefficients]
             [power powers])
    (+ acc (* coefficient (expt x power)))))
```

[梯形法](https://en.wikipedia.org/wiki/Trapezoidal_rule)计算面积：

$$
\displaystyle \int _{a}^{b}f(x)\,dx\approx \sum _{k=1}^{N}{\frac {f(x_{k-1})+f(x_{k})}{2}}\Delta x_{k}.
$$

```racket
(define (trapezoidal-area a b delta-x coefficients powers)
  (let trapezoidal-area-helper ([current-x a]
                                [current-y (polynomial a coefficients powers)]
                                [acc 0])
    (let ([next-x (+ current-x delta-x)])
      (cond
        [(> current-x b) acc]
        [(> next-x b) acc]
        [else
         (let* ([next-y (polynomial next-x coefficients powers)]
                [area (* delta-x (/ (+ current-y next-y) 2))])
           (trapezoidal-area-helper next-x next-y (+ acc area)))]))))
```

[圆盘法](https://en.wikipedia.org/wiki/Solid_of_revolution)计算体积：

$$
{\displaystyle V=\pi \int _{a}^{b}\left|f(y)^{2}-g(y)^{2}\right|\,dy\,.}
$$

```racket
(define (disk-method-volume a b delta-x coefficients powers)
  (let disk-method-volume-helper ([current-x a]
                                 [current-y (polynomial a coefficients powers)]
                                 [acc 0])
    (let ([next-x (+ current-x delta-x)])
      (cond
        [(> current-x b) acc]
        [(> next-x b) acc]
        [else
         (let* ([next-y (polynomial next-x coefficients powers)]
                [volume (/ (* delta-x pi (+ (sqr current-y) (sqr next-y))) 2)])
           (disk-method-volume-helper next-x next-y (+ acc volume)))]))))
```

这两个函数计算积分的部分是通用的，创建 `integrate` 函数，该函数接受一个特定的积分计算函数作为参数：

```racket
(define (integrate a b delta-x coefficients powers integrand-fn)
  (let integrate-helper ([current-x a]
                         [current-y (polynomial a coefficients powers)]
                         [acc 0])
    (let ([next-x (+ current-x delta-x)])
      (cond
        [(> current-x b) acc]
        [(> next-x b) acc]
        [else
         (let* ([next-y (polynomial next-x coefficients powers)]
                [value (integrand-fn current-y next-y)])
           (integrate-helper next-x next-y (+ acc value)))]))))

(define (trapezoidal-area a b delta-x coefficients powers)
  (integrate a b delta-x coefficients powers
             (lambda (current-y next-y)
               (* delta-x (/ (+ current-y next-y) 2)))))

(define (disk-method-volume a b delta-x coefficients powers)
  (integrate a b delta-x coefficients powers
             (lambda (current-y next-y)
               (/ (* delta-x pi (+ (sqr current-y) (sqr next-y))) 2))))
```

使用 `read-line`、`string-split`、`string->number` 解析输入数值：

```racket
(define (parse-line line)
  (map string->number (string-split line)))

(define (read-input)
  (let ([coefficients (parse-line (read-line))]
        [powers (parse-line (read-line))]
        [range (parse-line (read-line))])
    (values coefficients powers (first range) (second range))))
```

完整代码：

```racket title="solution"
#lang racket

;; polynomial : Real (Listof Real) (Listof Real) -> Real
(define (polynomial x coefficients powers)
  (for/fold ([acc 0])
            ([coefficient coefficients]
             [power powers])
    (+ acc (* coefficient (expt x power)))))

;; integrate : Real Real Real (Listof Real) (Listof Real) (Real Real -> Real) -> Real
(define (integrate a b delta-x coefficients powers integrand-fn)
  (let integrate-helper ([current-x a]
                         [current-y (polynomial a coefficients powers)]
                         [acc 0])
    (let ([next-x (+ current-x delta-x)])
      (cond
        [(> current-x b) acc]
        [(> next-x b) acc]
        [else
         (let* ([next-y (polynomial next-x coefficients powers)]
                [value (integrand-fn current-y next-y)])
           (integrate-helper next-x next-y (+ acc value)))]))))

;; trapezoidal-area : Real Real Real (Listof Real) (Listof Real) -> Real
(define (trapezoidal-area a b delta-x coefficients powers)
  (integrate a b delta-x coefficients powers
             (lambda (current-y next-y)
               (* delta-x (/ (+ current-y next-y) 2)))))

;; disk-method-volume : Real Real Real (Listof Real) (Listof Real) -> Real
(define (disk-method-volume a b delta-x coefficients powers)
  (integrate a b delta-x coefficients powers
             (lambda (current-y next-y)
               (/ (* delta-x pi (+ (sqr current-y) (sqr next-y))) 2))))


(define (parse-line line)
  (map string->number (string-split line)))

(define (read-input)
  (let ([coefficients (parse-line (read-line))]
        [powers (parse-line (read-line))]
        [range (parse-line (read-line))])
    (values coefficients powers (first range) (second range))))

(define-values (coefficients powers a b) (read-input))
(define delta-x 0.001)

(displayln (trapezoidal-area a b delta-x coefficients powers))
(displayln (disk-method-volume a b delta-x coefficients powers))
```

## 13-Lambda Calculus - Reductions #1

[Lambda 演算](https://en.wikipedia.org/wiki/Lambda_calculus)表达式简化。

$$
((λx.(x y))(λz.z))
$$

1. 将 $(λx.(x y))$ 应用于 $(λz.z)$，使用 $(λz.z)$ 替换 $x$ 得到 $((λz.z) y)$；
1. 将 $(λz.z)$ 应用于 $y$，得到 $y$。

```title="solution"
y
```

## 14-Lambda Calculus - Reductions #2

$$
((λx.((λy.(x y))x))(λz.w))
$$

1. 将 $(λx.((λy.(x y))x))$ 应用于 $(λz.w)$，使用 $(λz.w)$ 替换 $x$ 得到 $((λy.((λz.w) y))(λz.w))$；
1. 将 $(λy.((λz.w) y))$ 应用于 $(λz.w)$，使用 $(λz.w)$ 替换 $y$ 得到 $((λz.w) (λz.w))$；
1. 将 $(λz.w)$ 应用于自身，它没有使用参数 $z$，只是简单返回 $w$。

```title="solution"
w
```

## 15-Lambda Calculus - Reductions #3

$$
((λx.(x x))(λx.(x x)))
$$

函数 $(λx.(x x))$ 应用到自身上，根据 [β-规约](https://en.wikipedia.org/wiki/Lambda_calculus#%CE%B2-reduction)，将 $x$ 替换为 $(λx.(x x))$，得到 $((λx.(x x))(λx.(x x)))$，这个结果恰好又是原表达式的副本。

因此，这个表达式在逻辑上会无限次地重复自己。这种表达式在 λ 演算中被称为[不动点组合子](https://en.wikipedia.org/wiki/Fixed-point_combinator)。

```title="solution"
CAN'T REDUCE
```

## 16-Lambda Calculus - Reductions #4

$$
(λg.((λf.((λx.(f (x x)))(λx.(f (x x))))) g))
$$

1. 将 $(λf.((λx.(f (x x)))(λx.(f (x x)))))$ 应用于 $g$，使用 $g$ 替换 $f$ 得到 $((λx.(g (x x)))(λx.(g (x x))))$；
1. $((λx.(g (x x)))(λx.(g (x x))))$ 是一个不动点组合子；

这个表达式通过自我应用来构造一个不动点组合子，接受一个函数 $g$ 并返回 $g$ 的不动点。这个表达式无法通过β-规约简化为单一项，因为它始终保持自引用的递归结构。

```title="solution"
CAN'T REDUCE
```

## 17-Lambda Calculus - Evaluating Expressions #1

$$
(λx.x+1)3
$$

```title="solution"
4
```

## 18-Lambda Calculus - Evaluating Expressions #2

$$
(λx.x+1)((λy.y+2)3)
$$

1. 计算 $(λy.y+2)3$ 得到 $5$。
1. 用 $5$ 替换 $(λx.x+1)$ 中的 $x$，得到结果 $6$。

```title="solution"
6
```

## 19-Lambda Calculus - Evaluating Expressions #3

$$
λx.λy.x^{47}y
$$

> 邱奇数为使用邱奇编码的自然数表示法，而用以表示自然数 $n$ 的高阶函数是个任意函数 $f$ 映射到它自身的n重函数复合之函数，简言之，数的“值”即等价于参数被函数包裹的次数。

$λx.λy.x^{47}y$ 意味着函数将 $x$ 应用了 $47$ 次到 $y$ 上。

```title="solution"
47
```

## 20-Lambda Calculus - Evaluating Expressions #4

$$
λx.λy.x(xy)
$$

自然数 $2$ 的函数定义为 $2fx=f(fx)$，Lambda 表达式为 $λf.λx.f(fx)$。

```title="solution"
2
```

## 21-Lambda Calculus - Evaluating Expressions #5

$$
λx.λy.y
$$

自然数 $0$ 的函数定义为 $0fx=x$，Lambda 表达式为 $λf.λx.x$。

```title="solution"
0
```
