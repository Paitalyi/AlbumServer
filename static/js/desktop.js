$(document).ready(function () {
    var timeout; //节流debouncing 避免 msnry.layout() 方法频繁触发
	var thumbWidth = $('.thumb').outerWidth();// 获取 .thumb 的宽度
	var refreshTimeout = 600//单位为ms

    // 初始化 LazyLoad
    $("img.lazy").lazyload({
        effect: "fadeIn",  // 图片加载时的效果
        threshold: 200,     // 提前加载距离
        load: function() {  // 每当图片加载完成后触发
            var grid = document.querySelector('.gallery');
            var msnry = Masonry.data(grid); // 获取已初始化的 Masonry 实例

            // 清除之前的延时调用
            clearTimeout(timeout);

            // 使用 setTimeout 来延迟执行 layout()，达到节流效果
            timeout = setTimeout(function() {
                msnry.layout(); // 延迟调用 layout() 更新 Masonry 布局
            }, refreshTimeout); // 延迟ms执行 layout()
        }
    });

    // 初始化 Masonry 布局
    var grid = document.querySelector('.gallery');
    var msnry = new Masonry(grid, {
        itemSelector: '.thumb',
        columnWidth: thumbWidth,
        gutter: 20,
		fitWidth: true,           // 启用自动调整宽度
		percentPosition: true     // 启用百分比定位，确保居中对齐
    });

});
