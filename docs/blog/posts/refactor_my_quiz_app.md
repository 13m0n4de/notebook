---
date: 2025-05-28
categories: []
tags: [Rust, Leptos, Axum, Yew, WASM, CSR, SSR]
---

# Refactor My Quiz App

花了几天把 [NekoQuiz](https://github.com/13m0n4de/neko-quiz) 完全重构，从 Axum + Yew 到 Axum + Leptos，从 CSR 到 SSR with hydration。

远在这次重构之前，我就已经没有了使用它的机会，也许这是最后一次大更新。（尽管我不愿意那么想，这样的想法会成为项目被“遗弃”的第一步）

至少能确定的是，已经到了进行总结的最佳时刻。

<!-- more -->

## NekoQuiz 和猫咪问答

NekoQuiz 来源于 [USTC Hackergame](https://hack.lug.ustc.edu.cn/) 的题目“猫咪问答”，它由一系列问题组成，要求选手仅通过 **网络信息检索** 找到答案。

例如：

> Q：不严格遵循协议规范的操作着实令人生厌，好在 IETF 于 2021 年成立了 Protocol Police 以监督并惩戒所有违背 RFC 文档的行为个体。假如你发现了某位同学可能违反了协议规范，根据 Protocol Police 相关文档中规定的举报方法，你应该将你的举报信发往何处？
>
> A：与去年的鸽子题一脉相承的搞笑 RFC 题。搜索 "RFC protocol police"，优秀的搜索引擎可以给出正确的 RFC 编号：rfc8962。全文搜索 "report"，可以找到：
>
> ```
> 6.  Reporting Offenses
>    Send all your reports of possible violations and all tips about
>    wrongdoing to /dev/null.  The Protocol Police are listening and will
>    take care of it.
> ```
>
> 所以答案为 `/dev/null`。

其他题目也很有趣，如果你对它们感兴趣的话：

- [2020 年猫咪问答++ 题解](https://github.com/USTC-Hackergame/hackergame2020-writeups/blob/master/official/%E7%8C%AB%E5%92%AA%E9%97%AE%E7%AD%94++/README.md)
- [2021 年猫咪问答 Pro Max 题解](https://github.com/USTC-Hackergame/hackergame2021-writeups/blob/master/official/%E7%8C%AB%E5%92%AA%E9%97%AE%E7%AD%94%20Pro%20Max/README.md)
- [2022 年猫咪问答喵题解](https://github.com/USTC-Hackergame/hackergame2022-writeups/blob/master/official/%E7%8C%AB%E5%92%AA%E9%97%AE%E7%AD%94%E5%96%B5/README.md)
- [2023 年猫咪小测题解](https://github.com/USTC-Hackergame/hackergame2023-writeups/blob/master/official/%E7%8C%AB%E5%92%AA%E5%B0%8F%E6%B5%8B/README.md)
- [2024 年猫咪问答（Hackergame 十周年纪念版）题解](https://github.com/USTC-Hackergame/hackergame2024-writeups/blob/master/official/%E7%8C%AB%E5%92%AA%E9%97%AE%E7%AD%94%EF%BC%88Hackergame%20%E5%8D%81%E5%91%A8%E5%B9%B4%E7%BA%AA%E5%BF%B5%E7%89%88%EF%BC%89/README.md)

**信息检索能力是最基础也最宝贵的计算机技能，尤其在这个被 AI 笼罩着模糊阴影的 202X 年。**

## NekoQuiz 是个不太有趣的项目

USTC 猫咪问答的形式非常简单，一个页面，几个表单框，一个提交按钮。印象中前端用了 Bootstrap，后端是 Node.js。程序上相当普通，甚至可以说“无聊”。

而作为复刻项目的 NekoQuiz 乍一看不是这样：Tailwind CSS、WASM、TOML 配置、热重载（曾经）。实际上却是没差，这些花哨的词汇对 Quiz App 来说帮助不大，它们的出现是因为个人意愿超出了实际需求：

1. 校内的 CTF 比赛需要信息检索题（这是委婉的说法，确切来说是我的一厢情愿）
1. 我想用 Rust 写 Web App

我摸索着学习 Web 开发中相对新潮的事物，把它们应用进来，可能算是技术栈上狭义的“进步”，但我绝对不认为这很必要和有趣。

## 老一套

Rust 的 Web 开发体验很奇妙，总的来说体感不错。

最初我使用 Yew 作为前端，它和 React 的概念很像，`#!rust #[function_component]` 对应 React 的函数组件，`#!rust use_reducer_eq` 类似 React 的 `#!javascript useReducer`。在组件挂载时通过 `#!rust use_effect_with` 获取 Quiz 数据，这和 React 的 `#!javascript useEffect` 几乎一模一样。

网络请求使用 `#!rust gloo_net::Request::get` 发送，整个异步操作被包装在 `#!rust wasm_bindgen_futures::spawn_local()` 中执行。

```rust
pub async fn get_quiz() -> Result<Quiz, QuizError> {
    let response = Request::get("/api/quiz").send().await?;
    Ok(response.json::<Quiz>().await?)
}

impl AppContext {
    pub fn get_quiz(&self) {
        let state = self.state.clone();
        spawn_local(async move {
            match get_quiz().await {
                // ...
            }
        });
    }
}

#[function_component(App)]
pub fn app() -> Html {
    let state = use_reducer_eq(AppState::default);
    let context = AppContext::new(state.clone());

    {
        let context = context.clone();
        use_effect_with((), move |()| {
            context.get_quiz();
        });
    }

    // ...
}
```

前端代码通过 [Trunk](https://trunkrs.dev/) 编译为 WASM 和相关静态资源，并在后端的 Axum 路由中作为静态文件服务挂载。这种情况下，Axum 既充当 API 服务器又充当静态文件服务器：

```rust
pub async fn get_quiz(State(state): State<Arc<AppState>>) -> Json<Quiz> {
    Json(Quiz {
        title: state.title().await,
        questions: state.questions().await,
        version: state.version().await,
    })
}

async fn run() -> AppResult<()> {
    // ...
    Router::new()
        .nest_service("/", ServeDir::new(serve_dir))
        .route("/api/quiz", get(get_quiz))
    // ...
}
```

本质上是前后端分离的 CSR (client-side rendering) 模式。

## 和新方法

放出重构的代码之前，先聊聊 Web 技术的历史。

### PHP 是 SSR 吗？

哪怕时间倒退几年，SSR (server-side rendering) 也不是一个新概念，JSP 和 PHP 都是 SSR（至少字面意义上），只是当时并没有 SSR 的说法——没什么东西是 CSR 的。

**博学多闻 [容易：成功]**：传统的渲染方式中，由服务端渲染完整的 HTML 给浏览器，每次的交互都依靠表单提交并带来页面刷新。是的，体验并不好，对挑剔的现代人来说。

**天人感应 [困难：成功]**：夜风从半开的窗户挤进房间，带着远方工厂的废气，漆黑的角落中方形玻璃投射出冷白色的光芒。一位少年蜷缩在椅子里，他习惯了在手指下落的瞬间眨眼，黑暗与纯白重合，等待凌乱的色彩重新覆盖玻璃。指纹在塑料表面留下油腻的轨迹，这些轨迹将比他的童年存在更久，而网络无限。

定义虽如此，我相信 SSR 这个称呼对于 JSP / PHP 是没有意义的，就如同 [@Huli 所说](https://blog.huli.tw/2023/11/27/server-side-rendering-ssr-and-isomorphic/)：

> 就像是如果我們把「飲料」定義為「可以喝的液體」，那你能不能說酸辣湯也是一種飲料？照定義來看沒有問題，但當有人問你「最喜歡喝的飲料是什麼？」的時候，你會說酸辣湯嗎？應該不會，而我們也不會把酸辣湯稱之為是飲料。
>
> 同理，雖然 SSR 字面上的意思是那樣，PHP 這種傳統 server 輸出內容的方案也可以稱之為 SSR，但你不會這樣叫它。SSR 更適合拿來指涉的是「用來解決 SPA 問題的 server 端解決方案」。

### SPA 与 CSR

[XMLHttpRequest](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest) 技术让开发者可以在客户端动态生成页面内容，在不重新加载整个页面的情况下更新显示内容。Gmail 在 2004 年展示了这种无刷新交互的强大威力——收发邮件、切换标签、搜索联系人，页面从未刷新过。

2005 年，Jesse James Garrett 将这种使用 XMLHttpRequest 的交互模式命名为 [AJAX](https://developer.mozilla.org/en-US/docs/Glossary/AJAX)，这个概念迅速普及。随后 jQuery 统治了 DOM 操作的世界，Backbone.js 为混乱的 JavaScript 代码带来结构，接着 Angular、React、Vue 登场，SPA (Single Page Application) 成为了 Web 开发的主流范式。

SPA 的核心理念简单粗暴：**服务端只提供数据，前端负责所有的渲染工作。用户首次访问时下载一个相对较大的 JavaScript bundle，然后享受近乎原生应用的交互体验。**

**这种模式有了一个专门的术语：CSR (Client-Side Rendering)，即客户端渲染。**

这确实解决了传统渲染方式的问题——每次点击都要等待页面刷新。但新的问题也随之而来：

- **空白的首屏**：JavaScript 执行之前，用户看到的只是一个空白页面或者简陋的 loading 动画。初版 NekoQuiz 就收到了这样的抱怨。
- **不利于 SEO**：搜索引擎爬虫看到的是一段“空白”的 HTML 和 JavaScript 链接而不是实际内容

**逻辑思维 [中等：成功]**：这听起来像是在用一个问题解决另一个问题。

是的，也许技术发展就是这样，每个解决方案都会带来新的问题，或者说根本没有 Solution 只有 Workaround。

??? NOTE "第一版 NekoQuiz 从 SPA + CSR 起步，那第一版 USTC 猫咪问答呢？"

    很可能是 PHP 的：[Hackergame2018 ustcquiz 源代码](https://github.com/ustclug/hackergame2018-writeups/blob/master/official/ustcquiz/src/ustcquiz/app/index.php)

### 现代 SSR 的回归——水合（Hydration）

CSR 带来的问题让开发者们开始怀念服务器渲染的好处：首屏内容立即可见、SEO 友好、JavaScript 失效时页面依然可见。

但谁也不想回到 PHP + jQuery 的石器时代，于是许多框架提出 SSR 的方案，试图结合二者的优点：**首次访问时服务器渲染完整的 HTML，后续交互则切换到客户端渲染模式**。

用户体验变成了这样：

1. **服务器端**：生成包含实际内容的 HTML
1. **浏览器**：立即显示服务器渲染的内容（用户可以看到页面了）
1. **JavaScript 加载完成**：页面“水合”，变为可交互的 SPA

这种方式有效地避开了 CSR 的问题。

**水合（Hydration）**，来自化学反应名称，非常形象的取名。也有人把它比喻成“三体人模型”：

- **喝水（Render）**：服务端执行完整的渲染逻辑，生成包含实际内容的 HTML。
- **脱水（Dehydration）**：将应用状态序列化并嵌入 HTML，移除交互逻辑，输出静态但完整的页面。
- **水合（Hydration）**：客户端 JavaScript 接管静态 HTML，恢复应用状态和交互能力。

代价很明显，“浸泡”（水合）阶段需要耗时，页面要过一段时间才可交互，TTI (Time To Interactive) 上升了。

### 同构（Isomorphic）

我不想纠结 [Isomorphic（同构）和 Universal（通用）的命名问题](https://medium.com/@ghengeveld/isomorphism-vs-universal-javascript-4b47fb481beb)，它们更多处在 JavaScript 语境下。

[Leptos](https://github.com/leptos-rs/leptos) 官方倾向使用 Isomorphic 一词，我认为没什么问题。Leptos 实现了 Universal 的效果——同一套 Rust 代码可以编译为服务器二进制和客户端 WASM，但最终的目标还是构建出 Isomorphic 应用。

使用 Leptos 可以同时做到这几点：**使用相同的语言，共享相同的类型，甚至在相同的文件中**。

**这是我为 NekoQuiz 重构的最大原因**，毕竟 CSR 的 SEO 和白屏问题对 CTF 题不值一提，我只是对在多个独立的地方维护代码感到烦躁了。

Leptos 通过条件编译和 Server Functions 实现同构：`#!rust #[server]` 宏标记的函数只在服务端编译和执行，但客户端可以像调用本地函数一样调用它们，Leptos 会自动生成相应的网络请求代码。

以简化版的 NekoQuiz 源码为例：

=== "客户端入口（`lib.rs`）"

    ```rust
    #[cfg(feature = "hydrate")]
    #[wasm_bindgen::prelude::wasm_bindgen]
    pub fn hydrate() {
        use crate::app::*;
        console_error_panic_hook::set_once();
        leptos::mount::hydrate_body(App);
    }
    ```

=== "服务端入口（`main.rs`）"

    ```rust
    #[cfg(feature = "ssr")]
    #[tokio::main]
    async fn main() {
        // ...
        let app = Router::new()
            .leptos_routes(&leptos_options, routes, || shell(leptos_options))
            .with_state(leptos_options);
        // ...
        axum::serve(listener, app).await?;
        // ...
    }


    #[cfg(not(feature = "ssr"))]
    pub fn main() {
        // no client-side main function
        // unless we want this to work with e.g., Trunk for pure client-side testing
        // see lib.rs for hydration function instead
    }
    ```

=== "Server Function"

    ```rust
    #[server(GetQuiz, prefix = "/api", endpoint = "quiz", input = GetUrl)]
    pub async fn get_quiz() -> Result<Quiz, ServerFnError> {
        let config = expect_context::<Arc<Config>>();

        Ok(Quiz {
            title: config.general.title.clone(),
            questions: config.questions.clone(),
        })
    }

    #[component]
    fn HomePage() -> impl IntoView {
        let quiz_resource = Resource::new(|| (), |_| async { get_quiz().await });
        // ...
    }
    ```

- 使用 `hydrate` 特性时，编译出 WASM 模块，包含水合逻辑和 server functions 的客户端存根。
- 使用 `ssr` 特性时，编译出服务端可执行程序，包含完整的渲染逻辑和 server functions 实现。

相比之前 Yew + Axum 的方案，消除了手动维护 API 接口和类型定义的重复工作，我也可以不用再写分步编译、打包的脚本了。

## 后话

**逻辑思维 [困难：失败]**：但……这意味着什么？历史视角并没有让你真正看清任何事物的发展，混乱的时代下你只是追随潮流。

**标新立异 [中等：成功]**：大家都热衷于潮流，你需要比一些人\*更潮流\*。

Web 技术在螺旋。

## 参考

- [從歷史的角度探討多種 SSR（Server-side rendering）](https://blog.huli.tw/2023/11/27/server-side-rendering-ssr-and-isomorphic/)
- [Isomorphism vs Universal JavaScript](https://medium.com/@ghengeveld/isomorphism-vs-universal-javascript-4b47fb481beb)
- [Universal JavaScript](https://medium.com/@mjackson/universal-javascript-4761051b7ae9)
- [Leptos Book](https://book.leptos.dev)
- [Yew Docs](https://yew.rs/docs/getting-started/introduction)
