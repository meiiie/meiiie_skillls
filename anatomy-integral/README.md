# Tích phân trên máy đĩa–bánh xe

Thử [Anatomy](https://github.com/wheresryan22/anatomy): một hình isometric tương tác giải thích tích phân bằng một máy thật, không phải đồ thị.

Mở [`integral-light.html`](integral-light.html) hoặc [`integral.html`](integral.html). Kéo ngang, hoặc dùng ← → (Shift để nhảy lớn hơn), Home và End.

## Máy này tính gì

Một vòng tay quay là một vòng của đĩa, tức \(x\) đi từ \(0\) đến \(2\pi\).

Hàm số được cắt trên chốt Scotch lệch tâm 6:

\[
f(x) = 2 + \sin x
\]

Xe trượt nên bánh xe chạm đĩa tại bán kính

\[
\rho(x) = 6\,f(x) = 6(2 + \sin x)
\]

Bánh không trượt, bán kính \(4{,}8\). Góc bánh vì vậy là \(\frac{6}{4{,}8}\) lần tích phân. Hộp số ở đầu trục đưa kim về đúng tích phân, một vòng kim bằng 2 đơn vị:

\[
\int_0^x (2 + \sin t)\,dt = 2x + 1 - \cos x
\]

Hết một vòng, \(x = 2\pi\) và tích phân bằng \(4\pi\). Số ở góc phải đọc từ cùng công thức đang quay các chi tiết.

## Dựng lại

```bash
node anatomy-integral/build.mjs
node anatomy-integral/build.mjs --light
node anatomy-integral/build.mjs --audit
```

`--audit` kiểm tra va chạm và thứ tự vẽ. Thư viện vẽ trong `vendor/` là bản MIT của [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy), xem `vendor/LICENSE`.
