$(function() {
	//懒加载
	$(document).ready(function() {
		$("img.lazy").lazyload({
			effect: "fadeIn"
		});
	});
});