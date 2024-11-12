import cv2
import numpy as np
import os
import argparse

version = '1.0'

parser = argparse.ArgumentParser(prog='Img2Bin',
                                 description='Convert images into Binary.')

parser.add_argument('infile', metavar='images', type=str,
                    help='absolute or relative address of image files')
parser.add_argument('-o', dest='outfile', metavar='data file', type=str)
parser.add_argument('-EC', dest='s', metavar='lc', type=float, default=30,
                    help='Edge Cutoff = 0~255 for edge detection')
parser.add_argument('-BC', dest='s', metavar='lc', type=float, default=30,
                    help='Binary Cutoff = 0~255 for binary threshold')
parser.add_argument('--version', action='version', version='%(prog)s {:s}'.format(version))

args = parser.parse_args()

infile = args.infile
EC = args.EC
BC = args.BC

# 讀取圖片
img = cv2.imread(infile)

#show the original image
# cv2.imshow('Original Image', img)
#save the original image
# cv2.imwrite('original.jpg', img)

# 灰度化
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#save the gray image
# cv2.imwrite('gray.jpg', gray)

#show the gray image
# cv2.imshow('Gray Image', gray)

# 提高對比度
hist, bins = np.histogram(gray.flatten(), 256, [0, 256])
cdf = hist.cumsum()
cdf_m = np.ma.masked_equal(cdf, 0)
cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min())
cdf = np.ma.filled(cdf_m, 0).astype('uint8') 
gray = cdf[gray]

#show the contrast image
# cv2.imshow('Contrast Image', gray)

#save the contrast image
cv2.imwrite('contrast.jpg', gray)

# 高斯模糊強化邊界
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

#show the blurred image
# cv2.imshow('Blurred Image', blurred)

#save the blurred image
# cv2.imwrite('blurred.jpg', blurred)

# 邊緣檢測
edges = cv2.Canny(blurred, 1, EC)

#show the edges image
# cv2.imshow('Edges Image', edges)

#save the edges image
cv2.imwrite('edges.jpg', edges)

# 將邊界設為黑色，其他部分設為白色
binary = cv2.threshold(edges, BC, 255, cv2.THRESH_BINARY_INV)[1]

#show the binary image
# cv2.imshow('Binary Image', binary)

#save the binary image
cv2.imwrite('binary.jpg', binary)

# 擴大邊界以使黑色部分的面積達到所需的比例
dilated = cv2.dilate(binary, None, iterations=2)

# 顯示二維化的圖形
# cv2.imshow('2D Image', dilated)

#save the 2D image
cv2.imwrite('2D.jpg', dilated)
# cv2.destroyAllWindows()
