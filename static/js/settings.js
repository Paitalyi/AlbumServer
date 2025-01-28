(function() {
	// 获取控件
	const saveButton = document.getElementById('save-button');
	const resetButton = document.getElementById('reset-button');

	const thumbWidthInput = document.getElementById('thumbWidth');
	const imgRadiusInput = document.getElementById('imgRadius');
	const refreshTimeoutInput = document.getElementById('refreshTimeout');
	const lazyThresholdInput = document.getElementById('lazyThreshold');
	const gridGutterInput = document.getElementById('gridGutter');
	const brightnessInput = document.getElementById('brightness');
	const contrastInput = document.getElementById('contrast');
	const saturateInput = document.getElementById('saturate');
	const hueRotateInput = document.getElementById('hueRotate');
	const sepiaInput = document.getElementById('sepia');

	// 先获取一次localStorage中存储的值 初始化saved*变量
	let savedThumbWidth = localStorage.getItem('thumbWidth');
	let savedImgRadius = localStorage.getItem('imgRadius');
	let savedRefreshTimeout = localStorage.getItem('refreshTimeout');
	let savedLazyThreshold = localStorage.getItem('lazyThreshold');
	let savedGridGutter = localStorage.getItem('gridGutter');
	let savedBrightness = localStorage.getItem('brightness');
	let savedContrast = localStorage.getItem('contrast');
	let savedSaturate = localStorage.getItem('saturate');
	let savedHueRotate = localStorage.getItem('hueRotate');
	let savedSepia = localStorage.getItem('sepia');

	// 在保存改动的设置后 需要重新获取saved*变量
	// 方便下一次保存更改时判断是否变更
	function getSavedItems() {
		savedThumbWidth = localStorage.getItem('thumbWidth');
		savedImgRadius = localStorage.getItem('imgRadius');
		savedRefreshTimeout = localStorage.getItem('refreshTimeout');
		savedLazyThreshold = localStorage.getItem('lazyThreshold');
		savedGridGutter = localStorage.getItem('gridGutter');
		savedBrightness = localStorage.getItem('brightness');
		savedContrast = localStorage.getItem('contrast');
		savedSaturate = localStorage.getItem('saturate');
		savedHueRotate = localStorage.getItem('hueRotate');
		savedSepia = localStorage.getItem('sepia');
	}
	
	// 初始化页面
	// 除了第一次运行外 需要先运行getSavedItems()
	function initPage() {
		if (savedThumbWidth) {
			thumbWidthInput.value = savedThumbWidth;
		}
		if (savedImgRadius) {
			imgRadiusInput.value = savedImgRadius;
		}
		if (savedRefreshTimeout) {
			refreshTimeoutInput.value = savedRefreshTimeout;
		}
		if (savedLazyThreshold) {
			lazyThresholdInput.value = savedLazyThreshold;
		}
		if (savedGridGutter) {
			gridGutterInput.value = savedGridGutter;
		}
		if (savedBrightness) {
			brightnessInput.value = savedBrightness;
		}
		if (savedContrast) {
			contrastInput.value = savedContrast;
		}
		if (savedSaturate) {
			saturateInput.value = savedSaturate;
		}
		if (savedHueRotate) {
			hueRotateInput.value = savedHueRotate;
		}
		if (savedSepia) {
			sepiaInput.value = savedSepia;
		}
	}

	// 初始化页面
	document.addEventListener('DOMContentLoaded', () => {
		initPage();
	});

	saveButton.addEventListener('click', () => {
		const thumbWidth = thumbWidthInput.value;
		const imgRadius = imgRadiusInput.value;
		const refreshTimeout = refreshTimeoutInput.value;
		const lazyThreshold = lazyThresholdInput.value;
		const gridGutter = gridGutterInput.value;
		const brightness = brightnessInput.value;
		const contrast = contrastInput.value;
		const saturate = saturateInput.value;
		const hueRotate = hueRotateInput.value;
		const sepia = sepiaInput.value;

		const defaultSuccessMsg = '下列设置已经保存:\n';
		const defaultFailMsg = '';
		let successMsg = defaultSuccessMsg;
		let failMsg = defaultFailMsg;

		if (thumbWidth && thumbWidth!==savedThumbWidth && thumbWidth >= 50) {
			localStorage.setItem('thumbWidth', thumbWidth);
			successMsg += '- 桌面端图片宽度\n';
		} else if(thumbWidth!==savedThumbWidth){ // 此处为true表示: if的条件结果为false 是因为其他条件中某些为false
			failMsg += '请输入有效的图片宽度值!(>=50)\n';
		}
		if (imgRadius && imgRadius!==savedImgRadius && imgRadius >= 0) {
			localStorage.setItem('imgRadius', imgRadius);
			successMsg += '- 桌面端图片圆角\n';
		} else if(imgRadius!==savedImgRadius){
			failMsg += '请输入有效的图片圆角值!(>=0)\n';
		}
		if (refreshTimeout && refreshTimeout!==savedRefreshTimeout && refreshTimeout >= 100) {
			localStorage.setItem('refreshTimeout', refreshTimeout);
			successMsg += '- 节流实现中,定时器设置的时间长度\n';
		} else if(refreshTimeout!==savedRefreshTimeout){
			failMsg += '请输入有效的节流定时器倒计时长度!(>=100)\n';
		}
		if (lazyThreshold && lazyThreshold!==savedLazyThreshold && lazyThreshold > 0) {
			localStorage.setItem('lazyThreshold', lazyThreshold);
			successMsg += '- 图片懒加载中的提前加载距离\n';
		} else if(lazyThreshold!==savedLazyThreshold){
			failMsg += '请输入有效的图片懒加载触发距离!(>0)\n';
		}
		if (gridGutter && gridGutter!==savedGridGutter && gridGutter >= 0) {
			localStorage.setItem('gridGutter', gridGutter);
			successMsg += '- 图片瀑布流中,各列图片之间的间距\n';
		} else if(gridGutter!==savedGridGutter){
			failMsg += '请输入有效的图片瀑布流列间距!(>=0)\n';
		}
		if (brightness && brightness!==savedBrightness && brightness >= 0) {
			localStorage.setItem('brightness', brightness);
			successMsg += '- 图片亮度\n';
		} else if(brightness!==savedBrightness){
			failMsg += '请输入有效的CSS滤镜亮度值!(>=0)\n';
		}
		if (contrast && contrast!==savedContrast && contrast >= 0) {
			localStorage.setItem('contrast', contrast);
			successMsg += '- 图片对比度\n';
		} else if(contrast!==savedContrast){
			failMsg += '请输入有效的CSS滤镜对比度值!(>=0)\n';
		}
		if (saturate && saturate!==savedSaturate && saturate >= 0) {
			localStorage.setItem('saturate', saturate);
			successMsg += '- 图片饱和度\n';
		} else if(saturate!==savedSaturate){
			failMsg += '请输入有效的CSS滤镜饱和度值!(>=0)\n';
		}
		if (hueRotate && hueRotate!==savedHueRotate && !isNaN(hueRotate)) { // !isNaN(hueRotate)为true表示hueRotate为字符串类型的数字
			localStorage.setItem('hueRotate', hueRotate);
			successMsg += '- 对图片应用色相旋转\n';
		} else if(hueRotate!==savedHueRotate){
			failMsg += '请输入有效的CSS滤镜色相旋转角度值!\n';
		}
		if (sepia && sepia!==savedSepia && sepia >= 0 && sepia <= 1) {
			localStorage.setItem('sepia', sepia);
			successMsg += '- 将图像转换为深褐色\n';
		} else if(sepia!==savedSepia){
			failMsg += '请输入有效的CSS滤镜深褐色值!(0<=sepia<=1)\n';
		}
		if (failMsg !== defaultFailMsg) {
			alert(failMsg);
		}
		if (successMsg !== defaultSuccessMsg) {// 有成功修改的设置项
			alert(successMsg);
			getSavedItems();
		}
	});

	resetButton.addEventListener('click', () => {
		localStorage.setItem('thumbWidth', defaultThumbWidth);
		localStorage.setItem('imgRadius', defaultImgRadius);
		localStorage.setItem('refreshTimeout', defaultRefreshTimeout);
		localStorage.setItem('lazyThreshold', defaultLazyThreshold);
		localStorage.setItem('gridGutter', defaultGridGutter);
		localStorage.setItem('brightness', defaultBrightness);
		localStorage.setItem('contrast', defaultContrast);
		localStorage.setItem('saturate', defaultSaturate);
		localStorage.setItem('hueRotate', defaultHueRotate);
		localStorage.setItem('sepia', defaultSepia);
		alert('成功重置所有设置项!');
		getSavedItems();
		initPage();
	});
})();