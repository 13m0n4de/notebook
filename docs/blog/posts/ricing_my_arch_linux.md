---
date: 2024-12-06
categories:
  - Random Ramblings
tags:
  - Dotfiles
  - Ricing
  - Linux
  - Hyprland
---

# Ricing My Arch Linux

花了点时间从 i3 迁移到 Hyprland，终于把凌乱的 Dotfiles 整理好了。

这次除了整理配置文件，还将整体配色方案从 Nord 切换到了 Catppuccin Macchiato，并且统一了包括网站在内的所有主题。

Dotfiles 仓库：[github.com/13m0n4de/dotfiles](https://github.com/13m0n4de/dotfiles)

<!-- more -->

## 预览

![clean](https://github.com/13m0n4de/dotfiles/blob/arch/.github/assets/clean.png?raw=true)
![tools](https://github.com/13m0n4de/dotfiles/blob/arch/.github/assets/tools.png?raw=true)
![windows](https://github.com/13m0n4de/dotfiles/blob/arch/.github/assets/windows.png?raw=true)
![development](https://github.com/13m0n4de/dotfiles/blob/arch/.github/assets/development.png?raw=true)

## 主题

从全套 Nord 配色更换到了 Catppuccin Macchiato 配色。

- **配色方案**：[Catppuccin](https://github.com/catppuccin/)
    - 风味：Macchiato
    - 强调色：Teal
- **图标主题**: [Papirus Dark](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme/)
- **光标主题**: [Catppuccin](https://github.com/catppuccin/cursors/)
- **终端字体**：[Hack Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/Hack)
- **系统字体**：[Source Han Sans CN](https://fonts.adobe.com/fonts/source-han-sans-simplified-chinese)
- **壁纸作者**：[shionnn_k](https://x.com/shionnn_k)

## 系统信息

- **发行版**：[Arch Linux](https://archlinux.org/)
- **显示管理器**：[ly](https://github.com/fairyglade/ly)
- **窗口管理器**：[Hyprland](https://hyprland.org/)
- **状态栏**：[Waybar](https://github.com/Alexays/Waybar/)
- **通知守护程序**：[Mako](https://github.com/emersion/mako)
- **锁屏程序**：[Hyprlock](https://github.com/hyprwm/hyprlock)
- **系统菜单**：[nwg-bar](https://github.com/nwg-piotr/nwg-bar)
- **输入法**：[Fcitx5](https://fcitx-im.org/) + [Rime](https://rime.im/) + [雾凇拼音](https://github.com/iDvel/rime-ice)
- **壁纸管理器**：[Hyprpaper](https://github.com/hyprwm/hyprpaper)
- **启动器**：[Rofi](https://github.com/davatorium/rofi)
- **终端**: [Alacritty](https://alacritty.org/) + [Zellij](https://github.com/zellij-org/zellij)
- **Shell**：[Fish](https://fishshell.com/) + [Starship](https://starship.rs/)
- **编辑器**：[Neovim](https://neovim.io/)（配置在[单独的仓库](https://github.com/13m0n4de/nvim)中）
- **文件管理器**：[Yazi](https://github.com/sxyazi/yazi/)
- **系统监视器**：[Btop](https://github.com/aristocratos/btop)
- **截图工具**：[grim](https://git.sr.ht/~emersion/grim) + [slurp](https://github.com/emersion/slurp) + [satty](https://github.com/gabm/satty)
- **录屏工具**：[OBS](https://obsproject.com/)
- **配置管理器**：[YADM](https://yadm.io/)

各类软件都是 **非常克制** 地选出来的，遵循以下几个原则：

- 轻量：尽量避免繁重的依赖项
- 简单：专注于单一功能，易于配置
- 快速：响应迅速，资源占用低
- 现代：采用新技术，没有历史包袱
- 活跃：项目持续更新，社区积极维护

## YADM

[YADM](https://github.com/yadm-dev/yadm) 是一个 Dotfiles 管理器，看仓库 Languages 概览会误以为它是 Python 项目，其实它是一个 Shell 脚本，Python 只用来编写测试用例。

YADM 本质上是对 Git 的封装，它在 `$HOME/.local/share/yadm/repo.git` 创建一个 Git 仓库，并将工作目录设置为 `$HOME`。它的使用方式也几乎与 Git 一模一样：

```
yadm init
yadm add <important file>
yadm commit
yadm remote add origin <url>
yadm push -u origin <local branch>:<remote branch>
yadm clone <url>
yadm status
```

YADM 和[裸仓库管理 Dotfiles](https://www.atlassian.com/git/tutorials/dotfiles) 的方式不同，虽然初始时使用 `--bare` 选项创建裸仓库，但随后立即修改配置 `core.bare` 为 `false`、`core.worktree` 为 `$HOME`。

如果直接用不带 `--bare` 的初始化方式，需要在 `$HOME/.local/share/yadm/repo.git` 初始化，并手动移动 `.git` 目录，重新配置工作目录这个过程会比较复杂且容易出错，所以才有先创建裸仓库再设置为普通仓库的操作。

我需要 [Bootstrap](https://yadm.io/docs/bootstrap) 等功能，所以没选用裸仓库手动管理，而是 YADM，但它也足够 Simple 了。

### 为什么没用其他管理器

- GNU Stow：有点古早，而且我不是很喜欢符号链接，无论是自己创建还是让工具帮我创建。并且从使用文档来看，感觉没有比我自己手动管理符号链接容易，许多操作宁愿写几个简单的 Shell 脚本来完成。
- Punktf：需要编写 YAML 配置文件，并且看上去开发者非常关注于跨平台，而我不在乎这个。
- toml-bombadil：需要编写 TOML 配置文件，感觉维护不够积极，并且官方示例的某个仓库从 toml-bombadil 迁移到了 chezmoi（宣传危机）
- Dotter：需要编写 TOML 配置文件，基本上是通过配置文件控制模板和符号链接来管理 dotfiles。还算是符合要求，但是作者的 dotfiles 仓库的组织风格我不太喜欢，导致第一印象不是很好。
- Dotdrop：需要编写 YAML 配置文件（半自动）。
- Dotbot：需要编写 YAML 配置 文件，使用符号链接。
- chezmoi：
    - [默认情况下创建常规文件和目录，而不是符号链接](https://www.chezmoi.io/user-guide/frequently-asked-questions/design/#why-doesnt-chezmoi-use-symlinks-like-gnu-stow)，对我来说是增加不必要的复杂度
    - [使用奇怪的文件名](https://www.chezmoi.io/user-guide/frequently-asked-questions/design/#why-does-chezmoi-use-weird-filenames)
    - dotfiles 需要在 chezmoi 的目录下修改再应用
    - 我需要额外学习一些命令，想要脱离 chezmoi 使用比较麻烦，虽然官方给出了一些命令可以[迁移到其他地方](https://www.chezmoi.io/user-guide/advanced/migrate-away-from-chezmoi/)

### YADM 的问题

遇到的最大问题可能就是，仓库 README 不是很方便放置。

因为默认的工作目录在 `$HOME`，常规情况下需要放置一个 `$HOME/README.md` 才能在 Github 仓库主页中显示。

解决方法也有，使用 `sparse-checkout` 可以做到“展示”和“使用”上的分离，详细见 [issues#93](https://github.com/yadm-dev/yadm/issues/93)

```
# 在 bootstrap 时切换到 $HOME 目录并执行：
yadm sparse-checkout set --no-cone '/*' '!README.md' '!UNLICENSE.md'
```

但单纯针对 Github 的话，可以在 `$HOME/.github/` 目录下放置 `README.md`，见 [Github Docs - About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)：

> If you put your README file in your repository's hidden .github, root, or docs directory, GitHub will recognize and automatically surface your README to repository visitors.
>
> If a repository contains more than one README file, then the file shown is chosen from locations in the following order: the .github directory, then the repository's root directory, and finally the docs directory.

## Guix System

其实这次与其说是迁移，更像是重装，我直接把盘给格式化了。

新发行版先是在 [NixOS](https://nixos.org/) 和 [Guix System](https://guix.gnu.org/) 里纠结，前者是这两年的时尚单品，但对比后者，感觉 Guix System 比 NixOS 更“精致”、文档也更清晰，并且 Scheme(Guile) 比 Nix 语言要好。

再加上以往有体验过 Guix 包管理器，于是就先装了 Guix System，花了两天时间在折腾 Guix 上。

结果是大失败，从安装到配置每一步都花了很大精力去看文档、试错，对着 TTY 敲 Scheme 也很痛苦。我逐渐意识到还要继续写非常非常多的配置才能达到基本可用，而我根本不是 Scheme 高手，于是灰溜溜就回到了 Arch。

现在正在使用虚拟机继续配置 Guix System，等配置好了就可以直接安装。（最快也会是明年了吧）

## 网站配色

你可能注意到，网站也全部替换为了 Catppuccin Macchiato 配色，这是让 AI 辅助写的 [Custom color schemes](https://github.com/13m0n4de/notebook/blob/main/docs/stylesheets/custom.css)。

不像以前在官方亮暗色主题下修修补补，这次配色覆盖的更加全面，代码高亮也更好看。
