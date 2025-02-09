(function() {
	$(document).ready(function() {
		// 获取localStorage存储的值
		const savedLazyThreshold = localStorage.getItem('lazyThreshold');

		// 应用localStorage中存储的值
		const lazyThreshold = parseInt(savedLazyThreshold, 10);

		// 图片懒加载
		$("img.lazy").lazyload({
			effect: "fadeIn", // 图片加载时的效果
			threshold: lazyThreshold, // 提前加载距离
		});
	});
})();