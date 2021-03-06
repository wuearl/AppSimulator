import sys
import os
import time
from datetime import datetime
from PIL import Image
import cv2
import numpy as np
import aircv as ac
import pytesseract

sys.path.append(os.getcwd())

from Controller.setting import APPSIMULATOR_MODE
from Controller.Common import *
from Controller.NoxConSelenium import NoxConSelenium
from Controller.ControllerManager import Manager


#################################################################################
class MySelenium(NoxConSelenium):
    def __init__(self, task_info, mode):
        super().__init__(task_info=task_info, mode=mode)

        self.capture_name = 'capture_' + self._docker_name + '.png'
        self.capture_before_name = 'capture_' + self._docker_name + '_before.png'
        self.capture_path = self._work_path + '\\Controller\\images\\temp\\' + self.capture_name
        self.capture_before_path = self._work_path + '\\Controller\\images\\temp\\' + self.capture_before_name

        self.capture_cut_name = 'capture_' + self._docker_name + '_cut.png'
        self.capture_before_cut_name = 'capture_' + self._docker_name + '_before_cut.png'
        self.capture_cut_path = self._work_path + '\\Controller\\images\\temp\\' + self.capture_cut_name
        self.capture_before_cut_path = self._work_path + '\\Controller\\images\\temp\\' + self.capture_before_cut_name

        self.capture_comment_name = 'capture_' + self._docker_name + '_comment.png'
        self.capture_comment_cut_name = 'capture_' + self._docker_name + '_comment_cut.png'
        self.capture_comment_path = self._work_path + '\\Controller\\images\\temp\\' + self.capture_comment_name
        self.capture_comment_cut_path = self._work_path + '\\Controller\\images\\temp\\' + self.capture_comment_cut_name

        # border_path = self._work_path + '\\Controller\\images\\dianping\\border.png'
        self.border_path = self._work_path + '\\Controller\\images\\dianping\\border_128_128.png'

    def get_photo_top_y(self, img_obj):
        # 照片图框 152 * 152 or 128 * 128
        img_border = ac.imread(self.border_path)
        h, w, _ = img_border.shape
        ret = ac.find_all_template(img_obj, img_border, threshold=0.5)
        l = []
        for r in ret:
            (x, y) = r['result']
            l.append(y)

        if l:
            ret = min(l)
        else:
            ret = -1

        return ret

    def pic_to_ocr(self, one_page, photo_top_y, page_line_y):
        # start = datetime.now()
        if one_page:
            y = 800
            img = Image.open(self.capture_path)
            if photo_top_y != -1:
                y = photo_top_y
            else:
                if page_line_y != -1:
                    y = page_line_y

            img = img.crop((0, 75, 480, y))
            img.save(self.capture_comment_cut_path)

        else:  # page_line_y is next page y
            # 前后页分别截图
            img = Image.open(self.capture_before_path)
            # img = img.crop((0, 0, 480, 750))
            img.save(self.capture_before_cut_path)

            img = Image.open(self.capture_path)
            img = img.crop((0, 75, 480, 800))
            img.save(self.capture_cut_path)

            # 800 * 480
            img1 = cv2.imread(self.capture_before_cut_path)
            img2 = cv2.imread(self.capture_cut_path)

            # 纵向合成
            img_concat = np.vstack((img1, img2))
            cv2.imwrite(self.capture_comment_path, img_concat)

            # 合成图截图
            img = Image.open(self.capture_comment_path)
            img = img.crop((0, 180, 480, min_y - h / 2))
            img.save(self.capture_comment_cut_path)

            image = Image.open(self.capture_comment_cut_path)
            code = pytesseract.image_to_string(image, lang='chi_sim')
            if code:
                print('-------------------\n', code)
            else:
                print('-------------------\n', 'not found comment')

    def script(self):
        # ret, x, y = self.find_element(comment='APP打开结果OK', timeout=60)
        #
        self.v_scroll(from_y=140, to_y=10, wait_time=1)

        ret, x, y = self.find_element(comment='展开全文', timeout=5)
        if ret:
            self.click_xy(x, y, wait_time=1)
            self.get_capture()

        # nox_adb.exe shell input swipe 240 670 240 10 2000
        # nox_adb.exe shell screencap -p /sdcard/capture.png
        # nox_adb.exe pull /sdcard/capture.png c:\Nox\
        ret, _, page_line_y = self.find_element(comment='分页线', timeout=5)
        if ret:
            img_obj = cv2.imread(self.capture_path)
            photo_top_y = self.get_photo_top_y(img_obj)
        else:
            ret = self.v_scroll(from_y=670, to_y=10, wait_time=1)
            self.get_capture()  # 更新截图
            img_obj = cv2.imread(self.capture_path)
            photo_top_y = self.get_photo_top_y(img_obj)
            if photo_top_y == -1:
                ret, _, page_line_y = self.find_element(comment='分页线', timeout=5)

        self.pic_to_ocr(one_page=ret, photo_top_y=photo_top_y, page_line_y=page_line_y)

        # self.back()
        # ret = self.next_page(wait_time=1)


##################################################################################
def main(task, mode):
    msg = ''
    error = ''
    start = datetime.now()
    common_log(True, task['taskId'], 'Script ' + task['docker_name'], 'start', task)

    try:
        me = MySelenium(task_info=task, mode=mode)
        me.set_comment_to_pic({
            "web打开APP": 'images/dianping/webOpenApp.png',
            "APP打开结果OK": 'images/dianping/search_ready.png',
            "APP图标": 'images/dianping/app_icon.png',
            '附近热搜': 'images/dianping/search.png',
            '搜索': 'images/dianping/search_btn.png',
            "网友点评": 'images/dianping/wangyoudianping.png',
            "全部网友点评": 'images/dianping/wangyoudianping-all.png',
            "分享": 'images/dianping/share.png',
            "复制链接": 'images/dianping/copy_link.png',
            "打分": 'images/dianping/dafen.png',
            "展开全文": 'images/dianping/show_all.png',
            "分页线": 'images/dianping/page_line.png',
            "star": 'images/dianping/star.png',
        })
        me._DEBUG = True
        me.run()
    except Exception as e:
        msg = '<<error>>'
        error = e
    finally:
        if APPSIMULATOR_MODE == MODE_MULTI:  # multi nox mode
            m = Manager()
            m.nox_run_task_finally(taskId)

        common_log(True, task['taskId'], 'Script ' + task['docker_name'] + 'end.',
                   msg + 'total times:' + str((datetime.now() - start).seconds) + 's', error)
        return


#################################################################################
if __name__ == "__main__":
    # APPSIMULATOR_MODE = MODE_SINGLE
    if APPSIMULATOR_MODE == MODE_SINGLE:
        taskId = -1
        timer_no = -1
        redis_key = 'test'
    else:
        taskId = sys.argv[1]
        timer_no = int(sys.argv[2])
        redis_key = sys.argv[3]

    task = {
        'taskId': taskId,
        'app_name': 'dianping',
        'redis_key': redis_key,
        'docker_name': 'nox-' + str(taskId),
        'timer_no': timer_no
    }

    main(task=task, mode=APPSIMULATOR_MODE)
    print("Quit after 30 seconds.")
    time.sleep(30)
