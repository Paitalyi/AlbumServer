(function() {
	$(document).ready(function() {
		// 如果localStorage没有相应条目 则存储默认值
		function storeDefault(key, defaultValue) {
			if (localStorage.getItem(key) === null) {
				localStorage.setItem(key, defaultValue);
			}
		}
		storeDefault('thumbWidth', defaultThumbWidth);
		storeDefault('imgRadius', defaultImgRadius)
		storeDefault('refreshTimeout', defaultRefreshTimeout);
		storeDefault('lazyThreshold', defaultLazyThreshold);
		storeDefault('gridGutter', defaultGridGutter);

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
	});
})();