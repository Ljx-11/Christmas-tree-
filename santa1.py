import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
from math import pi, sin, cos, sqrt
from matplotlib.animation import PillowWriter

# ==============================
# 参数 - 调整粒子数量
# ==============================
N_tree = 6000        # 稍微增加树粒子数量
N_ground = 3500      # 地面粒子数量
N_snow = 1500        # 雪花数量
N_decorations = 400  # 装饰球数量

# ==============================
# 生成更大的树形粒子
# ==============================
def generate_tree(n=6000):
    z = np.random.uniform(0, 1, n)
    # 增大树的半径和高度
    radius = (1 - z)**1.5 * 3.5 + np.random.rand(n) * 0.4
    theta = np.random.uniform(0, 2*np.pi, n)
    
    x = radius * np.cos(theta) + (np.random.rand(n) - 0.5) * 0.2
    y = radius * np.sin(theta) + (np.random.rand(n) - 0.5) * 0.2
    z = z * 10 - 0.5  # 增加高度
    
    return x, y, z

# ==============================
# 生成装饰球
# ==============================
def generate_decorations(tree_x, tree_y, tree_z, n=400):
    indices = np.random.choice(len(tree_x), n, replace=False)
    deco_x = tree_x[indices] * 1.1  # 稍微向外偏移
    deco_y = tree_y[indices] * 1.1
    deco_z = tree_z[indices]
    
    colors = np.random.choice(['#FF6B6B', '#FFD93D', '#4ECDC4', '#C7C7C7'], n)
    sizes = np.random.uniform(10, 18, n)  # 稍微减小装饰球大小
    
    return deco_x, deco_y, deco_z, colors, sizes


def generate_3d_heart(n=1200, scale=0.5, z_top=10.2):
    """
    生成真正 3D 立体五角星（用于树顶）
    """

    # --------------------------------------
    # 1️⃣ 五角星的 2D 外轮廓（标准五角星路径）
    # --------------------------------------
    # 外圈半径
    R = 1.0
    # 内圈半径（黄金比例五角星）
    r = R * 0.382  

    # 五角的角度
    outer_angles = np.linspace(0, 2*np.pi, 6)[:-1]
    inner_angles = outer_angles + np.pi/5

    # 外圈点
    outer_x = R * np.cos(outer_angles)
    outer_z = R * np.sin(outer_angles)

    # 内圈点
    inner_x = r * np.cos(inner_angles)
    inner_z = r * np.sin(inner_angles)

    # 五角星顺序：外→内→外→内→…
    star_x_2d = np.empty(10)
    star_z_2d = np.empty(10)
    star_x_2d[0::2] = outer_x
    star_x_2d[1::2] = inner_x
    star_z_2d[0::2] = outer_z
    star_z_2d[1::2] = inner_z

    # --------------------------------------
    # 2️⃣ 在五角星内部随机采样 (2D)
    # --------------------------------------
    pts_x = []
    pts_y = []
    pts_z = []

    # 五角星厚度
    thickness = 0.12  

    for _ in range(n):
        # 随机从五角星内部采样（使用凸分解的思路）
        idx = np.random.randint(0, 10)
        next_idx = (idx + 1) % 10
        cx = 0
        cz = 0  # 五角星中心

        # 随机从三角形顶点采样：中心 - 顶点1 - 顶点2
        a = np.random.rand()
        b = np.random.rand()
        if a + b > 1:
            a = 1 - a
            b = 1 - b

        x = cx + a * star_x_2d[idx] + b * star_x_2d[next_idx]
        z = cz + a * star_z_2d[idx] + b * star_z_2d[next_idx]

        # Y 方向厚度（制造立体感）
        y = np.random.uniform(-thickness, thickness)

        pts_x.append(x)
        pts_y.append(y)
        pts_z.append(z)

    pts_x = np.array(pts_x)
    pts_y = np.array(pts_y)
    pts_z = np.array(pts_z)

    # --------------------------------------
    # 3️⃣ 缩放 + 噪声 + 平移到树顶
    # --------------------------------------
    pts_x *= scale
    pts_y *= scale
    pts_z *= scale

    pts_x += np.random.normal(0, 0.01, n)
    pts_y += np.random.normal(0, 0.01, n)
    pts_z += np.random.normal(0, 0.01, n)

    # 调整 z 到树顶
    min_z = np.min(pts_z)
    pts_z = pts_z - min_z + z_top

    return pts_x, pts_y, pts_z

# ==============================
# 地面 - 适应更大的树
# ==============================
def generate_ground(n=3500):
    r = np.sqrt(np.random.rand(n)) * 8  # 增大地面半径
    theta = np.random.rand(n) * 2 * np.pi
    
    wave1 = np.sin(r * 1.2) * 0.2
    wave2 = np.sin(theta * 3 + r * 1.5) * 0.1
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = wave1 + wave2 - 1
    
    return x, y, z

# ==============================
# 雪花 - 适应更大的场景
# ==============================
def generate_snow(n=1500):
    x = np.random.uniform(-11, 11, n)  # 扩大范围
    y = np.random.uniform(-11, 11, n)
    z = np.random.uniform(0, 12, n)    # 增加高度范围
    
    sizes = np.random.uniform(3, 5, n)
    
    return np.column_stack([x, y, z]), sizes

# ==============================
# 创建树的颜色
# ==============================
def create_tree_colors(z):
    normalized_z = (z - z.min()) / (z.max() - z.min())
    colors = []
    for z_val in z:
        t = (z_val - z.min()) / (z.max() - z.min())
        # 更丰富的绿色渐变
        r = 0.05 * (1 - t) + 0.25 * t
        g = 0.4 * (1 - t) + 0.85 * t
        b = 0.05 * (1 - t) + 0.25 * t
        colors.append([r, g, b])
    return colors

# ==============================
# 获取所有粒子
# ==============================
tree_x, tree_y, tree_z = generate_tree(N_tree)
deco_x, deco_y, deco_z, deco_colors, deco_sizes = generate_decorations(tree_x, tree_y, tree_z, N_decorations)
heart_x, heart_y, heart_z = generate_3d_heart(n=800, scale=0.7, z_top=9.6)
ground_x, ground_y, ground_z = generate_ground(N_ground)
snow_positions, snow_sizes = generate_snow(N_snow)

# 存储原始坐标
heart_original = np.vstack([heart_x, heart_y, heart_z])

# ==============================
# 绘制 - 调整坐标范围适应更大的树
# ==============================
fig = plt.figure(figsize=(12, 14))
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor("#0a0a2a")
fig.patch.set_facecolor("#0a0a2a")
ax.set_axis_off()

# 扩大坐标范围适应更大的树
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_zlim(-2, 8)

# 初始视角
ax.view_init(25, -30)

# 创建树的颜色
tree_colors = create_tree_colors(tree_z)

# 树（渐变绿色）- 稍微增大粒子尺寸
tree_scatter = ax.scatter(tree_x, tree_y, tree_z, s=4, c=tree_colors, alpha=0.9, linewidths=0)

# 装饰球
deco_scatter = ax.scatter(deco_x, deco_y, deco_z, s=deco_sizes, c=deco_colors, alpha=0.9)

# 立体心形（金色）- 减小粒子尺寸
heart_colors_array = np.ones((len(heart_x), 4))
heart_colors_array[:, 0] = 1.0    # R
heart_colors_array[:, 1] = 0.84   # G - 金色
heart_colors_array[:, 2] = 0.0    # B

# 心形发光效果 - 调整参数适应更小的心形
dist_center = np.sqrt(heart_x**2 + (heart_z - 10.2)**2 + heart_y**2)
heart_alpha = 0.8 * np.exp(- (dist_center**2) / (2*(0.5**2))) + 0.3
heart_colors_array[:, 3] = np.clip(heart_alpha, 0.2, 0.95)

heart_scatter = ax.scatter(heart_x, heart_y, heart_z, s=4, c=heart_colors_array)  # 减小粒子尺寸

# 地面
ground_scatter = ax.scatter(ground_x, ground_y, ground_z, s=2, color="white", alpha=0.7, linewidths=0)

# 雪花
snow_scatter = ax.scatter(snow_positions[:, 0], snow_positions[:, 1], snow_positions[:, 2], 
                         s=snow_sizes, color="white", alpha=0.8)

# 添加文字
ax.text2D(0.35, 0.25, "Merry Christmas", transform=ax.transAxes, color="#FFD93D", 
          fontsize=28, fontweight='bold', fontfamily='Comic Sans MS')  # 使用 Comic Sans MS 字体

# 添加星星背景 - 扩大范围
star_x = np.random.uniform(-10, 10, 80)
star_y = np.random.uniform(-10, 10, 80)  
star_z = np.random.uniform(8, 12, 80)
ax.scatter(star_x, star_y, star_z, s=np.random.uniform(1, 3, 80), color="white", alpha=0.6)

# ==============================
# 动画更新
# ==============================
def rotation_matrix_z(deg):
    th = np.deg2rad(deg)
    c, s = np.cos(th), np.sin(th)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]])

# 预计算值
heart_initial_sizes = np.full(len(heart_x), 4)  # 减小初始尺寸

def update(frame):
    # 雪花飘落
    snow_positions[:, 2] -= 0.07
    reset_mask = snow_positions[:, 2] < -2
    reset_count = np.sum(reset_mask)
    if reset_count > 0:
        snow_positions[reset_mask, 2] = 12
        snow_positions[reset_mask, 0] = np.random.uniform(-11, 11, reset_count)
        snow_positions[reset_mask, 1] = np.random.uniform(-11, 11, reset_count)
    snow_scatter._offsets3d = (snow_positions[:, 0], snow_positions[:, 1], snow_positions[:, 2])
    
    # 树闪烁效果
    tree_alpha = 0.85 + 0.1 * np.sin(frame * 0.2)
    tree_scatter.set_alpha(tree_alpha)
    
    # 心形旋转
    R = rotation_matrix_z(frame * 0.1)
    heart_rotated = R @ heart_original
    heart_scatter._offsets3d = (heart_rotated[0,:], heart_rotated[1,:], heart_rotated[2,:])
    
    # 心形脉动效果 - 减小脉动幅度
    pulse = 0.9 + 0.1 * np.sin(frame * 0.15)
    current_sizes = heart_initial_sizes * pulse
    heart_scatter.set_sizes(current_sizes)
    
    # 心形颜色闪烁
    heart_alpha_dynamic = 0.7 + 0.3 * np.sin(frame * 0.12)
    current_colors = heart_colors_array.copy()
    current_colors[:, 3] = np.clip(heart_colors_array[:, 3] * heart_alpha_dynamic, 0.2, 0.95)
    heart_scatter.set_color(current_colors)
    
    # 装饰球闪烁
    deco_alpha = 0.8 + 0.2 * np.sin(frame * 0.25)
    deco_scatter.set_alpha(deco_alpha)
    
    # 缓慢旋转视角
    elev = 25 + 1.5 * np.sin(frame * 0.04)
    azim = -30 + frame * 0.08
    ax.view_init(elev, azim)
    
    return []

# 创建动画
try:
    ani = FuncAnimation(fig, update, frames=1000, interval=40, blit=False, repeat=True)
    plt.tight_layout()
    plt.show()
except Exception as e:
    print(f"动画错误: {e}")
    plt.tight_layout()
    plt.show()
    
    
# 创建动画
# try:
#     ani = FuncAnimation(fig, update, frames=100, interval=40, blit=False, repeat=True)
    
#     # 保存为GIF
#     print("正在保存GIF，请稍候...")
#     gif_filename = "christmas_tree_animation.gif"
    
#     # 使用PillowWriter保存GIF，设置dpi=100
#     writer = PillowWriter(fps=25, 
#                          metadata=dict(artist='Christmas Tree Animation'), 
#                          bitrate=1800)
    
#     ani.save(gif_filename, writer=writer, dpi=100)
#     print(f"GIF已保存为: {gif_filename}")
    
#     plt.tight_layout()
#     plt.show()
    
# except Exception as e:
#     print(f"动画错误: {e}")
#     plt.tight_layout()
#     plt.show()

