(function() {
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

	$(document).ready(function() {
		// 绑定openIndex到.menu-index
		$('.menu-index').on('click', openIndex);

		const root = document.documentElement;

		// 如果localStorage没有相应条目 则存储默认值
		if (localStorage.getItem('brightness') === null) {
			localStorage.setItem('brightness', defaultBrightness);
		}
		if (localStorage.getItem('contrast') === null) {
			localStorage.setItem('contrast', defaultContrast);
		}
		if (localStorage.getItem('saturate') === null) {
			localStorage.setItem('saturate', defaultSaturate);
		}
		if (localStorage.getItem('hueRotate') === null) {
			localStorage.setItem('hueRotate', defaultHueRotate);
		}
		if (localStorage.getItem('sepia') === null) {
			localStorage.setItem('sepia', defaultSepia);
		}

		// 获取localStorage存储的值
		const brightness = localStorage.getItem('brightness');
		const contrast = localStorage.getItem('contrast');
		const saturate = localStorage.getItem('saturate');
		const hueRotate = localStorage.getItem('hueRotate');
		const sepia = localStorage.getItem('sepia');

		// 设置CSS变量
		root.style.setProperty('--brightness', brightness);
		root.style.setProperty('--contrast', contrast);
		root.style.setProperty('--saturate', saturate);
		root.style.setProperty('--hue-rotate', `${hueRotate}deg`);
		root.style.setProperty('--sepia', sepia);

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
	});
})();