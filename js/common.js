function openIndex() {
	location.href = "/";
}

function updateReadingProgress() {
    // 获取页面的总高度和当前滚动位置
    const documentHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrollPosition = window.scrollY;

    // 计算阅读进度，百分比形式
    const progress = (scrollPosition / documentHeight) * 100;

    // 更新进度条的宽度
    document.getElementById('reading_progress').style.width = progress + '%';
}

// 监听滚动事件
window.addEventListener('scroll', updateReadingProgress);

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