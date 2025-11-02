---
date: 2025-10-23
categories:
  - Scientific Witchery
  - Security
tags: [Hashcat, Functional Programming, Password Cracking, Python]
---

# Functional Pipeline Programming in Python

用 Python 写了个小工具，根据手机号段信息生成 [hashcat](https://github.com/hashcat/hashcat) 掩码。

仓库：[github.com/13m0n4de/purrify](https://github.com/13m0n4de/purrify)

平平无奇？看看这个：

```python title="purrify.py" linenums="87-96"
_ = sys.stdin > (
    pipe
    | foreach(parse_csv_line)
    | where(X.__len__() > min_length)
    | where(X[type_idx] == "MOBILE")
    | where(in_cities, geo_indices=geo_indices, cities=cities)
    | foreach(lambda x: (x[prefix_idx], int(x[length_idx])))
    | foreach(as_args(purrify))
    | foreach_do(print)
)
```

<!-- more -->

## 总是需要一个前言

前些天需要爆破某个加密压缩包，密码是某地区的手机号，这样简单的任务我居然发现自己没有合适的工具。

在网上简单搜寻了一阵子字典生成器，实现都有些怪异：向某个不知名网站发出网络请求获得所有符合要求的号码，有时甚至需要手动在 Excel 文件查找城市代码以及运营商号码。太奇怪了，甚至称得上恶心。

但更让我打消使用念头的，不是工具本身的问题，而是生成的字典文件实在太大，用起来很不方便。

## 冗长的发展

我需要的其实是「手机号码 hashcat 掩码生成器」，如果没有就得自己写了。

于是我继续搜索，找到了 [Felinize](https://github.com/Arnie97/felinize/)，基于 [libphonenumber](https://github.com/google/libphonenumber) 的手机号段数据，使用起来相当简单：

```
$ ./felinize.hs 北京 南京 < ranges.csv > ranges.hcmask
```

Felinize 是用 [Haskell](https://www.haskell.org/) 写的，Haskell 非常适合处理这种数据的场景，函数式管道的写法也相当漂亮：

```haskell
main = do
  args <- getArgs
  interact
    $ unlines
    . fmap (\line -> felinize [] False [] 0 $ line !! 0)
    . filter (numberLocation $ locationInArgs args)
    . filter (numberType $ (==) "MOBILE")
    . fmap (fmap trim . splitOn ";")
    . lines
 where
  numberLocation cond line = cond $ last line
  numberType     cond line = cond $ line !! 2
  locationInArgs args city = any (flip isInfixOf city) args
```

我凭借完全不够用的 Haskell 知识读了遍代码，大致弄明白了掩码生成逻辑。

libphonenumber 是 Google 开发的电话号码处理库，可以对世界各国/地区的电话号码进行解析、格式化和验证。它的元信息 [metadata.zip](https://github.com/google/libphonenumber/blob/master/metadata/metadata.zip) 中包含地区对应的号段信息，大概长这样：

```csv title="metadata/86/range.csv"
Prefix                ; Length ; Type       ; Tariff        ; Area Code Length ; National Only ; Operator         ; Format                         ; Timezone        ; Regions ; Geocode:en                                              ; Geocode:zh                      ; Provenance
10100                 ; 7      ; FIXED_LINE ; STANDARD_RATE ; 2                ; false         ;                  ; "shortcodes_with_prefix_2/5-6" ; "Asia/Shanghai" ; "CN"    ; "Beijing"                                               ; "北京市"
10[18]0[1-9]          ; 10     ; FIXED_LINE ; STANDARD_RATE ; 2                ; false         ;                  ; "fixed_2/4/4"                  ; "Asia/Shanghai" ; "CN"    ; "Beijing"                                               ; "北京市"
10[18][1-9]           ; 10     ; FIXED_LINE ; STANDARD_RATE ; 2                ; false         ;                  ; "fixed_2/4/4"                  ; "Asia/Shanghai" ; "CN"    ; "Beijing"                                               ; "北京市"
1300000               ; 11     ; MOBILE     ; STANDARD_RATE ;                  ; false         ; "china_unicom"   ; "mobile_3/4/4"                 ; "Asia/Shanghai" ; "CN"    ; "Jinan, Shandong"                                       ; "山东省济南市"
1300001               ; 11     ; MOBILE     ; STANDARD_RATE ;                  ; false         ; "china_unicom"   ; "mobile_3/4/4"                 ; "Asia/Shanghai" ; "CN"    ; "Changzhou, Jiangsu"                                    ; "江苏省常州市"
1300002               ; 11     ; MOBILE     ; STANDARD_RATE ;                  ; false         ; "china_unicom"   ; "mobile_3/4/4"                 ; "Asia/Shanghai" ; "CN"    ; "Chaohu, Anhui"                                         ; "安徽省巢湖市"
130001[2-489]         ; 11     ; MOBILE     ; STANDARD_RATE ;                  ; false         ; "china_unicom"   ; "mobile_3/4/4"                 ; "Asia/Shanghai" ; "CN"    ; "Tianjin"                                               ; "天津市"
```

它只是一个用 `;` 作分隔符的 CSV 文件。程序可以解析 CSV 文本，通过地区名称 `Geocode:xx` 筛选想要的号码前缀 `Prefix` 和号码长度 `Length`，再展开前缀，用任意数字补齐号码到指定长度。

比如天津市的某个号码前缀 `130001[2-489]` 应该展开为七位数字 `1300012`、`1300013`、`1300014`、`1300018`、`1300019`，而后 4 位就是任意数字组合。

Hashcat 的掩码文件 `.hcmask` 每一行都可选的自定义字符集和掩码，一般格式如下：

```
[?1,][?2,][?3,][?4,]mask
```

我可以定义多个字符集，用逗号分隔，掩码放在最后。例如刚刚天津市的某号段掩码如下，定义了 `23489` 字符集，用 `?1` 使用第一个自定义字符集，用 `?d` 使用自带的数字字符集：

```
23489,130001?1?d?d?d?d
```

Felinize 读取 CSV 文件，过滤符合地区的号码前缀，将其展开并生成字符集，最后输出符合 `.hcmask` 格式的字符集和掩码。

## 过于巧合的转折

但……我该用 Python 复刻一遍吗？只是为了换种更大众的语言？似乎没必要。

我完全提不起兴致，Felinize 相当好用，为什么要重复造轮子？况且用 Python 重写……代码会很“无趣”。

无聊中我开始网络漫游。

![the_problem_with_wikipedia.png](https://imgs.xkcd.com/comics/the_problem_with_wikipedia.png)

直到我开始翻看 Felinize 作者 [@Arnie97](https://github.com/Arnie97) 的主页。

我发现一个相当有趣的 Python 库：[pipetools](https://github.com/0101/pipetools)，@Arnie97 是作者之一。它可以实现类似于使用 Unix 管道的函数组合，允许任意函数的前向组合和管道连接——无需修饰它们或做任何额外的事情。

简而言之，它可以将这样的代码：

```python
def pyfiles_by_length(directory):
    all_files = os.listdir(directory)
    py_files = [f for f in all_files if f.endswith(".py")]
    sorted_files = sorted(py_files, key=len, reverse=True)
    numbered = enumerate(py_files, 1)
    rows = ("{0}. {1}".format(i, f) for i, f in numbered)
    return "\n".join(rows)
```

改成这样：

```python
pyfiles_by_length = (
    pipe
    | os.listdir
    | where(X.endswith(".py"))
    | sort_by(len).descending
    | (enumerate, X, 1)
    | foreach("{0}. {1}")
    | "\n".join
)
```

甚至可以向管道输入：

```python
result = some_input > pipe | foo | bar | boo
```

多酷，这可是在 Python 里。

## 对起承转合的偏执

我立马着手编写，最终得到了文章开头的代码（省略了转化掩码的函数 `purrify`，它的内部并不管道）：

```python hl_lines="14 23-32"
def parse_csv_line(line: str) -> list[str]:
    return [field.strip().strip('"') for field in line.rstrip("\n").split(";")]


def in_cities(row: list[str], cities: list[str], geo_indices: tuple[int]) -> bool:
    return any(
        city.lower() in row[idx].lower() for idx in geo_indices for city in cities
    )


def main():
    cities = sys.argv[1:]

    header = sys.stdin > pipe | take_first(1) | next | parse_csv_line
    prefix_idx = header.index("Prefix")
    length_idx = header.index("Length")
    type_idx = header.index("Type")
    geo_indices = header > (
        pipe | enumerate | where(X[1].startswith("Geocode:")) | foreach(X[0]) | tuple
    )
    min_length = max(prefix_idx, length_idx, type_idx, *geo_indices)

    _ = sys.stdin > (
        pipe
        | foreach(parse_csv_line)
        | where(X.__len__() > min_length)
        | where(X[type_idx] == "MOBILE")
        | where(in_cities, geo_indices=geo_indices, cities=cities)
        | foreach(lambda x: (x[prefix_idx], int(x[length_idx])))
        | foreach(as_args(purrify))
        | foreach_do(print)
    )
```

得益于 `sys.stdin` 实现了迭代器协议，能够遍历它返回文本流中的每一行，我可以轻松得到 CSV 的表头 `header`：

1. 将 `sys.stdin` 输入到 `pipe` 中
1. `take_first(1)` 返回包含第一行文本的列表
1. `next` 获取列表第一项数据（输入的第一行文本）
1. `parse_csv_line` 函数将文本按照 CSV 格式解析为列表

获取到必要的信息后（因为每个国家/地区的表头不同），我继续处理剩余的数据行。整个管道的流程如下：

1. `foreach(parse_csv_line)`：将每一行文本按 CSV 格式解析为字段列表
1. `where(X.__len__() > min_length)`：过滤掉字段数量不足的行（避免索引越界）
1. `where(X[type_idx] == "MOBILE")`：只保留类型为 `MOBILE` 的号码
1. `where(in_cities, ...)`：筛选符合指定地区的号码
1. `foreach(lambda x: (x[prefix_idx], int(x[length_idx])))`：提取号码前缀和长度，组成元组
1. `foreach(as_args(purrify))`：将元组解包为参数传入 `purrify` 函数，转换为掩码
1. `foreach_do(print)`：打印每个掩码到标准输出

**这一切都是惰性的**，只要将 `ranges.csv` 重定向至标准输入，掩码就自然地流向标准输出。

嗯，结束了，工具取名 **Purrify**，模仿自 Felinize。

- *Felinize*：*feline* (猫科的) + *-ize* (使...化)
- *Purrify*：*purr* (猫咪的呼噜声) + *-ify* (使...化)

代码仓库在：[github.com/13m0n4de/purrify](https://github.com/13m0n4de/purrify)。

你可以使用 [uv](https://github.com/astral-sh/uv) 安装 Purrify：

```
uv tool install git+https://github.com/13m0n4de/purrify
```

指定一个或多个城市名称，可以使用中文、英文或其他语言：

```
purrify 南京 shanghai < ranges.csv > phones.hcmask
hashcat -a 3 -m 13000 rar.hash phones.hcmask
```

如果需要一份字典文件，可以用 hashcat 从 `.hcmask` 文件生成：

```
hashcat -a 3 --stdout phones.hcmask > phones.list
```

## 比正片有意思的片尾彩蛋

看别人主页可不算视奸癖，当一个人同时写 Haskell 和安全工具，你就知道 TA 肯定还关注着许多好玩的——比如 @Arnie97 Star 的 [github.com/FiloSottile/whoami.filippo.io](https://github.com/FiloSottile/whoami.filippo.io)。

```
ssh whoami.filippo.io
```

它会识别出你是谁（你的 GitHub 账户），也许以后可以详细研究一下写一篇文章。

## 永远被跳过的致谢名单

- [github.com/Arnie97/felinize](https://github.com/Arnie97/felinize)
- [github.com/0101/pipetools](https://github.com/0101/pipetools)
- [pipetools’ documentation](https://0101.github.io/pipetools/doc/)
- [Hashcat Wiki: Mask Attack](https://hashcat.net/wiki/doku.php?id=mask_attack)
