from imutils import contours
import numpy as np
import imutils
import cv2
from shutil import move
from os import remove
from os.path import dirname, realpath, join

SCREENSHORT_PATH_REMOTE_SOURCE = 'screenshort/path/remote/source.png'


class OCR:
    def __init__(self):
        """
        Initialization
        """
        here = dirname(realpath(__file__))
        self.reference_images_path = join(here, '..', 'reference_images', 'reference_images.jpg')
        screenshort_dir_local_dest = join(here, '..', 'captured_images')
        self.screenshort_path_local_dest_png = join(screenshort_dir_local_dest, 'screenshort.png')
        self.screenshort_path_local_dest_jpg = join(screenshort_dir_local_dest, 'screenshort.jpg')

    def plot_graph(self, img):
        """
        Plat images for debug only
        """
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def process_background_is_white(self, image):
        """
        Process and return if background is white
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert it to grayscale
        image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)[1]  # thresholding
        n_white_pix = np.sum(image == 255)
        n_black_pix = np.sum(image == 0)
        return image, n_white_pix > n_black_pix

    def process_image(self, image):
        """
        Create dictionary of splitted images
        """
        image, backgrond_is_white = self.process_background_is_white(image)
        if backgrond_is_white:
            image = cv2.bitwise_not(image)
        cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = contours.sort_contours(cnts, method="left-to-right")[0]
        digits = {}
        for (i, c) in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            roi = image[y:y + h, x:x + w]
            roi = cv2.resize(roi, (57, 88))
            digits[i] = roi
        return digits

    def create_references(self):
        """
        Create references for matching with captured images
        """
        image = cv2.imread(self.reference_images_path)
        return self.process_image(image)

    def read_resize(self):
        """
        Read and resize images
        """
        image = cv2.imread(self.screenshort_path_local_dest_jpg)
        return imutils.resize(image, width=300)

    def read_numbers(self):
        """
        Read and return numbers result
        """
        image = self.read_resize()
        return self.process_image(image)

    def read_background(self):
        """
        Read and return background result
        """
        image = self.read_resize()
        return self.process_background_is_white(image)[1]

    def replace_to_ofn_letters(self, digit):
        """
        Replace digits 10, 11, 12 to letters O, F, N respectively
        """
        digits = {'10': 'O', '11': 'F', '12': 'N'}
        if digit in digits.keys():
            return digits[digit]
        return digit

    def match_digits(self, digits_read, digits_template):
        """
        Match digits or letters with template and return float number or True/False if there is ON/OFF message
        """
        result = ''
        for num, digit_read_value in enumerate(digits_read.values()):            
            n_white_pix = np.sum(digit_read_value == 255)
            n_black_pix = np.sum(digit_read_value == 0)
            if n_white_pix > n_black_pix:
                digit = '.'
            else:
                scores = []
                for template_key, template_value in digits_template.items():
                    match_result = cv2.matchTemplate(digit_read_value, template_value, cv2.TM_CCOEFF)
                    (_, score, _, _) = cv2.minMaxLoc(match_result)
                    scores.append(score)
                digit = str(np.argmax(scores))
            digit = self.replace_to_ofn_letters(digit)
            result += digit
        result = result.replace('0', 'O') if 'F' in result or 'N' in result else result
        return {'ON': True, 'OFF': False}[result] if result == 'ON' or result == 'OFF' else float(result)

    def move_image_encode_jpg(self):
        """
        Moves and encodes from png to jpg
        """
        move(SCREENSHORT_PATH_REMOTE_SOURCE, self.screenshort_path_local_dest_png)
        img = cv2.imread(self.screenshort_path_local_dest_png)
        cv2.imwrite(self.screenshort_path_local_dest_jpg, img)
        remove(self.screenshort_path_local_dest_png)

    def get_number(self):
        """
        Get float Number or button ON/OFF message
        """
        self.move_image_encode_jpg()
        digits_template = self.create_references()
        digits_read = self.read_numbers()
        return self.match_digits(digits_read, digits_template)

    def get_background(self):
        """
        Get Button background
        """
        self.move_image_encode_jpg()
        return self.read_background()
