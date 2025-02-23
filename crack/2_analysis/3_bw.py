import cv2
import numpy as np
import os
import glob

# 輸入、輸出資料夾路徑 (請依需求調整)
input_folder = '2_crop_output'
output_folder = '3_bw_output'

# 若輸出資料夾不存在則自動建立
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 取得所有 PNG 檔案路徑
file_paths = glob.glob(os.path.join(input_folder, '*.png'))

# 設定紅色的 HSV 範圍 (可依實際情況調整)
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 50, 50])
upper_red2 = np.array([180, 255, 255])

for file_path in file_paths:
    # 讀取圖片 (含 alpha 通道)
    img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"警告：無法讀取 {file_path}，略過。")
        continue

    # 判斷是否有 alpha 通道 (4 通道)
    has_alpha = (img.shape[2] == 4)

    # 拆分通道
    if has_alpha:
        b_channel, g_channel, r_channel, alpha_channel = cv2.split(img)
        bgr = cv2.merge([b_channel, g_channel, r_channel])
    else:
        bgr = img
        alpha_channel = None

    # --- 第1步：篩選紅色範圍 (HSV) 轉為二值化 ---
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask1, mask2)
    # 紅色區域為 255(白)，其他為 0(黑)

    # --- 第2步：移除面積小於 10 的白色區塊 ---
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_red, connectivity=8)
    mask_cleaned = np.zeros_like(mask_red)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 10:
            mask_cleaned[labels == i] = 255

    # --- 第3步：合回 alpha 通道 (若有) ---
    if has_alpha:
        # 生成 BGRA：白/黑 分別放在 B=G=R
        result = cv2.merge([mask_cleaned, mask_cleaned, mask_cleaned, alpha_channel])
    else:
        # 只有三通道
        result = cv2.merge([mask_cleaned, mask_cleaned, mask_cleaned])

    # --- 第4步：輸出結果 ---
    # 用你想要的方式來輸出：base_name + "_bw"
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    final_path = os.path.join(output_folder, f"{base_name}_bw.png")

    cv2.imwrite(final_path, result)
    print(f"處理完成: {file_path} → {final_path}")
