---
date: 2024-05-12
categories:
  - Scientific Witchery
tags:
  - OS
  - Kernel
  - Rust
  - RISC-V
---

# Bad Apple!! on LemonCore

前段时间写了个操作系统，取名叫 LemonCore，惯例，播放一下 BadApple。

- OS：[github.com/13m0n4de/lemon-core](https://github.com/13m0n4de/lemon-core)
- App: [gist.github.com/13m0n4de/238b13f361e0326a0e8868e00119fb2a](https://gist.github.com/13m0n4de/238b13f361e0326a0e8868e00119fb2a)
- Video: [\[Touhou\] Bad Apple!! PV \[Shadow\]](https://www.nicovideo.jp/watch/sm8628149)

<!-- more -->

预览效果：

<video width="2516" height="1518" controls>
  <source src="/assets/images/blog/bad_apple_on_lemon_core/ba.webm" type="video/webm">
Your browser does not support the video tag.
</video>

## 视频取摸

直接解析视频需要实现一个解析视频文件格式的程序，有点太夸张，有点没必要。BadApple 只有黑白两色，可以分别用二进制位 `1` 和 `0` 存储。并且每帧的图像长宽都是一样的，直接将数据连续存放也没有问题（事先和解析程序商议好视频长宽的话）。

例如：

```
## ## ##            11011011
# ### ##            10111011
# ## # #    -->     10110101 
## #  ##            11010011
## # ###            11010111
```

其实也就相当于 LCD 显示屏的图片取摸过程，只是更加简单一些，不用考虑彩色情况，也不用多出个将视频帧切分为图片的步骤。

转换脚本：

```python title="converter.py"
import cv2
import numpy as np

cap = cv2.VideoCapture("bad_apple.mp4")
width = 480
height = 360

binary_flat = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray_frame, 128, 1, cv2.THRESH_BINARY)
    binary_flat.append(binary.flatten())

packed_bytes = np.packbits(binary_flat)
packed_bytes.tofile("bad_apple.bin")

cap.release()
```

可以得到 $480 \times 360 \times 6569 \div 8 = 141890400$ 字节的文件。

## 显示程序

用户程序库移植了 [embedded-graphics](https://crates.io/crates/embedded-graphics) crate，实现起来要简单不少。

先实现一个使用 `BinaryColor` 色彩的显示设备，显示像素时只需根据色彩状态 (`On` & `Off`) 将 FrameBuffer 对应数据写成 `0xffffff` 或 `0x000000`：

```rust title="bad_apple.rs"
impl Display {
    fn new(size: Size) -> Self {
        let fb_ptr = framebuffer() as *mut u8;
        let fb = unsafe { core::slice::from_raw_parts_mut(fb_ptr, VIRTGPU_LEN) };
        Self { size, fb }
    }

    fn draw_pixel(&mut self, x: i32, y: i32, color: BinaryColor) {
        let idx = (y * VIRTGPU_XRES as i32 + x) as usize * 4;
        if idx + 2 < self.fb.len() {
            let c = if color.is_on() { 0xff } else { 0x00 };
            self.fb[idx] = c;
            self.fb[idx + 1] = c;
            self.fb[idx + 2] = c;
        }
    }
}

impl DrawTarget for Display {
    type Color = BinaryColor;
    type Error = core::convert::Infallible;

    fn draw_iter<I>(&mut self, pixels: I) -> Result<(), Self::Error>
    where
        I: IntoIterator<Item = Pixel<Self::Color>>,
    {
        for Pixel(Point { x, y }, color) in pixels {
            self.draw_pixel(x, y, color);
        }
        framebuffer_flush();
        Ok(())
    }
}

impl OriginDimensions for Display {
    fn size(&self) -> Size {
        self.size
    }
}
```

显示时，不断从 `/data/bad_apple.bin` 中读取每一帧的数据，用其构建黑白图像 `ImageRaw::<BinaryColor>` 并显示在屏幕中心：

```rust title="bad_apple.rs"
#[no_mangle]
extern "Rust" fn main() -> i32 {
    let mut display = Display::new(Size::new(VIRTGPU_XRES, VIRTGPU_YRES));
    display.clear(BinaryColor::On).unwrap();

    let fd = open("/data/bad_apple.bin", OpenFlags::RDONLY);
    assert!(fd >= 0);
    let fd = fd as usize;

    let mut image_buffer = vec![0u8; IMAGE_BUFFER_SIZE];
    for _ in 0..FRAMES_COUNT {
        if read(fd, &mut image_buffer) == 0 {
            break;
        }
        let raw_image = ImageRaw::<BinaryColor>::new(&image_buffer, IMAGE_WIDTH as u32);
        let image = Image::new(
            &raw_image,
            Point {
                x: (VIRTGPU_XRES as i32 - IMAGE_WIDTH as i32) / 2,
                y: (VIRTGPU_YRES as i32 - IMAGE_HEIGHT as i32) / 2,
            },
        );
        image.draw(&mut display).unwrap();
    }
    close(fd);

    display.clear(BinaryColor::On).unwrap();

    0
}
```

嗯结束了。

答辩的时候还短暂地展示了一下，老师当然是一脸迷惑。
