# Kiwoo 托管运行时资源

作品需要摄像头、MediaPipe、WASM、模型或下列常用浏览器库时读取本页。Kiwoo 作品允许在运行时
联网加载资源；部署接口只要求提交一个 HTML，不要求把大型模型转成 base64 塞进 HTML。

## 使用原则

- Kiwoo 生产运行时基址是 `https://preview.loot.alrite.fun`。在交付 HTML 中写完整绝对 URL，不要写
  `{{LOOT_RUNTIME_VENDOR_BASE_URL}}` 占位符，也不要猜相对 `/vendor/...` 路径。
- 下列固定版本资源由 Kiwoo 托管，优先于 jsDelivr、unpkg、cdnjs 或 Google 模型仓。沙箱允许摄像头
  和麦克风权限，并会按需缓存静态资源；首次加载仍然需要网络。
- 资源加载失败时显示真实、非阻塞的错误状态，并允许用户重试。鼠标/触摸可以是摄像头功能的备用
  交互，但摄像头与模型初始化成功时必须真正驱动主要功能。
- 如果用户明确要求完全离线运行，要说明这些托管资源首次加载需要网络，再让用户选择是否接受；
  不得直接删除摄像头、手势或其他核心能力。

## 摄像头手势

需要手势分类时优先使用 Tasks Vision 的 `GestureRecognizer`：

```html
<script type="module">
import { FilesetResolver, GestureRecognizer } from
  "https://preview.loot.alrite.fun/vendor/mediapipe-tasks/vision/1.0.1/vision_bundle.mjs";

const vision = await FilesetResolver.forVisionTasks(
  "https://preview.loot.alrite.fun/vendor/mediapipe-tasks/vision/1.0.1/wasm"
);
const recognizer = await GestureRecognizer.createFromOptions(vision, {
  baseOptions: {
    modelAssetPath:
      "https://preview.loot.alrite.fun/vendor/mediapipe-tasks/vision/1.0.1/models/gesture_recognizer.task"
  },
  runningMode: "VIDEO",
  numHands: 1
});
</script>
```

如果只需要手部 21 个关键点，可以把 `GestureRecognizer` 换成 `HandLandmarker`，模型使用：

```text
https://preview.loot.alrite.fun/vendor/mediapipe-tasks/vision/1.0.1/models/hand_landmarker.task
```

也可以使用 legacy MediaPipe Hands。入口与 `locateFile` 必须使用同一个固定基址：

```html
<script
  src="https://preview.loot.alrite.fun/vendor/mediapipe/hands/0.4.1675469240/hands.js"
  crossorigin="anonymous"></script>
<script>
const handsBase =
  "https://preview.loot.alrite.fun/vendor/mediapipe/hands/0.4.1675469240";
const hands = new Hands({ locateFile: file => `${handsBase}/${file}` });
</script>
```

不要在同一页混用两个 legacy MediaPipe 家族；需要手 + 脸、手 + 姿态等多种视觉能力时统一使用
Tasks Vision。获取摄像头使用 `navigator.mediaDevices.getUserMedia({ video: true })`，页面退出或重试
时停止旧 `MediaStreamTrack`。推理循环保持至多一个请求在途，避免堆积。

## 其他已托管入口

| 能力 | 入口 URL |
|---|---|
| Face Detection | `https://preview.loot.alrite.fun/vendor/mediapipe/face_detection/0.4.1646425229/face_detection.js` |
| Face Mesh | `https://preview.loot.alrite.fun/vendor/mediapipe/face_mesh/0.4.1633559619/face_mesh.js` |
| Pose | `https://preview.loot.alrite.fun/vendor/mediapipe/pose/0.5.1675469404/pose.js` |
| Selfie Segmentation | `https://preview.loot.alrite.fun/vendor/mediapipe/selfie_segmentation/0.1.1675465747/selfie_segmentation.js` |
| Three.js | `https://preview.loot.alrite.fun/vendor/npm/three/0.180.0/build/three.module.js` |
| p5.js | `https://preview.loot.alrite.fun/vendor/npm/p5/1.9.0/p5.min.js` |
| GSAP | `https://preview.loot.alrite.fun/vendor/npm/gsap/3.12.4/gsap.min.js` |
| Chart.js | `https://preview.loot.alrite.fun/vendor/npm/chart.js/4.4.1/chart.umd.js` |
| Anime.js | `https://preview.loot.alrite.fun/vendor/npm/animejs/3.2.2/anime.min.js` |

MediaPipe 的 loader、WASM 与模型必须来自同一家族基址。未列出的文件不要靠猜路径使用；如果现有
托管资源不能实现用户要求，先说明缺口并让用户选择方案。
