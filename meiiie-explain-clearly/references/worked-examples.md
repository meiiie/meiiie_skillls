# Original teaching examples

## Vietnamese: idempotency and a retry

Goal: distinguish repeating a request from repeating its effect.

“Idempotency” nghĩa là lặp lại cùng một thao tác vẫn cho kết quả cuối cùng như khi thực hiện một lần, trong phạm vi trạng thái đang xét.

Ví dụ: đặt trạng thái đèn thành “tắt” hai lần vẫn để đèn tắt. Lệnh “đảo trạng thái đèn” thì khác: chạy hai lần sẽ đưa đèn về trạng thái ban đầu.

Trong API thanh toán, khóa idempotency có thể giúp máy chủ nhận ra yêu cầu được gửi lại. Cơ chế này chỉ hiệu quả theo phạm vi, thời hạn lưu khóa và quy tắc của API. Nó không tự bảo đảm rằng mọi tác động bên ngoài chỉ xảy ra một lần.

Check: a timeout alone does not establish whether the server applied the first request. Explain why the API's documented retry rules matter.

Medium: text is enough for the distinction. Use a sequence diagram only if the learner needs to follow the timeout and response paths. Label request versus effect separately. Do not draw the missing response as a failed transaction.

## English: average speed

Goal: distinguish distance-weighted travel from an unweighted average of speeds.

A cyclist rides 10 km at 10 km/h, then 10 km at 20 km/h. The first part takes 1 hour. The second takes 0.5 hours. Average speed is total distance divided by total time: 20 / 1.5, or about 13.3 km/h. It is not 15 km/h. The cyclist spends more time at the lower speed.

Boundary: the arithmetic average of these speeds works for equal time intervals, not these equal distances. This example ignores stops; include stop time if the question defines the whole journey that way.

Medium: a small distance/time diagram can help. An interactive control is worthwhile only if the user wants to explore how changing time or distance changes the average. Do not generate a narrated film for this short question by default.

## Interaction contract: a learning artifact, not a simulation claim

For a requested toy queue explainer, label assumptions (one server, chosen arrival/service model, finite example). Let a learner adjust one variable and predict the effect before seeing it. Show units, elapsed time, waiting count, and a textual state description. Explain that the toy model does not predict production latency. Validate boundary conditions, reset, and repeatability when a seed is used. Render and inspect the output before calling it a working interactive artifact.
