import cv2
import numpy as np
import os
from PIL import Image

def remove_white_border_image(pil_img, threshold=240):
    """
    將傳入的 PIL Image 中接近白色的區域變為透明，
    再利用 getbbox() 裁切掉透明的邊界，回傳裁切後的圖片。
    
    :param pil_img: 輸入的 PIL Image 物件
    :param threshold: 白色判定閾值，RGB 三值 >= 此值則視為白色
    :return: 裁切後的 PIL Image 物件
    """
    pil_img = pil_img.convert("RGBA")
    arr = np.array(pil_img)
    # 建立 mask：當 R、G、B 三色皆大於等於 threshold 時，視為白色
    mask = (arr[..., 0] >= threshold) & (arr[..., 1] >= threshold) & (arr[..., 2] >= threshold)
    arr[mask, 3] = 0  # 將符合條件的 alpha 設為 0 (透明)
    new_img = Image.fromarray(arr)
    
    bbox = new_img.getbbox()
    if bbox:
        return new_img.crop(bbox)
    else:
        return new_img

def process_image(file_path, output_dir, threshold_value=250, white_threshold=240):
    """
    處理單一圖片的流程：
      1. 讀取圖片後裁切出左半邊（捨棄右半邊）。
      2. 轉灰階、threshold 找出非白色區域，並利用最大輪廓取得模型區域。
      3. 將模型區域轉為 PIL Image，去除白邊框後存檔。
    
    :param file_path: 輸入檔案路徑
    :param output_dir: 輸出檔案存放資料夾
    :param threshold_value: OpenCV threshold 閾值（用於找出白邊反相區域）
    :param white_threshold: PIL 去除白邊框的閾值
    """
    # 讀取圖片（使用 OpenCV 讀取 BGR 格式）
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"讀不到影像：{file_path}")

    # 裁切出左半邊 (假設左右區域寬度相同)
    h, w, _ = img.shape
    mid_x = w // 2
    left_img = img[:, :mid_x]

    # 轉灰階及 threshold 處理：將近白色區域反相（變成黑色）以便取得輪廓
    gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
    _, thr = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # 取得輪廓，選擇面積最大的區域作為模型區域
    contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"警告：在 {file_path} 找不到任何輪廓，跳過此檔案。")
        return

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w_box, h_box = cv2.boundingRect(largest_contour)
    model_img = left_img[y:y+h_box, x:x+w_box]

    # 將 OpenCV BGR 轉換為 PIL Image（RGB 模式）
    pil_img = Image.fromarray(cv2.cvtColor(model_img, cv2.COLOR_BGR2RGB))

    # 去除模型圖片中的白色邊框
    final_img = remove_white_border_image(pil_img, threshold=white_threshold)

    # 儲存最終輸出檔案（只保留一個輸出檔）
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    final_path = os.path.join(output_dir, f"{base_name}_crop.png")
    final_img.save(final_path, "PNG")
    print(f"處理檔案：{file_path}")
    print(f"  → 最終輸出檔案：{final_path}\n")

def main():
    # 取得程式所在目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 設定輸入資料夾 (crack_png) 與輸出資料夾 (output)
    input_folder = os.path.join(script_dir, "crack_png")
    output_folder = os.path.join(script_dir, "2_crop_output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 搜尋輸入資料夾中的所有 PNG 檔案（不分大小寫）
    png_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder)
                 if f.lower().endswith(".png")]

    if not png_files:
        print("在 crack_png 資料夾中找不到 PNG 檔案。")
        return

    # 逐一處理每個檔案
    for file_path in png_files:
        try:
            process_image(file_path, output_folder)
        except Exception as e:
            print(f"處理 {file_path} 時發生錯誤：{e}")

if __name__ == '__main__':
    main()
