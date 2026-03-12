# 电影推荐系统设计规范

基于参考图片逆向分析的现代化深色主题设计系统。

## 设计原则

1. **深色优先** - 采用深色背景降低视觉疲劳，提升沉浸感
2. **卡片化布局** - 内容模块化，层次清晰
3. **渐变点缀** - 使用微妙渐变增强视觉深度
4. **圆角柔和** - 大圆角营造现代友好氛围
5. **留白充足** - 保持呼吸感，避免拥挤
6. **对比明确** - 深色背景与亮色内容形成强对比

## 色板系统

### 主色调
```css
--bg-primary: #0a0e27;           /* 深蓝黑背景 */
--bg-secondary: #141b3a;         /* 次级深蓝背景 */
--bg-card: #1a2142;              /* 卡片背景 */
--bg-card-hover: #1f2750;        /* 卡片悬停 */
```

### 渐变色
```css
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
--gradient-card: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
--gradient-overlay: linear-gradient(180deg, rgba(10, 14, 39, 0) 0%, rgba(10, 14, 39, 0.8) 100%);
```

### 文本色
```css
--text-primary: #ffffff;         /* 主文本 */
--text-secondary: #a0aec0;       /* 次要文本 */
--text-muted: #718096;           /* 弱化文本 */
--text-accent: #667eea;          /* 强调文本 */
```

### 功能色
```css
--accent-purple: #667eea;        /* 主强调色 */
--accent-pink: #f5576c;          /* 次强调色 */
--success: #48bb78;              /* 成功 */
--warning: #ed8936;              /* 警告 */
--error: #f56565;                /* 错误 */
--info: #4299e1;                 /* 信息 */
```

### 边框与分割
```css
--border-subtle: rgba(255, 255, 255, 0.08);
--border-normal: rgba(255, 255, 255, 0.12);
--border-strong: rgba(255, 255, 255, 0.18);
```

## 字体系统

### 字体族
```css
--font-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
--font-mono: "SF Mono", "Consolas", "Monaco", monospace;
```

### 字号层级
```css
--text-xs: 12px;      /* 辅助信息 */
--text-sm: 14px;      /* 次要内容 */
--text-base: 16px;    /* 正文 */
--text-lg: 18px;      /* 小标题 */
--text-xl: 20px;      /* 标题 */
--text-2xl: 24px;     /* 大标题 */
--text-3xl: 30px;     /* 特大标题 */
--text-4xl: 36px;     /* 超大标题 */
```

### 字重
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 行高
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

## 布局规范

### 间距系统（8px 基准）
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
```

### 容器宽度
```css
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
--container-2xl: 1536px;
```

### 网格系统
- 电影卡片网格：`repeat(auto-fill, minmax(200px, 1fr))`
- 响应式列数：移动端 1 列，平板 2-3 列，桌面 4-6 列
- 网格间距：16-24px

## 圆角规范

```css
--radius-sm: 8px;      /* 小元素（按钮、标签）*/
--radius-md: 12px;     /* 中等元素（输入框）*/
--radius-lg: 16px;     /* 大元素（卡片）*/
--radius-xl: 20px;     /* 超大元素（模态框）*/
--radius-2xl: 24px;    /* 特大元素（Hero 区域）*/
--radius-full: 9999px; /* 圆形（头像、徽章）*/
```

## 阴影系统

```css
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.15);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.2);
--shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.25);
--shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.3);
--shadow-glow: 0 0 24px rgba(102, 126, 234, 0.4);
--shadow-glow-pink: 0 0 24px rgba(245, 87, 108, 0.4);
```

## 组件样式

### 卡片（Card）
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-normal);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-gradient {
  background: var(--gradient-card), var(--bg-card);
}
```

### 按钮（Button）
```css
.btn-primary {
  background: var(--gradient-primary);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-md);
  padding: 12px 24px;
  font-weight: var(--font-semibold);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  box-shadow: var(--shadow-glow);
  transform: translateY(-1px);
}

.btn-secondary {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-normal);
  border-radius: var(--radius-md);
  padding: 12px 24px;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-strong);
}
```

### 输入框（Input）
```css
.input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: var(--text-base);
  transition: all 0.3s ease;
}

.input:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--accent-purple);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  outline: none;
}

.input::placeholder {
  color: var(--text-muted);
}
```

### 电影卡片（Movie Card）
```css
.movie-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.3s ease;
}

.movie-card:hover {
  border-color: var(--border-normal);
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.movie-card-cover {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  background: var(--gradient-card);
}

.movie-card-content {
  padding: var(--space-4);
}

.movie-card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-card-meta {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
```

### 导航栏（Navigation）
```css
.navbar {
  background: rgba(10, 14, 39, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
}

.navbar-link {
  color: var(--text-secondary);
  text-decoration: none;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.navbar-link:hover,
.navbar-link.active {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.08);
}
```

### 搜索框（Search）
```css
.search-container {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 16px 48px 16px 20px;
  color: var(--text-primary);
  font-size: var(--text-base);
}

.search-input:focus {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--accent-purple);
  box-shadow: var(--shadow-glow);
}

.search-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}
```

## 交互状态

### 悬停（Hover）
- 卡片：上移 2-4px，增强阴影
- 按钮：上移 1px，增加发光效果
- 链接：改变颜色，添加背景

### 激活（Active）
- 按钮：下移 1px，减弱阴影
- 输入框：边框高亮，添加外发光

### 禁用（Disabled）
```css
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

### 加载（Loading）
```css
.loading {
  position: relative;
  pointer-events: none;
}

.loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(10, 14, 39, 0.6);
  backdrop-filter: blur(2px);
  border-radius: inherit;
}
```

## 动画规范

### 过渡时长
```css
--transition-fast: 150ms;
--transition-base: 250ms;
--transition-slow: 350ms;
```

### 缓动函数
```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 常用动画
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

## 响应式断点

```css
--breakpoint-sm: 640px;   /* 手机 */
--breakpoint-md: 768px;   /* 平板 */
--breakpoint-lg: 1024px;  /* 小屏笔记本 */
--breakpoint-xl: 1280px;  /* 桌面 */
--breakpoint-2xl: 1536px; /* 大屏 */
```

### 响应式策略
- 移动优先（Mobile First）
- 流式布局（Fluid Layout）
- 弹性网格（Flexible Grid）
- 自适应图片（Responsive Images）

## 设计禁区

### 禁止使用
1. ❌ 纯白背景（#ffffff）- 破坏深色主题
2. ❌ 过于鲜艳的颜色 - 视觉刺激过强
3. ❌ 小于 8px 的圆角 - 不符合现代风格
4. ❌ 硬边框（无圆角）- 视觉生硬
5. ❌ 过小的点击区域（< 44px）- 可用性差
6. ❌ 低对比度文本（对比度 < 4.5:1）- 可读性差
7. ❌ 过多的动画效果 - 分散注意力
8. ❌ 不一致的间距 - 破坏视觉节奏

### 必须遵守
1. ✅ 保持 8px 间距基准
2. ✅ 使用设计系统定义的颜色
3. ✅ 确保文本对比度符合 WCAG AA 标准
4. ✅ 所有交互元素提供视觉反馈
5. ✅ 保持组件样式一致性
6. ✅ 响应式设计覆盖所有断点
7. ✅ 动画时长不超过 350ms
8. ✅ 关键操作提供确认机制

## 可访问性（Accessibility）

### 颜色对比
- 正文文本：至少 4.5:1
- 大号文本（18px+）：至少 3:1
- 交互元素：至少 3:1

### 键盘导航
- 所有交互元素可通过 Tab 键访问
- 焦点状态清晰可见
- 支持 Enter/Space 触发操作

### 屏幕阅读器
- 图片提供 alt 文本
- 按钮提供 aria-label
- 表单元素关联 label

## 性能优化

### 图片优化
- 使用 WebP 格式
- 提供多尺寸响应式图片
- 懒加载非首屏图片
- 电影封面尺寸：200x300px（缩略图）、400x600px（详情页）

### CSS 优化
- 使用 CSS 变量减少重复
- 避免深层嵌套选择器
- 使用 transform 和 opacity 做动画
- 合理使用 will-change

### 渲染优化
- 避免布局抖动
- 使用 contain 属性隔离渲染
- 虚拟滚动处理长列表
- 防抖/节流处理高频事件
