(function() {
	$(document).ready(function() {
		// 如果localStorage没有相应条目 则存储默认值
		if (localStorage.getItem('thumbWidth') === null) {
			localStorage.setItem('thumbWidth', defaultThumbWidth);
		}
		if (localStorage.getItem('imgRadius') === null) {
			localStorage.setItem('imgRadius', defaultImgRadius);
		}
		if (localStorage.getItem('refreshTimeout') === null) {
			localStorage.setItem('refreshTimeout', defaultRefreshTimeout);
		}
		if (localStorage.getItem('lazyThreshold') === null) {
			localStorage.setItem('lazyThreshold', defaultLazyThreshold);
		}
		if (localStorage.getItem('gridGutter') === null) {
			localStorage.setItem('gridGutter', defaultGridGutter);
		}

		// 获取localStorage存储的值
		const savedThumbWidth = localStorage.getItem('thumbWidth');
		const savedImgRadius = localStorage.getItem('imgRadius');
		const savedRefreshTimeout = localStorage.getItem('refreshTimeout');
		const savedLazyThreshold = localStorage.getItem('lazyThreshold');
		const savedGridGutter = localStorage.getItem('gridGutter');

		// 应用localStorage中存储的值
		const thumbWidth = parseInt(savedThumbWidth, 10);
		const imgRadius = parseInt(savedImgRadius, 10);
		const refreshTimeout = parseInt(savedRefreshTimeout, 10);
		const lazyThreshold = parseInt(savedLazyThreshold, 10);
		const gridGutter = parseInt(savedGridGutter, 10);

		// 设置CSS变量
		const root = document.documentElement;
		root.style.setProperty('--thumb-width', `${thumbWidth}px`);
		root.style.setProperty('--img-radius', `${imgRadius}px`);

		// 初始化 Masonry 布局
		let grid = document.querySelector('.gallery');
		let msnry = new Masonry(grid, {
			itemSelector: '.thumb',
			columnWidth: thumbWidth,
			gutter: gridGutter,
			fitWidth: true, // 启用自动调整宽度
			percentPosition: true // 启用百分比定位 确保居中对齐
		});

		let timeout; // 记录setTimeout返回的ID
		// 初始化 LazyLoad
		$("img.lazy").lazyload({
			effect: "fadeIn", // 图片加载时的效果
			threshold: lazyThreshold, // 提前加载距离
			load: function() { // 每当图片加载完成后触发
				var grid = document.querySelector('.gallery');
				var msnry = Masonry.data(grid); // 获取已初始化的 Masonry 实例
				// 使用setTimeout和clearTimeout实现节流debouncing
				// 清除之前的延时调用
				clearTimeout(timeout);
				// 使用 setTimeout 来延迟执行 layout()，达到节流效果
				timeout = setTimeout(function() {
					msnry.layout(); // 延迟调用 layout() 更新 Masonry 布局
				}, refreshTimeout); // 延迟ms执行 layout()
			}
		});

		// 检查页面是否有滚动条 如果没有 则直接显示全部图片
		// 防止因为图片无法进入视口 懒加载无法触发
		if ($(document).height() <= $(window).height()) {
			$("img.lazy").trigger("appear");
		}

		// 准备全屏图片查看器
		const body = document.body;
		const images = document.querySelectorAll('.lazy');
		const fullscreenViewer = document.getElementById('fullscreen-viewer');
		const leftOverlay = document.getElementById("left-overlay");
		const rightOverlay = document.getElementById("right-overlay");
		const fullscreenImage = document.getElementById('fullscreen-image');
		const prevButton = document.getElementById('fullscreen-prev-button');
		const nextButton = document.getElementById('fullscreen-next-button');
		const progressIndicator = document.getElementById('progress-indicator');
		const closeButton = document.getElementById('fullscreen-close-button');
		const totalImages = images.length;
		let currentIndex = 0;
		// 更新全屏图片
		function updateFullscreenImage() {
			fullscreenImage.src = images[currentIndex].src;
			fullscreenImage.alt = images[currentIndex].alt;
			progressIndicator.textContent = `${currentIndex + 1}/${totalImages}`; // 更新进度指示器
			console.log('View img ' + String(currentIndex + 1));
		}

		// 更新覆盖层的位置和宽度，使其覆盖图片的有效区域
		function updateOverlays() {
			const rect = fullscreenImage.getBoundingClientRect();
			leftOverlay.style.top = `${rect.top}px`;
			leftOverlay.style.left = `${rect.left}px`;
			leftOverlay.style.width = `${rect.width / 2}px`;
			leftOverlay.style.height = `${rect.height}px`;

			rightOverlay.style.top = `${rect.top}px`;
			rightOverlay.style.left = `${rect.left + rect.width / 2}px`;
			rightOverlay.style.width = `${rect.width / 2}px`;
			rightOverlay.style.height = `${rect.height}px`;
		}

		function closeFullscreenViewer() {
			fullscreenViewer.style.display = 'none';
			body.classList.remove('locked');
		}

		// 给所有图片添加点击事件
		images.forEach((item, index) => {
			item.addEventListener('click', function(event) {
				currentIndex = index;
				fullscreenImage.src = event.target.src;
				fullscreenImage.alt = event.target.alt;
				fullscreenViewer.style.display = 'flex';
				body.classList.add('locked');
				progressIndicator.textContent =
				`${currentIndex + 1}/${totalImages}`; // 更新进度指示器
				console.log('View img ' + String(currentIndex + 1));
			});
		});

		// 初始化时和窗口大小改变时更新覆盖层
		window.addEventListener("resize", updateOverlays);
		// 图片加载完成时更新覆盖层
		fullscreenImage.addEventListener("load", updateOverlays);

		// 前后切换按钮的点击事件
		prevButton.addEventListener('click', function() {
			currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
			updateFullscreenImage();
			prevButton.focus(); // 将焦点设置到prevButton上
		});
		nextButton.addEventListener('click', function() {
			currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
			updateFullscreenImage();
			nextButton.focus(); // 将焦点设置到nextButton上
		});

		// 左右覆盖层的点击事件
		leftOverlay.addEventListener("click", (event) => {
			prevButton.click(); // 模拟点击 Prev 按钮
		});
		rightOverlay.addEventListener("click", (event) => {
			nextButton.click(); // 模拟点击 Next 按钮
		});

		// 关闭按钮的点击事件
		closeButton.addEventListener('click', function() {
			closeFullscreenViewer();
		});

		// 全屏查看器的点击事件： 关闭
		fullscreenViewer.addEventListener('click', function(event) {
			if (event.target === fullscreenViewer) {
				closeFullscreenViewer();
			}
		});
	});
})();