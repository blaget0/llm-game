import joblib
import cv2
import sklearn
import numpy as np

def origin_LBP(img):
    dst = np.zeros(img.shape, dtype=img.dtype)
    h, w = img.shape
    start_index = 1
    for i in range(start_index, h - 1):
        for j in range(start_index, w - 1):
            center = img[i][j]
            code = 0
            # Clockwise, 8 pixel points compared to center
            code |= (img[i - 1][j - 1] >= center) << 7
            code |= (img[i - 1][j] >= center) << 6
            code |= (img[i - 1][j + 1] >= center) << 5
            code |= (img[i][j + 1] >= center) << 4
            code |= (img[i + 1][j + 1] >= center) << 3
            code |= (img[i + 1][j] >= center) << 2
            code |= (img[i + 1][j - 1] >= center) << 1
            code |= (img[i][j - 1] >= center) << 0
            dst[i - start_index][j - start_index] = code
    return dst


def find_unit_properties(imgs):
    model = joblib.load(r'llm_code\baseline_logreg (1).joblib')

    vectors = []

    for img in imgs:
        img = cv2.imread(img)
        resized = cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        lbp = origin_LBP(gray).flatten()
        vectors.append(lbp)
    vectors = np.array(vectors)


    preds = model.predict_proba(vectors)

    return preds 



if __name__ =='__main__':
    print(find_unit_properties([r'llm_code\unit3.png', r'llm_code\unit1.png']))
