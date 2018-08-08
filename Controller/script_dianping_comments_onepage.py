# coding:utf-8
import os
import sys

sys.path.append(os.getcwd())
from PIL import Image
import cv2
import numpy as np
import aircv as ac
from datetime import datetime
import pytesseract

import time
from Controller.setting import *
from Controller.Common import *
from Controller.NoxConDocker import NoxConDocker
from Controller.NoxConSelenium import NoxConSelenium
from Controller.ControllerManager import Manager

_DEBUG = False

navigator_bar_h = 73
author_area_h = 67  # 评论人顶端区域高度
category_area_h = 75  # 顶端分类：全部，好评，，，  高度
border_size = 128


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

    def get_photo_top_y(self):
        img_obj = ac.imread(self.capture_path)
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

    def get_page_line_y(self):
        l = []
        img_obj = cv2.imread(self.capture_comment_cut_path)
        img_border = cv2.imread(self.border_path)  # 分页线
        ret = ac.find_all_template(img_obj, img_border, threshold=0.95)
        for r in ret:
            (x, y) = r['result']
            l.append(y)
        if l:
            ret = min(l)
        else:
            ret = -1

        return ret

    def alignment_page(self, is_first=False):
        # 跳过分类区
        if is_first:
            self.scroll(from_y=140, to_y=10, wait_time=1)
        else:
            line_y = self.get_page_line_y()
            if line_y != -1:
                self.scroll(from_y=line_y, to_y=navigator_bar_h, wait_time=1)

    def concat(self):
        '''
            前后页截图 合成 滚屏效果
        '''
        img_before = Image.open(self.capture_before_path)
        # img_before = img_before.crop((0, 0, SCREEN_WIDTH, 750))
        img_before.save(self.capture_before_cut_path)

        img_current = Image.open(self.capture_path)
        img_current = img_current.crop((0, category_area_h, SCREEN_WIDTH, SCREEN_HEIGHT))  # 切掉导航栏
        img_current.save(self.capture_cut_path)

        # 800 * 480
        img_before = cv2.imread(self.capture_before_cut_path)
        img_current = cv2.imread(self.capture_cut_path)

        # 纵向合成
        img_concat = np.vstack((img_before, img_current))
        cv2.imwrite(self.capture_comment_path, img_concat)

    def one_page_cut(self, page_line_y):
        '''
            return: self.capture_comment_cut_path
        '''
        cut_y = page_line_y
        photo_top_y = self.get_photo_top_y()
        if photo_top_y != -1:
            cut_y = photo_top_y - border_size / 2

        img = Image.open(self.capture_path)
        img = img.crop((0, category_area_h + author_area_h, SCREEN_WIDTH, cut_y))
        img.save(self.capture_comment_cut_path)

    def two_page_cut(self):
        '''
            return: self.capture_comment_cut_path
        '''
        cut_y = -1
        self.concat()  # 合成前后图
        photo_top_y = self.get_photo_top_y()
        if photo_top_y != -1:
            cut_y = photo_top_y - border_size / 2
        else:
            page_line_y = self.get_page_line_y()
            if page_line_y != -1:
                cut_y = page_line_y

        img = Image.open(self.capture_comment_path)
        if cut_y != -1:
            img = img.crop((0, 180, SCREEN_WIDTH, cut_y - border_size / 2))
        img.save(self.capture_comment_cut_path)

    def ocr(self):
        image = Image.open(self.capture_comment_cut_path)
        code = pytesseract.image_to_string(image, lang='chi_sim')
        if code:
            print('-------------------\n', code)
        else:
            print('-------------------\n', 'not found comment')

    def script(self):
        self.alignment_page(is_first=True)
        ret, x, y = self.find_element(comment='展开全文', timeout=5)
        if ret:
            self.click_xy(x, y, wait_time=1)
            self.get_capture()

        # nox_adb.exe shell input swipe 240 670 240 10 2000
        # nox_adb.exe shell screencap -p /sdcard/capture.png
        # nox_adb.exe pull /sdcard/capture.png c:\Nox\

        is_one_page, _, page_line_y = self.find_element(comment='分页线', timeout=5, threshold=0.95)
        if is_one_page:
            self.one_page_cut(page_line_y)
        else:
            self.scroll(from_y=670, to_y=10, wait_time=1)
            self.get_capture()  # 更新截图
            self.two_page_cut()

        self.ocr()
        # self.back()


##################################################################################
def main(task, mode):
    msg = ''
    error = ''
    start = datetime.now()
    common_log(_DEBUG, task['taskId'], 'Script ' + task['docker_name'], 'start', task)

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
        end = datetime.now()
        print(error)
        return


#################################################################################
if __name__ == "__main__":
    _DEBUG = True
    print("start")
    if APPSIMULATOR_MODE == 'vmware':
        taskId = -1
        timer_no = -1
        mode = 'single'
    else:
        taskId = sys.argv[1]
        timer_no = int(sys.argv[2])
        mode = 'multi'

    task = {
        'taskId': taskId,
        'app_name': 'dianping',
        'docker_name': 'nox-' + str(taskId),
        'timer_no': timer_no
    }

    main(task=task, mode=mode)
    print("Close after 30 seconds.")
    time.sleep(30)
