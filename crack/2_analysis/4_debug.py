import cv2
import numpy as np
import networkx as nx
from skimage.morphology import skeletonize
import os
import glob

def process_image(image_path, output_folder, debug=False):
    """
    處理單一張圖片，並在 debug 模式下儲存中間結果檢查各步驟。
    """
    print(f"處理檔案: {image_path}")
    
    # 1. 讀取原圖 (二值裂縫影像)
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img_gray is None:
        print(f"無法讀取 {image_path}，請確認路徑或檔名。")
        return False

    # 取得檔案基本名稱，方便後續存檔
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # 若啟用 debug 模式，建立 debug 子資料夾
    if debug:
        debug_folder = os.path.join(output_folder, "debug")
        if not os.path.exists(debug_folder):
            os.makedirs(debug_folder)

    # 2. 再做一次閾值處理 (保險用，即使圖本來已二值化)
    _, bin_img = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    if debug:
        debug_path = os.path.join(debug_folder, f"{base_name}_binary.png")
        cv2.imwrite(debug_path, bin_img)
        print(f"已儲存二值化圖: {debug_path}")

    # 3. 形態學閉合，連接相近斷裂
    kernel_close = np.ones((25, 25), np.uint8)
    closed = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel_close)
    if debug:
        debug_path = os.path.join(debug_folder, f"{base_name}_closed.png")
        cv2.imwrite(debug_path, closed)
        print(f"已儲存閉合後圖: {debug_path}")

    # 4. 骨架化
    closed_bool = (closed > 0)
    skel = skeletonize(closed_bool)  # 回傳 True/False 的陣列
    rows, cols = skel.shape
    # 將骨架化結果轉換為 0/255 的圖以便儲存
    skel_img = (skel.astype(np.uint8)) * 255
    if debug:
        debug_path = os.path.join(debug_folder, f"{base_name}_skeleton.png")
        cv2.imwrite(debug_path, skel_img)
        print(f"已儲存骨架化圖: {debug_path}")

    # 5. 建立 Graph，用於後續尋找最短路徑
    G = nx.Graph()
    points = np.argwhere(skel)
    points_set = set(map(tuple, points))
    # 定義 8 鄰域
    neighbors = [(-1, -1), (-1, 0), (-1, 1),
                 (0, -1),           (0, 1),
                 (1, -1),  (1, 0),  (1, 1)]
    
    for (r, c) in points_set:
        G.add_node((r, c))
        for dr, dc in neighbors:
            nr, nc = r + dr, c + dc
            if (nr, nc) in points_set:
                weight = np.sqrt(dr**2 + dc**2)
                G.add_edge((r, c), (nr, nc), weight=weight)

    if len(G.nodes) == 0:
        print("骨架上沒有點，無法尋找路徑")
        return False

    # 6. 找出所有骨架點，挑選出最底端與最頂端的點集合
    all_points = list(G.nodes)
    max_row = max(p[0] for p in all_points)
    min_row = min(p[0] for p in all_points)
    bottom_points = [p for p in all_points if p[0] == max_row]
    top_points = [p for p in all_points if p[0] <= min_row + 20]

    if debug:
        print(f"底部點: {bottom_points}")
        print(f"頂部點: {top_points}")
        # 將底部點與頂部點標示在骨架圖上
        skel_color = cv2.cvtColor(skel_img, cv2.COLOR_GRAY2BGR)
        for p in bottom_points:
            # 底部點以紅色圓點標示
            cv2.circle(skel_color, (p[1], p[0]), radius=10, color=(0, 0, 255), thickness=-1)
        for p in top_points:
            # 頂部點以藍色圓點標示
            cv2.circle(skel_color, (p[1], p[0]), radius=10, color=(255, 0, 0), thickness=-1)
        debug_path = os.path.join(debug_folder, f"{base_name}_endpoints.png")
        cv2.imwrite(debug_path, skel_color)
        print(f"已儲存標示底部與頂部點圖: {debug_path}")

    # 7. 使用 Dijkstra 演算法找出從底部到頂部的最短路徑
    min_dist = float('inf')
    best_path = None
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
        return False

    print("最短路徑長度:", min_dist)

    if debug:
        # 將最短路徑標示在骨架圖上 (綠色點)
        skel_color_with_path = cv2.cvtColor(skel_img, cv2.COLOR_GRAY2BGR)
        for (r, c) in best_path:
            cv2.circle(skel_color_with_path, (c, r), radius=2, color=(0, 255, 0), thickness=-1)
        debug_path = os.path.join(debug_folder, f"{base_name}_path.png")
        cv2.imwrite(debug_path, skel_color_with_path)
        print(f"已儲存標示最短路徑圖: {debug_path}")

    # 8. 建立路徑遮罩，並以形態學膨脹加粗線條
    path_mask = np.zeros((rows, cols), dtype=np.uint8)
    for (r, c) in best_path:
        path_mask[r, c] = 255
    line_thickness = 20  # 設定線條粗細
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (line_thickness, line_thickness))
    thick_path = cv2.dilate(path_mask, kernel_dilate, iterations=1)
    if debug:
        debug_path = os.path.join(debug_folder, f"{base_name}_thick_path.png")
        cv2.imwrite(debug_path, thick_path)
        print(f"已儲存加粗後路徑遮罩圖: {debug_path}")

    # 9. 將紅線疊回原圖 (原圖轉換成彩色)
    color_img = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
    color_img[thick_path == 255] = (0, 0, 255)  # 使用紅色標示主要裂縫
    output_path = os.path.join(output_folder, f"{base_name}_final.png")
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

    # 可透過 debug 參數開啟中間檢查步驟
    for file_path in file_list:
        success = process_image(file_path, output_folder, debug=True)
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
