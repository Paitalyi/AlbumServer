(function () {
	$(document).ready(function () {
		const body = document.body;
		const images = document.querySelectorAll('.lazy');
		const fullscreenViewer = document.getElementById('fullscreen-viewer');
		const leftOverlay = document.getElementById("left-overlay");
		const rightOverlay = document.getElementById("right-overlay");
		const fullscreenImage = document.getElementById('fullscreen-image');
		const prevButton = document.getElementById('fullscreen-prev-button');
		const nextButton = document.getElementById('fullscreen-next-button');
		const progressIndicator = document.getElementById('progress-indicator');
		const slideshowButton = document.getElementById('fullscreen-slideshow-button');
		const closeButton = document.getElementById('fullscreen-close-button');
		const slideshowProgressIndicator = document.getElementById('slideshow-progress-indicator');
		const totalImages = images.length;
		let currentIndex = 0;
		let slideshowInterval = null;
		let slideshowIntervalTime = localStorage.getItem('slideshowIntervalTime');
		let slideshowProgress = 0;
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

		function startSlideshow() {
			let startTime = Date.now();
			slideshowProgress = 0;

			function animateProgress() {
				let elapsed = Date.now() - startTime;
				slideshowProgress = (elapsed % slideshowIntervalTime) / slideshowIntervalTime * 100;
				slideshowProgressIndicator.style.width = slideshowProgress + '%';
				progressAnimation = requestAnimationFrame(animateProgress);
			}

			animateProgress(); // 开始进度动画

			slideshowInterval = setInterval(() => {
				currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
				updateFullscreenImage();
				startTime = Date.now(); // 重新计算进度
			}, slideshowIntervalTime);
		}

		function closeFullscreenViewer() {
			fullscreenViewer.style.display = 'none';
			body.classList.remove('locked');
			if (slideshowButton.classList.contains('active')) {
				clearInterval(slideshowInterval);
				cancelAnimationFrame(progressAnimation);
				slideshowButton.classList.remove('active');
				slideshowButton.innerHTML = '▶';
				slideshowProgressIndicator.style.width = '0%';
			}
		}

		// 给所有图片添加点击事件
		images.forEach((item, index) => {
			item.addEventListener('click', function (event) {
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
		prevButton.addEventListener('click', function () {
			currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
			updateFullscreenImage();
			prevButton.focus(); // 将焦点设置到prevButton上
		});
		nextButton.addEventListener('click', function () {
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

		// 幻灯片按钮点击事件
		slideshowButton.addEventListener('click', function () {
			if (slideshowButton.classList.contains('active')) {
				clearInterval(slideshowInterval);
				cancelAnimationFrame(progressAnimation);
				slideshowButton.classList.remove('active');
				slideshowButton.innerHTML = '▶';
				slideshowProgressIndicator.style.width = '0%';
			} else {
				slideshowButton.classList.add('active');
				slideshowButton.innerHTML = '⏸';
				startSlideshow();
			}
		});

		// 关闭按钮的点击事件
		closeButton.addEventListener('click', function () {
			closeFullscreenViewer();
		});

		// 全屏查看器的点击事件： 关闭
		fullscreenViewer.addEventListener('click', function (event) {
			if (event.target === fullscreenViewer) {
				closeFullscreenViewer();
			}
		});
	});
})();