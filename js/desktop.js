function openIndex() {
	location.href = "/";
}

// 滚动到顶部
$('.menu-top').click(function() {
	$('body, html').animate({
		scrollTop: 0
	}, 900);
});

// 滚动到底部
$('.menu-bottom').click(function() {
	$('body, html').animate({
		scrollTop: $(document).height() - $(window).height()
	}, 900);
});

$(window).scroll(function() {
	const scrollTop = $(window).scrollTop();
	const scrollBottom = $(document).height() - $(window).height() - scrollTop;

	// 显示/隐藏 .menu-top
	if (scrollTop > 500) {
		$('.menu-top').show();
	} else {
		$('.menu-top').hide();
	}

	// 显示/隐藏 .menu-bottom
	if (scrollBottom > 500) {
		$('.menu-bottom').show();
	} else {
		$('.menu-bottom').hide();
	}
});

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
