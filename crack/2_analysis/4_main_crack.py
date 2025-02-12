import cv2
import numpy as np
import networkx as nx
from skimage.morphology import skeletonize
import os
import glob

def process_image(image_path, output_folder):
    
    print(f"處理檔案: {image_path}")
    
    # === 1. 讀取原圖 (二值裂縫影像) ===
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        print(f"無法讀取 {image_path}，請確認路徑或檔名。")
        return False

    # (保險) 再做一次閾值，確保為 0/255
    _, bin_img = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)

    # === 2. (可選) 形態學閉合，連接相近斷裂(若已相連可省略) ===
    kernel_close = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel_close)

    # === 3. 骨架化 (Skeletonization) ===
    closed_bool = (closed > 0)
    skel = skeletonize(closed_bool)  # 回傳 True/False
    rows, cols = skel.shape

    # === 4. 建立 Graph，用 NetworkX 找最短路徑 ===
    G = nx.Graph()
    # 取得骨架上所有的點 (r, c) 坐標
    points = np.argwhere(skel)
    points_set = set(map(tuple, points))
    # 定義八鄰域
    neighbors = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1),           (0, 1),
                 (1, -1),  (1, 0),  (1, 1)]
    
    # 為每個骨架點建立節點及與鄰近點的邊
    for (r, c) in points_set:
        G.add_node((r, c))
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            if (nr, nc) in points_set:
                weight = np.sqrt(dr**2 + dc**2)
                G.add_edge((r, c), (nr, nc), weight=weight)

    if len(G.nodes) == 0:
        print("骨架上沒有點，無法尋找路徑")
        # 如果連骨架都沒產生，同樣視為無主要裂縫，另存原圖到 no_main_crack 資料夾
        no_main_crack_folder = os.path.join(output_folder, "no_main_crack")
        if not os.path.exists(no_main_crack_folder):
            os.makedirs(no_main_crack_folder)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path_no_main = os.path.join(no_main_crack_folder, f"{base_name}_no_main_crack.png")
        cv2.imwrite(output_path_no_main, img_gray)
        print(f"已將原圖儲存到 {output_path_no_main} (骨架點數為 0)")
        return False

    # 找出所有骨架點，並挑選出最底端 (row 最大) 與最頂端 (row 最小) 的點集合
    all_points = list(G.nodes)
    max_row = max(p[0] for p in all_points)
    min_row = min(p[0] for p in all_points)
    bottom_points = [p for p in all_points if p[0] == max_row]
    top_points = [p for p in all_points if p[0] <= min_row + 20]

    # === 5. Dijkstra 找最短路徑 (自底→頂) ===
    min_dist = float('inf')
    best_path = None
    # 針對每個底端點，使用 single_source_dijkstra 找出所有可達的點
    for s in bottom_points:
        try:
            lengths, paths = nx.single_source_dijkstra(G, s, weight='weight')
            for t in top_points:
                if t in lengths and lengths[t] < min_dist:
                    min_dist = lengths[t]
                    best_path = paths[t]
        except nx.NetworkXNoPath:
            continue

    if best_path is None:
        print("找不到自底端到頂端的路徑")
        # 新增：若判斷無主要裂縫，將原圖存到 no_main_crack 資料夾中
        no_main_crack_folder = os.path.join(output_folder, "no_main_crack")
        if not os.path.exists(no_main_crack_folder):
            os.makedirs(no_main_crack_folder)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path_no_main = os.path.join(no_main_crack_folder, f"{base_name}_no_main_crack.png")
        cv2.imwrite(output_path_no_main, img_gray)
        print(f"已將原圖儲存到 {output_path_no_main} (未找到主要裂縫)")
        return False

    print("最短路徑長度:", min_dist)

    # === 6. 建立路徑遮罩，並以形態學擴張來加粗紅線 ===
    path_mask = np.zeros((rows, cols), dtype=np.uint8)
    for (r, c) in best_path:
        path_mask[r, c] = 255

    # 調整線條粗細 (調整 kernel 大小與 iterations)
    line_thickness = 20  # 此處定義線條粗細
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (line_thickness, line_thickness))
    thick_path = cv2.dilate(path_mask, kernel_dilate, iterations=1)

    # === 7. 將紅線疊回原圖 (原圖若為灰階，先轉 BGR) ===
    color_img = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
    color_img[thick_path == 255] = (0, 0, 255)  # 紅色 (B,G,R)

    # === 8. 輸出最終結果 ===
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(output_folder, f"{base_name}_main_crack.png")
    cv2.imwrite(output_path, color_img)
    print(f"已輸出 {output_path} (主要裂縫以紅線標示)")
    
    return True

def main():
    input_folder = "3_bw_output"
    output_folder = "4_main_crack_output"
    # 若輸出資料夾不存在，則建立之
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 使用 glob 讀取資料夾中所有 png 檔案
    file_list = glob.glob(os.path.join(input_folder, "*.png"))
    if not file_list:
        print(f"找不到 {input_folder} 資料夾中的 png 檔案。")
        return

    # 紀錄找不到主要裂縫的檔案
    failed_files = []

    for file_path in file_list:
        success = process_image(file_path, output_folder)
        if not success:
            failed_files.append(os.path.basename(file_path))
    
    # 最後整理顯示找不到主要裂縫的檔案名稱
    if failed_files:
        print("\n以下檔案找不到主要裂縫：")
        for name in failed_files:
            print(f"- {name}")
    else:
        print("\n所有檔案皆成功找出主要裂縫。")

if __name__ == "__main__":
    main()
