// 默认值 可配置
const defaultThumbWidth = 500;     // 图片宽度 单位px
const defaultImgRadius = 10;       // 图片圆角 单位px
const defaultRefreshTimeout = 600; // 节流实现中 定时器设置的时间长度 单位为ms
const defaultLazyThreshold = 100;  // 图片懒加载中 提前加载距离 单位px
const defaultGridGutter = 20;      // 图片瀑布流中 各列图片之间的间距 单位px
const defaultBrightness = 1.06;    // 图片亮度 0全黑 1无影响 大于1使得图片更明亮
const defaultContrast = 1;         // 图片对比度 0使得图片变灰 1无影响 大于1将增强对比度
const defaultSaturate = 1.08;      // 图片饱和度 0完全不饱和 1无影响 大于1则增加饱和度
const defaultHueRotate = -8;       // 对图片应用色相旋转 单位deg 0无影响
const defaultSepia = 0.15;         // 将图像转换为深褐色 0无影响 1则完全是深褐色的
