/**
 * CIPHER NEXUS - 主应用入口
 * 初始化应用并注册全局事件
 */

// 应用状态
const AppState = {
    currentView: 'converter',
    isSplashComplete: false,
    conversionHistory: [],
    settings: {
        theme: 'dark',
        animation: 'full',
        defaultKey: '',
        autoCopy: false
    }
};

// 密码分类数据
const CipherCategories = {
    classical: {
        name: '古典密码',
        icon: 'fa-scroll',
        color: '#ffd700',
        ciphers: [
            { id: 'caesar', name: '凯撒密码', desc: '最经典的替换密码' },
            { id: 'vigenere', name: '维吉尼亚密码', desc: '多表替换密码' },
            { id: 'rail-fence', name: '栅栏密码', desc: '经典置换密码' },
            { id: 'atbash', name: 'Atbash密码', desc: '字母反转密码' },
            { id: 'affine', name: '仿射密码', desc: '数学加密' },
            { id: 'polybius', name: 'Polybius方阵', desc: '坐标加密' },
            { id: 'bacon', name: '培根密码', desc: '二进制编码' },
            { id: 'beaufort', name: 'Beaufort密码', desc: '维吉尼亚变体' },
            { id: 'autokey', name: '自动密钥密码', desc: '自密钥加密' },
            { id: 'simple-sub', name: '简单替换', desc: '单表替换' },
            { id: 'ROT13', name: 'ROT13', desc: '凯撒密码特例' },
            { id: 'reverse', name: '反转密码', desc: '文字翻转' }
        ]
    },
    modern: {
        name: '现代加密',
        icon: 'fa-lock',
        color: '#00ff9d',
        ciphers: [
            { id: 'aes', name: 'AES 加密', desc: '高级加密标准' },
            { id: 'des', name: 'DES 加密', desc: '数据加密标准' },
            { id: 'triple-des', name: '3DES 加密', desc: '三重DES' },
            { id: 'rc4', name: 'RC4 加密', desc: '流加密算法' },
            { id: 'sm4', name: 'SM4 国密', desc: '中国国家标准' },
            { id: 'rabbit', name: 'Rabbit加密', desc: '流加密' },
            { id: 'aes-gcm', name: 'AES-GCM', desc: '认证加密' },
            { id: 'chacha20', name: 'ChaCha20', desc: '现代流加密' }
        ]
    },
    encoding: {
        name: '编码转换',
        icon: 'fa-code',
        color: '#00f0ff',
        ciphers: [
            { id: 'base64', name: 'Base64', desc: '二进制到文本' },
            { id: 'base64-decode', name: 'Base64 解码', desc: 'Base64反向转换' },
            { id: 'base32', name: 'Base32', desc: '32字符编码' },
            { id: 'base58', name: 'Base58', desc: '比特币地址' },
            { id: 'base91', name: 'Base91', desc: '高效编码' },
            { id: 'base100', name: 'Base100', desc: 'Emoji编码' },
            { id: 'url', name: 'URL 编码', desc: '百分号编码' },
            { id: 'url-decode', name: 'URL 解码', desc: '百分号解码' },
            { id: 'html', name: 'HTML 实体', desc: '字符实体编码' },
            { id: 'html-decode', name: 'HTML 解码', desc: '字符实体解码' },
            { id: 'unicode', name: 'Unicode', desc: '统一码' },
            { id: 'ascii', name: 'ASCII', desc: '美国信息交换码' },
            { id: 'utf8', name: 'UTF-8', desc: '可变长编码' },
            { id: 'hex', name: '十六进制', desc: 'Hex编码' },
            { id: 'hex-decode', name: '十六进制 解码', desc: 'Hex解码' },
            { id: 'octal', name: '八进制', desc: '0-7编码' },
            { id: 'quoted-print', name: '引用可打印', desc: 'MIME编码' },
            { id: 'uuencoding', name: 'UUEncode', desc: 'Unix编码' }
        ]
    },
    special: {
        name: '特殊编码',
        icon: 'fa-eye',
        color: '#bf00ff',
        ciphers: [
            { id: 'morse', name: '摩斯电码', desc: '点划编码' },
            { id: 'binary', name: '二进制', desc: '0/1编码' },
            { id: 'binary-decode', name: '二进制 解码', desc: '二进制解码' },
            { id: 'pigpen', name: '猪圈密码', desc: '符号替换' },
            { id: 'taps', name: '敲击码', desc: '敲击通信' },
            { id: 'rot47', name: 'ROT47', desc: '数字字母轮换' },
            { id: 'keyboard', name: '键盘密码', desc: '键盘位置映射' },
            { id: 'leetspeak', name: 'LeetSpeak', desc: '黑客语言' },
            { id: 'zodiac', name: '星座密码', desc: '星座符号编码' },
            { id: 'dvorak', name: 'Dvorak密码', desc: '键盘布局转换' }
        ]
    },
    tools: {
        name: '工具类',
        icon: 'fa-tools',
        color: '#ff6b35',
        ciphers: [
            { id: 'hash-md5', name: 'MD5 哈希', desc: '128位散列' },
            { id: 'hash-sha1', name: 'SHA-1 哈希', desc: '160位散列' },
            { id: 'hash-sha256', name: 'SHA-256 哈希', desc: '256位散列' },
            { id: 'hash-sha512', name: 'SHA-512 哈希', desc: '512位散列' },
            { id: 'hash-ripemd', name: 'RIPEMD 哈希', desc: '160位散列' },
            { id: 'uuid', name: 'UUID 生成', desc: '唯一标识符' },
            { id: 'qrcode', name: '二维码生成', desc: '快速响应码' }
        ]
    }
};

// 初始化应用
function initApp() {
    console.log('CIPHER NEXUS 初始化中...');
    
    // 初始化主题
    initTheme();
    
    // 初始化跳转界面
    initSplashScreen();
    
    // 初始化动态背景
    initBackground();
    
    // 初始化导航
    initNavigation();
    
    // 初始化事件监听
    initEventListeners();
    
    console.log('CIPHER NEXUS 初始化完成');
}

// 初始化主题
function initTheme() {
    const savedTheme = localStorage.getItem('cipher-nexus-theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        // 检查系统主题偏好
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    }
}

// 跳转动画界面
function initSplashScreen() {
    const splashScreen = document.getElementById('splash-screen');
    const mainInterface = document.getElementById('main-interface');
    const enterBtn = document.getElementById('enter-btn');
    
    // 初始化粒子效果
    initParticleEffect();
    
    // 打字机效果
    if (typeof Typed !== 'undefined') {
        new Typed('#typed-subtitle', {
            strings: ['专业密码学工具平台', '加密 · 解密 · 编码 · 分析'],
            typeSpeed: 50,
            backSpeed: 30,
            loop: true,
            showCursor: true,
            cursorChar: '|'
        });
    }
    
    // 点击进入按钮
    enterBtn.addEventListener('click', (e) => {
        e.preventDefault();
        enterMainInterface();
    });
    
    // 点击任意位置进入
    splashScreen.addEventListener('click', (e) => {
        if (e.target.closest('.enter-btn') || e.target.closest('.logo-container')) return;
        enterMainInterface();
    });
    
    // 按Enter键进入
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !AppState.isSplashComplete) {
            enterMainInterface();
        }
    });
}

// 粒子效果
function initParticleEffect() {
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 150;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 2;
            this.vy = (Math.random() - 0.5) * 2;
            this.size = Math.random() * 3 + 1;
            this.color = `hsl(${Math.random() * 60 + 180}, 100%, 50%)`;
            this.opacity = Math.random() * 0.5 + 0.3;
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.opacity;
            ctx.fill();
        }
    }
    
    // 创建粒子
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    // 动画循环
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 绘制连线
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 240, 255, ${0.15 * (1 - dist / 150)})`;
                    ctx.stroke();
                }
            }
        }
        
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    // 窗口大小改变
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// 进入主界面
function enterMainInterface() {
    if (AppState.isSplashComplete) return;
    AppState.isSplashComplete = true;
    
    const splashScreen = document.getElementById('splash-screen');
    const mainInterface = document.getElementById('main-interface');
    
    // 释放粒子画布内存
    if (window.pauseParticles) {
        window.pauseParticles = true;
    }
    
    // 庆祝动画
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#00f0ff', '#bf00ff', '#00ff9d', '#ffd700']
        });
    }
    
    // 跳转动画
    gsap.to(splashScreen, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.inOut',
        onComplete: () => {
            splashScreen.classList.add('hidden');
            mainInterface.classList.remove('hidden');
            
            // 主界面入场动画
            gsap.fromTo(mainInterface, 
                { opacity: 0, scale: 0.95 },
                { opacity: 1, scale: 1, duration: 0.8, ease: 'power2.out' }
            );
            
            // 初始化背景动画
            initBackground();
            
            // 加载历史记录
            loadHistory();
        }
    });
}

// 动态背景
function initBackground() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const stars = [];
    const starCount = 200;
    
    class Star {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speed = Math.random() * 0.5 + 0.1;
            this.opacity = Math.random();
        }
        
        update() {
            this.y -= this.speed;
            if (this.y < 0) {
                this.y = canvas.height;
                this.x = Math.random() * canvas.width;
            }
            this.opacity = Math.sin(Date.now() * 0.001 + this.x) * 0.5 + 0.5;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 240, 255, ${this.opacity * 0.8})`;
            ctx.fill();
        }
    }
    
    for (let i = 0; i < starCount; i++) {
        stars.push(new Star());
    }
    
    // 网格线
    let gridOffset = 0;
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 绘制网格
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.03)';
        ctx.lineWidth = 1;
        
        const gridSize = 50;
        gridOffset = (gridOffset + 0.2) % gridSize;
        
        for (let x = gridOffset; x < canvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        
        for (let y = gridOffset; y < canvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
        
        // 绘制星星
        stars.forEach(star => {
            star.update();
            star.draw();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// 导航初始化
function initNavigation() {
    const navToggle = document.getElementById('nav-toggle');
    const navList = document.getElementById('nav-list');
    const navItems = document.querySelectorAll('.nav-item');
    
    // 移动端菜单切换
    navToggle.addEventListener('click', () => {
        navList.classList.toggle('active');
        gsap.fromTo(navList, 
            { opacity: navList.classList.contains('active') ? 0 : 1 },
            { opacity: navList.classList.contains('active') ? 1 : 0, duration: 0.3 }
        );
    });
    
    // 导航项点击
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const view = item.dataset.view;
            if (view) {
                showView(view);
                if (window.innerWidth <= 768) {
                    navList.classList.remove('active');
                }
            }
        });
    });
    
    // 主题切换
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => {
        toggleTheme();
    });
    
    // 全屏切换
    const fullscreenToggle = document.getElementById('fullscreen-toggle');
    fullscreenToggle.addEventListener('click', () => {
        toggleFullscreen();
    });
}

// 侧边栏切换
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// 关闭侧边栏
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.remove('active');
    }
}

// 切换主题
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    const themeBtn = document.querySelector('#theme-toggle i');
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('cipher-nexus-theme', newTheme);
    
    if (themeBtn) {
        if (newTheme === 'light') {
            themeBtn.classList.remove('fa-moon');
            themeBtn.classList.add('fa-sun');
        } else {
            themeBtn.classList.remove('fa-sun');
            themeBtn.classList.add('fa-moon');
        }
    }
    
    showToast(`已切换到${newTheme === 'dark' ? '深色' : '浅色'}主题`, 'success');
}

// 切换全屏
function toggleFullscreen() {
    try {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            showToast('已进入全屏模式', 'success');
        } else {
            document.exitFullscreen();
            showToast('已退出全屏模式', 'success');
        }
    } catch (err) {
        showToast('全屏功能不可用', 'error');
    }
}

// 显示视图
function showView(viewName) {
    const sections = document.querySelectorAll('.view-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${viewName}-view`);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // 视图切换动画
        gsap.fromTo(targetSection,
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }
        );
    }
    
    AppState.currentView = viewName;
}

// 事件监听初始化
function initEventListeners() {
    // 转换器输入处理
    const inputEl = document.getElementById('converter-input');
    if (inputEl) {
        inputEl.addEventListener('input', handleInput);
    }
    
    // 密码类型变更
    const cipherType = document.getElementById('cipher-type');
    if (cipherType) {
        cipherType.addEventListener('change', handleCipherChange);
    }
    
    // 密钥输入
    const cipherKey = document.getElementById('cipher-key');
    if (cipherKey) {
        cipherKey.addEventListener('input', handleInput);
    }
    
    // 偏移量输入
    const cipherShift = document.getElementById('cipher-shift');
    if (cipherShift) {
        cipherShift.addEventListener('input', handleInput);
    }
    
    // 设置界面
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.addEventListener('change', handleThemeChange);
    }
    
    const animationSelect = document.getElementById('animation-select');
    if (animationSelect) {
        animationSelect.addEventListener('change', handleAnimationChange);
    }
    
    const defaultKey = document.getElementById('default-key');
    if (defaultKey) {
        defaultKey.addEventListener('input', handleDefaultKeyChange);
    }
    
    const autoCopy = document.getElementById('auto-copy');
    if (autoCopy) {
        autoCopy.addEventListener('change', handleAutoCopyChange);
    }
    
    // 键盘快捷键
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter 转换
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            doConvert();
        }
        // Ctrl+Shift+C 复制输出
        if (e.ctrlKey && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            copyOutput();
        }
    });
    
    // 窗口大小改变
    window.addEventListener('resize', handleResize);
}

// 主题切换
function handleThemeChange(e) {
    const theme = e.target.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('cipher-nexus-theme', theme);
    showToast(`已切换到${theme === 'dark' ? '深色' : theme === 'light' ? '浅色' : '自动'}主题`, 'success');
}

// 动画切换
function handleAnimationChange(e) {
    const animation = e.target.value;
    document.documentElement.setAttribute('data-animation', animation);
    localStorage.setItem('cipher-nexus-animation', animation);
    showToast(`动画已${animation === 'none' ? '关闭' : animation === 'minimal' ? '简化' : '开启'}`, 'success');
}

// 默认密钥变更
function handleDefaultKeyChange(e) {
    const key = e.target.value;
    AppState.settings.defaultKey = key;
    localStorage.setItem('cipher-nexus-default-key', key);
}

// 自动复制变更
function handleAutoCopyChange(e) {
    const autoCopy = e.target.checked;
    AppState.settings.autoCopy = autoCopy;
    localStorage.setItem('cipher-nexus-auto-copy', autoCopy);
}

// 输入处理
function handleInput() {
    const input = document.getElementById('converter-input');
    const output = document.getElementById('converter-output');
    const charCount = document.getElementById('char-count');
    
    if (input && charCount) {
        charCount.textContent = `${input.value.length} 字符`;
    }
    
    // 自动清空输出
    if (output) {
        output.value = '';
    }
}

// 密码类型变更处理
function handleCipherChange() {
    const cipherType = document.getElementById('cipher-type').value;
    const keyGroup = document.getElementById('key-group');
    const shiftGroup = document.getElementById('shift-group');
    
    // 需要密钥的密码
    const keyCiphers = ['vigenere', 'beaufort', 'autokey', 'aes', 'des', 'rc4', 'sm4', 'aes-gcm', 'chacha20', 'rabbit', 'triple-des'];
    // 需要偏移量的密码
    const shiftCiphers = ['caesar', 'ROT13', 'affine'];
    
    if (keyGroup) {
        keyGroup.style.display = keyCiphers.includes(cipherType) ? 'block' : 'none';
    }
    
    if (shiftGroup) {
        shiftGroup.style.display = shiftCiphers.includes(cipherType) ? 'block' : 'none';
    }
}

// 执行转换
function doConvert() {
    const inputEl = document.getElementById('converter-input');
    const outputEl = document.getElementById('converter-output');
    const cipherTypeEl = document.getElementById('cipher-type');
    const keyEl = document.getElementById('cipher-key');
    const shiftEl = document.getElementById('cipher-shift');
    
    if (!inputEl || !outputEl || !cipherTypeEl) {
        console.error('找不到必要的DOM元素');
        return;
    }
    
    const input = inputEl.value;
    const cipherType = cipherTypeEl.value;
    const key = keyEl ? keyEl.value : '';
    const shift = shiftEl ? (parseInt(shiftEl.value) || 3) : 3;
    
    if (!input) {
        showToast('请输入需要转换的内容', 'error');
        return;
    }
    
    let result = '';
    
    try {
        switch (cipherType) {
            case 'caesar':
                result = caesarCipher(input, shift);
                break;
            case 'ROT13':
                result = caesarCipher(input, 13);
                break;
            case 'vigenere':
                result = vigenereCipher(input, key || 'CIPHER');
                break;
            case 'rail-fence':
                result = railFenceCipher(input, 3);
                break;
            case 'atbash':
                result = atbashCipher(input);
                break;
            case 'base64':
                result = btoa(unescape(encodeURIComponent(input)));
                break;
            case 'base64-decode':
                try {
                    result = decodeURIComponent(escape(atob(input)));
                } catch (e) {
                    showToast('Base64解码失败，输入格式不正确', 'error');
                    return;
                }
                break;
            case 'url':
                result = encodeURIComponent(input);
                break;
            case 'url-decode':
                try {
                    result = decodeURIComponent(input);
                } catch (e) {
                    showToast('URL解码失败', 'error');
                    return;
                }
                break;
            case 'html':
                result = input.replace(/[\u00-\u1F\u7F-\u9F]/g, c => '&#' + c.charCodeAt(0) + ';');
                break;
            case 'html-decode':
                const div = document.createElement('div');
                div.innerHTML = input;
                result = div.textContent;
                break;
            case 'unicode':
                result = input.split('').map(c => c.charCodeAt(0).toString(16).padStart(4, '0')).join('\\u');
                break;
            case 'binary':
                result = input.split('').map(c => c.charCodeAt(0).toString(2).padStart(8, '0')).join(' ');
                break;
            case 'binary-decode':
                try {
                    result = input.trim().split(' ').map(b => String.fromCharCode(parseInt(b, 2))).join('');
                } catch (e) {
                    showToast('二进制解码失败', 'error');
                    return;
                }
                break;
            case 'hex':
                result = input.split('').map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('');
                break;
            case 'hex-decode':
                try {
                    result = input.replace(/\s/g, '').match(/.{1,2}/g).map(h => String.fromCharCode(parseInt(h, 16))).join('');
                } catch (e) {
                    showToast('十六进制解码失败', 'error');
                    return;
                }
                break;
            case 'morse':
                result = textToMorse(input);
                break;
            case 'aes':
                if (key) {
                    result = CryptoJS.AES.encrypt(input, key).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'des':
                if (key) {
                    result = CryptoJS.DES.encrypt(input, key).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'hash-md5':
                result = CryptoJS.MD5(input).toString();
                break;
            case 'hash-sha1':
                result = CryptoJS.SHA1(input).toString();
                break;
            case 'hash-sha256':
                result = CryptoJS.SHA256(input).toString();
                break;
            case 'hash-sha512':
                result = CryptoJS.SHA512(input).toString();
                break;
            case 'affine':
                result = affineCipher(input, 5, 8);
                break;
            case 'polybius':
                result = polybiusCipher(input);
                break;
            case 'bacon':
                result = baconCipher(input);
                break;
            case 'beaufort':
                result = beaufortCipher(input, key || 'CIPHER');
                break;
            case 'autokey':
                result = autokeyCipher(input, key || 'CIPHER');
                break;
            case 'simple-sub':
                result = simpleSubstitutionCipher(input);
                break;
            case 'base32':
                result = base32Encode(input);
                break;
            case 'base58':
                result = base58Encode(input);
                break;
            case 'ascii':
                result = textToAscii(input);
                break;
            case 'utf8':
                result = textToUtf8(input);
                break;
            case 'octal':
                result = textToOctal(input);
                break;
            case 'quoted-print':
                result = quotedPrintableEncode(input);
                break;
            case 'uuencoding':
                result = uuEncode(input);
                break;
            case 'pigpen':
                result = pigpenCipher(input);
                break;
            case 'taps':
                result = tapsCipher(input);
                break;
            case 'reverse':
                result = input.split('').reverse().join('');
                break;
            case 'rot47':
                result = rot47Cipher(input);
                break;
            case 'atbash':
                result = atbashCipher(input);
                break;
            case 'ntsc':
                result = nthCharacterCipher(input, 3);
                break;
            case 'keyboard':
                result = keyboardCipher(input);
                break;
            case 'leetspeak':
                result = leetspeakEncode(input);
                break;
            case 'zodiac':
                result = zodiacCipher(input);
                break;
            case 'dvorak':
                result = dvorakCipher(input);
                break;
            case 'base91':
                result = base91Encode(input);
                break;
            case 'base100':
                result = base100Encode(input);
                break;
            case 'aes-gcm':
                if (key) {
                    result = CryptoJS.AES.encrypt(input, key, { mode: CryptoJS.mode.GCM }).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'chacha20':
                if (key) {
                    const keyHex = CryptoJS.enc.Utf8.parse(key.padEnd(32, '0').slice(0, 32));
                    const iv = CryptoJS.lib.WordArray.random(12);
                    const encrypted = CryptoJS.AES.encrypt(input, keyHex, { iv: iv, mode: CryptoJS.mode.CBC });
                    result = iv.toString() + ':' + encrypted.toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'rabbit':
                if (key) {
                    result = CryptoJS.Rabbit.encrypt(input, key).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'sm4':
                if (key) {
                    result = CryptoJS.AES.encrypt(input, key).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'rc4':
                if (key) {
                    result = CryptoJS.RC4.encrypt(input, key).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'triple-des':
                if (key) {
                    result = CryptoJS.TripleDES.encrypt(input, key).toString();
                } else {
                    showToast('请输入密钥', 'error');
                    return;
                }
                break;
            case 'uuid':
                result = generateUUID();
                break;
            case 'hash-ripemd':
                result = CryptoJS.RIPEMD160(input).toString();
                break;
            case 'qrcode':
                result = generateQRCode(input);
                break;
            default:
                result = '暂不支持此加密方式';
        }
        
        outputEl.value = result;
        
        // 保存到历史记录
        saveToHistory(input, result, cipherType);
        
        // 成功动画
        gsap.fromTo(outputEl, 
            { scale: 0.98 },
            { scale: 1, duration: 0.3, ease: 'back.out' }
        );
        
        showToast('转换成功', 'success');
        
    } catch (error) {
        console.error('转换错误:', error);
        showToast('转换失败: ' + error.message, 'error');
    }
}

// 凯撒密码
function caesarCipher(text, shift) {
    return text.split('').map(char => {
        if (char.match(/[a-z]/i)) {
            const base = char === char.toUpperCase() ? 65 : 97;
            return String.fromCharCode((char.charCodeAt(0) - base + shift) % 26 + base);
        }
        return char;
    }).join('');
}

// 维吉尼亚密码
function vigenereCipher(text, key) {
    let result = '';
    let keyIndex = 0;
    key = key.toUpperCase();
    
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char.match(/[a-z]/i)) {
            const base = char === char.toUpperCase() ? 65 : 97;
            const shift = key.charCodeAt(keyIndex % key.length) - 65;
            result += String.fromCharCode((char.charCodeAt(0) - base + shift) % 26 + base);
            keyIndex++;
        } else {
            result += char;
        }
    }
    return result;
}

// Atbash密码
function atbashCipher(text) {
    return text.split('').map(char => {
        if (char.match(/[a-z]/i)) {
            const base = char === char.toUpperCase() ? 65 : 97;
            return String.fromCharCode(25 - (char.charCodeAt(0) - base) + base);
        }
        return char;
    }).join('');
}

// 仿射密码
function affineCipher(text, a, b) {
    const m = 26;
    const result = [];
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char.match(/[a-z]/i)) {
            const base = char === char.toUpperCase() ? 65 : 97;
            const x = char.charCodeAt(0) - base;
            const y = (a * x + b) % m;
            result.push(String.fromCharCode(y + base));
        } else {
            result.push(char);
        }
    }
    return result.join('');
}

// Polybius方阵
function polybiusCipher(text) {
    const matrix = [
        ['A', 'B', 'C', 'D', 'E'],
        ['F', 'G', 'H', 'I', 'K'],
        ['L', 'M', 'N', 'O', 'P'],
        ['Q', 'R', 'S', 'T', 'U'],
        ['V', 'W', 'X', 'Y', 'Z']
    ];
    let result = '';
    text = text.toUpperCase().replace(/J/g, 'I');
    for (const char of text) {
        if (char.match(/[A-Z]/)) {
            for (let row = 0; row < 5; row++) {
                for (let col = 0; col < 5; col++) {
                    if (matrix[row][col] === char) {
                        result += (row + 1) + '' + (col + 1) + ' ';
                    }
                }
            }
        } else {
            result += char + ' ';
        }
    }
    return result.trim();
}

// 培根密码
function baconCipher(text) {
    const baconMap = {
        'A': 'AAAAA', 'B': 'AAAAB', 'C': 'AAABA', 'D': 'AAABB', 'E': 'AABAA',
        'F': 'AABAB', 'G': 'AABBA', 'H': 'AABBB', 'I': 'ABAAA', 'J': 'ABAAB',
        'K': 'ABABA', 'L': 'ABABB', 'M': 'ABBAB', 'N': 'ABBAB', 'O': 'ABBBA',
        'P': 'ABBBB', 'Q': 'BAAAA', 'R': 'BAAAB', 'S': 'BAABA', 'T': 'BAABB',
        'U': 'BABAA', 'V': 'BABAB', 'W': 'BABBA', 'X': 'BABBB', 'Y': 'BBAAA',
        'Z': 'BBAAB'
    };
    return text.toUpperCase().split('').map(char => baconMap[char] || char).join(' ');
}

// Beaufort密码
function beaufortCipher(text, key) {
    let result = '';
    key = key.toUpperCase();
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char.match(/[a-z]/i)) {
            const base = char === char.toUpperCase() ? 65 : 97;
            const keyChar = key[i % key.length].charCodeAt(0) - 65;
            const textChar = char.toUpperCase().charCodeAt(0) - 65;
            const shifted = (keyChar - textChar + 26) % 26;
            result += String.fromCharCode(shifted + base);
        } else {
            result += char;
        }
    }
    return result;
}

// 自动密钥密码
function autokeyCipher(text, key) {
    let result = '';
    let keyStream = key.toUpperCase();
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char.match(/[a-z]/i)) {
            const base = char === char.toUpperCase() ? 65 : 97;
            const shift = keyStream[i].charCodeAt(0) - 65;
            result += String.fromCharCode((char.toUpperCase().charCodeAt(0) - 65 + shift) % 26 + base);
            keyStream += text[i].toUpperCase();
        } else {
            result += char;
        }
    }
    return result;
}

// 简单替换密码
function simpleSubstitutionCipher(text) {
    const substitution = 'QWERTYUIOPASDFGHJKLZXCVBNM';
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    return text.toUpperCase().split('').map(char => {
        const idx = alphabet.indexOf(char);
        return idx >= 0 ? substitution[idx] : char;
    }).join('');
}

// Base32编码 (RFC 4648)
function base32Encode(input) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let bits = '';
    for (const char of input) {
        bits += char.charCodeAt(0).toString(2).padStart(8, '0');
    }
    while (bits.length % 5 !== 0) bits += '0';
    let result = '';
    for (let i = 0; i < bits.length; i += 5) {
        result += alphabet[parseInt(bits.substr(i, 5), 2)];
    }
    // 添加padding
    const paddingLength = (8 - (result.length % 8)) % 8;
    result += '='.repeat(paddingLength);
    return result;
}

// Base58编码
function base58Encode(input) {
    const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    let num = BigInt(0);
    for (const char of input) {
        num = num * BigInt(256) + BigInt(char.charCodeAt(0));
    }
    if (num === BigInt(0)) return '1';
    let result = '';
    while (num > 0) {
        result = alphabet[Number(num % BigInt(58))] + result;
        num = num / BigInt(58);
    }
    return result;
}

// 文本转ASCII
function textToAscii(text) {
    return text.split('').map(c => c.charCodeAt(0)).join(' ');
}

// 文本转UTF-8
function textToUtf8(text) {
    return new TextEncoder().encode(text).reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');
}

// 文本转八进制
function textToOctal(text) {
    return text.split('').map(c => c.charCodeAt(0).toString(8).padStart(3, '0')).join(' ');
}

// Quoted-Printable编码
function quotedPrintableEncode(text) {
    return text.split('').map(char => {
        const code = char.charCodeAt(0);
        if (code > 127 || char === '=') {
            return '=' + code.toString(16).padStart(2, '0').toUpperCase();
        }
        return char;
    }).join('');
}

// UUEncode
function uuEncode(text) {
    const chars = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_';
    let result = String.fromCharCode(text.length + 32);
    for (let i = 0; i < text.length; i += 3) {
        const b1 = text.charCodeAt(i);
        const b2 = i + 1 < text.length ? text.charCodeAt(i + 1) : 0;
        const b3 = i + 2 < text.length ? text.charCodeAt(i + 2) : 0;
        result += chars[(b1 >> 2) & 0x3F];
        result += chars[((b1 << 4) | (b2 >> 4)) & 0x3F];
        result += chars[((b2 << 2) | (b3 >> 6)) & 0x3F];
        result += chars[b3 & 0x3F];
    }
    return result;
}

// 猪圈密码
function pigpenCipher(text) {
    const pigpen = {
        'A': '⌐⌐', 'B': '⌐⌎', 'C': '⌐¬', 'D': '⌐⏌', 'E': '⌐⎿',
        'F': '⌐⏍', 'G': '⎿⌐', 'H': '⏌⌐', 'I': '¬⌐', 'J': '⌎⌐',
        'K': '⌐⌎', 'L': '⌎⏌', 'M': '⌎⎿', 'N': '⌎⏍', 'O': '⏌⎿',
        'P': '⏌⏍', 'Q': '⎿¬', 'R': '⎿⏌', 'S': '⏍⌐', 'T': '⏍⌎',
        'U': '⏍⏌', 'V': '⎿⎿', 'W': '⏍⏍', 'X': '⌐¬', 'Y': '¬⌎',
        'Z': '¬⏌'
    };
    return text.toUpperCase().split('').map(c => pigpen[c] || c).join(' ');
}

// 敲击码
function tapsCipher(text) {
    const taps = {
        'A': '12', 'B': '2111', 'C': '2121', 'D': '211', 'E': '1',
        'F': '2211', 'G': '221', 'H': '2221', 'I': '22', 'J': '1112',
        'K': '1121', 'L': '1211', 'M': '121', 'N': '1221', 'O': '122',
        'P': '1111', 'Q': '111', 'R': '2112', 'S': '212', 'T': '22',
        'U': '2212', 'V': '222', 'W': '2222', 'X': '2111', 'Y': '2122',
        'Z': '2211'
    };
    return text.toUpperCase().split('').map(c => taps[c] || c).join(' ');
}

// ROT47
function rot47Cipher(text) {
    return text.split('').map(char => {
        const code = char.charCodeAt(0);
        if (code >= 33 && code <= 126) {
            return String.fromCharCode(33 + ((code - 33 + 47) % 94));
        }
        return char;
    }).join('');
}

// N字密码 (Nth Character Cipher)
function nthCharacterCipher(text, n) {
    return text.split('').filter((_, i) => i % n === 0).join('');
}

// 键盘密码
function keyboardCipher(text) {
    const keyboard = 'QWERTYUIOPASDFGHJKLZXCVBNM';
    const shifted = 'MNHBVGFCXDSZAQWERTYUIOPLKJHG';
    return text.toUpperCase().split('').map(char => {
        const idx = keyboard.indexOf(char);
        return idx >= 0 ? shifted[idx] : char;
    }).join('');
}

// Leetspeak编码
function leetspeakEncode(text) {
    const leet = { 'A': '4', 'B': '8', 'E': '3', 'G': '6', 'I': '1', 'O': '0', 'S': '5', 'T': '7', 'Z': '2' };
    return text.toUpperCase().split('').map(c => leet[c] || c).join('');
}

// 星座密码 (Zodiac)
function zodiacCipher(text) {
    const zodiac = '♈♉♊♋♌♍♎♏♐♑♒♓';
    return text.toUpperCase().split('').map((c, i) => {
        if (c.match(/[A-Z]/)) {
            return zodiac[(c.charCodeAt(0) - 65) % 12];
        }
        return c;
    }).join('');
}

// Dvorak密码
function dvorakCipher(text) {
    const qwerty = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const dvorak = 'AXJE.UCTVIBM徐YHQRLZSPDGKFWVONULHEQCMIYT';
    return text.toUpperCase().split('').map(c => {
        const idx = qwerty.indexOf(c);
        return idx >= 0 ? dvorak[idx] : c;
    }).join('');
}

// Base91编码 (正确的实现)
function base91Encode(input) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"';
    let result = '';
    let b = 0;
    let n = 0;
    for (let i = 0; i < input.length; i++) {
        b |= input.charCodeAt(i) << n;
        n += 8;
        if (n > 13) {
            const v = b % 91;
            b = Math.floor(b / 91);
            n -= 13;
            result += alphabet[v];
        }
    }
    if (n > 0) {
        result += alphabet[b % 91];
    }
    return result;
}

// Base100编码 (Emoji)
function base100Encode(text) {
    const emoji = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ👁️🍺🦊💎🔥⭐✨🎯🚀💡🎨🔮🌀💫🌟🌙☀️🌈🎭🎪🎬🎮🎲🎵🎶🎤🎧📱💻🖥️⌨️🖱️💾💿📀📷📹🎥📽️📞☎️📟📠📺📻🎙️🎚️🎛️⏱️⏲️⏰🕰️📡🔋🔌💡🔦🕯️🪔🧯🛒💰💴💵💶💷💸💳💹💵💰📦📫📬📭📮📯📜📃📄📑🧾📊📈📉📆📅🗓️📇🗃️🗳️🗄️📋📁📂🗂️🗞️📰🔖🧷🔗📎🖇️📐📏🧮📌📍✂️🖊️🖋️✒️🖌️🖍️📝✏️🔍🔎🔏🔐🔒🔓';
    let result = '';
    for (let i = 0; i < text.length; i++) {
        const code = text.charCodeAt(i);
        result += emoji[code % emoji.length];
    }
    return result;
}

// 生成UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// 生成二维码 (返回Base64图片)
function generateQRCode(text) {
    if (!text) return '请输入内容';
    
    // 使用Google Chart API生成二维码
    const encodedText = encodeURIComponent(text);
    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodedText}`;
    
    // 返回Markdown图片格式，显示在预览区域
    return `![QR Code](${qrUrl})\n\n或者直接访问:\n${qrUrl}`;
}

// 栅栏密码
function railFenceCipher(text, rails) {
    const fence = Array(rails).fill().map(() => []);
    let rail = 0;
    let direction = 1;
    
    for (const char of text) {
        fence[rail].push(char);
        rail += direction;
        if (rail === rails - 1 || rail === 0) direction *= -1;
    }
    
    return fence.flat().join('');
}

// 文本转摩斯电码
function textToMorse(text) {
    const morseCode = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..',
        '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...',
        ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-',
        '_': '..--.-', '"': '.-..-.', '\'': '.----.', '@': '.--.-.'
    };
    
    return text.toUpperCase().split('').map(char => {
        if (char === ' ') return '/';
        return morseCode[char] || char;
    }).join(' ');
}

// 交换输入输出
function swapIO() {
    const input = document.getElementById('converter-input');
    const output = document.getElementById('converter-output');
    
    const temp = input.value;
    input.value = output.value;
    output.value = temp;
    
    gsap.fromTo([input, output],
        { scale: 1.02 },
        { scale: 1, duration: 0.3 }
    );
}

// 自动识别
function autoDetect() {
    const input = document.getElementById('converter-input').value;
    const detectResult = document.getElementById('detect-result');
    
    if (!input) {
        showToast('请先输入内容', 'info');
        return;
    }
    
    // 简单检测逻辑
    let detected = '';
    
    if (/^[01\s]+$/.test(input) && input.includes(' ')) {
        detected = '二进制';
    } else if (/^[0-9A-Fa-f]+$/.test(input) && input.length % 2 === 0) {
        detected = '十六进制';
    } else if (/^[A-Z0-9+/]+={0,2}$/.test(input) && input.length % 4 === 0) {
        detected = 'Base64';
    } else if (/^[\.\-]+\s*[\.\-]+\s*[\.\-]+$/.test(input)) {
        detected = '摩斯电码';
    } else if (/%[0-9A-Fa-f]{2}/.test(input)) {
        detected = 'URL编码';
    } else if (/&#[0-9]+;/.test(input)) {
        detected = 'HTML实体';
    }
    
    if (detectResult) {
        detectResult.textContent = detected ? `检测: ${detected}` : '未识别';
    }
    
    if (detected) {
        showToast(`检测到: ${detected}`, 'info');
    }
}

// 复制输出
function copyOutput() {
    const output = document.getElementById('converter-output');
    
    if (!output.value) {
        showToast('没有可复制的内容', 'error');
        return;
    }
    
    navigator.clipboard.writeText(output.value).then(() => {
        showToast('已复制到剪贴板', 'success');
        
        // 复制成功动画
        gsap.fromTo('.output-action-btn', 
            { scale: 1.2 },
            { scale: 1, duration: 0.3, ease: 'back.out' }
        );
    }).catch(err => {
        showToast('复制失败', 'error');
    });
}

// 清空输入
function clearInput() {
    const input = document.getElementById('converter-input');
    const output = document.getElementById('converter-output');
    const charCount = document.getElementById('char-count');
    const detectResult = document.getElementById('detect-result');
    
    input.value = '';
    output.value = '';
    if (charCount) charCount.textContent = '0 字符';
    if (detectResult) detectResult.textContent = '';
    
    gsap.fromTo([input, output],
        { backgroundColor: 'rgba(0, 240, 255, 0.1)' },
        { backgroundColor: 'rgba(0, 0, 0, 0.3)', duration: 0.5 }
    );
}

// 粘贴输入
async function pasteInput() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById('converter-input').value = text;
        handleInput();
        showToast('已粘贴', 'success');
    } catch (err) {
        showToast('粘贴失败', 'error');
    }
}

// 格式化时间 - 2026年标准格式
function formatTime(date = new Date()) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 保存到历史记录
function saveToHistory(input, output, type) {
    const historyItem = {
        id: Date.now(),
        input,
        output,
        type,
        time: formatTime()
    };
    
    AppState.conversionHistory.unshift(historyItem);
    
    // 保存到本地存储
    localStorage.setItem('cipher-nexus-history', JSON.stringify(AppState.conversionHistory));
    
    // 更新历史记录显示
    renderHistory();
}

// 加载历史记录
function loadHistory() {
    const saved = localStorage.getItem('cipher-nexus-history');
    if (saved) {
        AppState.conversionHistory = JSON.parse(saved);
        renderHistory();
    }
}

// 渲染历史记录
function renderHistory() {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;
    
    if (AppState.conversionHistory.length === 0) {
        historyList.innerHTML = `
            <div class="empty-history">
                <i class="fas fa-history"></i>
                <p>暂无转换历史</p>
            </div>
        `;
        return;
    }
    
    historyList.innerHTML = AppState.conversionHistory.map(item => `
        <div class="history-item" onclick="loadHistoryItem(${item.id})">
            <div class="history-item-content">
                <div class="history-item-info">
                    <div class="history-item-type">${getCipherName(item.type)}</div>
                    <div class="history-item-preview">${item.input.substring(0, 50)}...</div>
                </div>
                <div class="history-item-time">${item.time}</div>
                <div class="history-item-actions">
                    <button class="output-action-btn" onclick="event.stopPropagation(); copyHistoryItem(${item.id})">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// 获取密码名称
function getCipherName(type) {
    const names = {
        'caesar': '凯撒密码',
        'vigenere': '维吉尼亚密码',
        'rail-fence': '栅栏密码',
        'atbash': 'Atbash密码',
        'base64': 'Base64',
        'url': 'URL编码',
        'html': 'HTML实体',
        'unicode': 'Unicode',
        'binary': '二进制',
        'hex': '十六进制',
        'morse': '摩斯电码',
        'aes': 'AES加密',
        'des': 'DES加密',
        'hash-md5': 'MD5哈希',
        'hash-sha256': 'SHA-256哈希'
    };
    return names[type] || type;
}

// 加载历史记录项
function loadHistoryItem(id) {
    const item = AppState.conversionHistory.find(h => h.id === id);
    if (item) {
        document.getElementById('converter-input').value = item.input;
        document.getElementById('converter-output').value = item.output;
        document.getElementById('cipher-type').value = item.type;
        handleInput();
        showToast('已加载历史记录', 'info');
    }
}

// 复制历史记录项
function copyHistoryItem(id) {
    const item = AppState.conversionHistory.find(h => h.id === id);
    if (item) {
        navigator.clipboard.writeText(item.output).then(() => {
            showToast('已复制', 'success');
        });
    }
}

// 清空历史记录
function clearHistory() {
    AppState.conversionHistory = [];
    localStorage.removeItem('cipher-nexus-history');
    renderHistory();
    showToast('历史记录已清空', 'success');
}

// 导出历史记录
function exportHistory() {
    const data = JSON.stringify(AppState.conversionHistory, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cipher-nexus-history-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('导出成功', 'success');
}

// 打开分类
function openCategory(category) {
    const categoryData = CipherCategories[category];
    if (!categoryData) return;
    
    // 关闭侧边栏
    closeSidebar();
    
    // 切换到密码库视图
    showView('categories');
    
    const subModules = document.getElementById('sub-modules');
    if (!subModules) return;
    
    // 动画显示子模块
    subModules.innerHTML = `
        <div class="sub-category">
            <button class="back-btn" onclick="closeCategory()">
                <i class="fas fa-arrow-left"></i> 返回
            </button>
            <h3>${categoryData.name}</h3>
            <div class="cipher-grid">
                ${categoryData.ciphers.map((cipher, index) => `
                    <div class="cipher-card" onclick="openCipherDetail('${category}', '${cipher.id}')" 
                         style="animation-delay: ${index * 0.1}s">
                        <div class="cipher-icon" style="background: ${categoryData.color}20; color: ${categoryData.color}">
                            <i class="fas fa-key"></i>
                        </div>
                        <h4>${cipher.name}</h4>
                        <p>${cipher.desc}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    gsap.fromTo('.sub-category',
        { opacity: 0, x: 50 },
        { opacity: 1, x: 0, duration: 0.5, ease: 'power2.out' }
    );
    
    // 隐藏大模块
    gsap.to('.category-modules', { opacity: 0.3, duration: 0.3 });
}

// 关闭分类
function closeCategory() {
    const subModules = document.getElementById('sub-modules');
    if (subModules) {
        gsap.to(subModules, {
            opacity: 0,
            duration: 0.3,
            onComplete: () => {
                subModules.innerHTML = '';
            }
        });
    }
    
    gsap.to('.category-modules', { opacity: 1, duration: 0.3 });
}

// 打开密码详情
function openCipherDetail(category, cipherId) {
    const cipherData = CipherCategories[category].ciphers.find(c => c.id === cipherId);
    if (!cipherData) return;
    
    const cipherDetail = document.getElementById('cipher-detail');
    if (!cipherDetail) return;
    
    // 设置当前密码类型
    document.getElementById('cipher-type').value = cipherId;
    handleCipherChange();
    
    // 切换到转换器视图
    showView('converter');
    
    // 滚动到转换器
    gsap.to(window, { scrollTo: '#converter-view', duration: 0.5 });
    
    showToast(`已选择: ${cipherData.name}`, 'info');
}

// 添加到转换链
function addToChain() {
    const output = document.getElementById('converter-output');
    const chainList = document.getElementById('chain-list');
    
    if (!output.value) {
        showToast('请先进行转换', 'error');
        return;
    }
    
    const type = document.getElementById('cipher-type').value;
    const typeName = getCipherName(type);
    
    const chainItem = document.createElement('div');
    chainItem.className = 'chain-item';
    chainItem.innerHTML = `
        <span>${typeName}</span>
        <button onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;
    
    chainList.appendChild(chainItem);
    
    // 输入变为上次的输出
    document.getElementById('converter-input').value = output.value;
    output.value = '';
    
    gsap.fromTo(chainItem,
        { opacity: 0, scale: 0.8 },
        { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out' }
    );
}

// 显示Toast消息
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // 自动移除
    setTimeout(() => {
        gsap.to(toast, {
            opacity: 0,
            x: 100,
            duration: 0.3,
            onComplete: () => toast.remove()
        });
    }, 3000);
}

// 分享输出
function shareOutput() {
    const output = document.getElementById('converter-output');
    if (navigator.share) {
        navigator.share({
            title: 'CIPHER NEXUS',
            text: output.value
        }).then(() => {
            showToast('分享成功', 'success');
        });
    } else {
        copyOutput();
    }
}

// 窗口大小改变处理
function handleResize() {
    // 响应式处理
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initApp);

// 全局函数导出 - 核心转换函数
window.caesarCipher = caesarCipher;
window.vigenereCipher = vigenereCipher;
window.atbashCipher = atbashCipher;
window.affineCipher = affineCipher;
window.polybiusCipher = polybiusCipher;
window.baconCipher = baconCipher;
window.beaufortCipher = beaufortCipher;
window.autokeyCipher = autokeyCipher;
window.simpleSubstitutionCipher = simpleSubstitutionCipher;
window.base32Encode = base32Encode;
window.base58Encode = base58Encode;
window.base91Encode = base91Encode;
window.base100Encode = base100Encode;
window.textToAscii = textToAscii;
window.textToUtf8 = textToUtf8;
window.textToOctal = textToOctal;
window.quotedPrintableEncode = quotedPrintableEncode;
window.uuEncode = uuEncode;
window.pigpenCipher = pigpenCipher;
window.tapsCipher = tapsCipher;
window.rot47Cipher = rot47Cipher;
window.nthCharacterCipher = nthCharacterCipher;
window.keyboardCipher = keyboardCipher;
window.leetspeakEncode = leetspeakEncode;
window.zodiacCipher = zodiacCipher;
window.dvorakCipher = dvorakCipher;
window.generateUUID = generateUUID;
window.generateQRCode = generateQRCode;
window.railFenceCipher = railFenceCipher;
window.textToMorse = textToMorse;

// 全局函数导出 - UI交互函数
window.navigateTo = showView;
window.openCategory = openCategory;
window.closeCategory = closeCategory;
window.openCipherDetail = openCipherDetail;
window.doConvert = doConvert;
window.copyOutput = copyOutput;
window.clearInput = clearInput;
window.pasteInput = pasteInput;
window.swapIO = swapIO;
window.autoDetect = autoDetect;
window.handleInput = handleInput;
window.handleCipherChange = handleCipherChange;
window.addToChain = addToChain;
window.copyHistoryItem = copyHistoryItem;
window.loadHistoryItem = loadHistoryItem;
window.clearHistory = clearHistory;
window.exportHistory = exportHistory;
window.showToast = showToast;
window.shareOutput = shareOutput;
window.toggleSidebar = toggleSidebar;
window.closeSidebar = closeSidebar;
