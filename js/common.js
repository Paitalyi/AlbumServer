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