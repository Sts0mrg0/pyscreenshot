import logging
import os
from time import sleep

from easyprocess import EasyProcess
from PIL import Image, ImageChops

import fillscreen
import pyscreenshot
from config import bbox_ls
from double_disp import check_double_disp
from image_debug import img_debug
from pyscreenshot.util import py2

# backend tester (bt)


def check_ref(backend, bbox, childprocess, refimgpath):
    img_ref = Image.open(refimgpath)
    logging.debug("ref full getextrema: %s", img_ref.getextrema())
    if bbox:
        img_ref = img_ref.crop(bbox)

    im = pyscreenshot.grab(bbox=bbox, backend=backend, childprocess=childprocess)

    img_ref = img_ref.convert("RGB")
    logging.debug("ref  getextrema: %s", img_ref.getextrema())
    im = im.convert("RGB")
    logging.debug("shot getextrema: %s", im.getextrema())

    assert "RGB" == img_ref.mode
    assert "RGB" == im.mode

    img_debug(img_ref, "ref" + str(bbox))
    img_debug(im, str(backend) + str(bbox))

    img_diff = ImageChops.difference(img_ref, im)
    ex = img_diff.getextrema()
    logging.debug("diff getextrema: %s", ex)
    diff_bbox = img_diff.getbbox()
    if diff_bbox:
        img_debug(img_diff, "img_diff" + str(diff_bbox))
    # if (
    #     platform_is_osx()
    #     and backend
    #     and backend in ["qtpy", "pyqt", "pyqt5", "pyside", "pyside2"]
    # ):
    #     color_diff_max = max([b for (_, b) in ex])
    #     assert color_diff_max < 70
    # else:
    if not diff_bbox is None:
        print(
            "different image data %s bbox=%s extrema:%s diff_bbox=%s"
            % (backend, bbox, ex, diff_bbox)
        )
    assert diff_bbox is None


def backend_ref(backend, childprocess=True, refimgpath="", delay=0):
    for bbox in bbox_ls:
        print("bbox: {}".format(bbox))
        print("backend: %s" % backend)
        check_ref(backend, bbox, childprocess, refimgpath)
        if delay:
            sleep(delay)


def backend_to_check(backend, delay=0):
    refimgpath = fillscreen.init()
    backend_ref(backend, childprocess=True, refimgpath=refimgpath, delay=delay)
    backend_ref(backend, childprocess=None, refimgpath=refimgpath, delay=delay)

    check_double_disp(backend)


def kde():
    XDG_CURRENT_DESKTOP = os.environ.get("XDG_CURRENT_DESKTOP")
    if XDG_CURRENT_DESKTOP:
        return "kde" in XDG_CURRENT_DESKTOP.lower()


def gnome():
    XDG_CURRENT_DESKTOP = os.environ.get("XDG_CURRENT_DESKTOP")
    if XDG_CURRENT_DESKTOP:
        return "gnome" in XDG_CURRENT_DESKTOP.lower()


def check_import(module):
    found = False
    # try:
    #     __import__(module)

    #     ok = True
    # except ImportError:
    #     pass
    if py2():
        import imp

        try:
            imp.find_module(module)
            found = True
        except ImportError:
            found = False
    else:
        import importlib

        spam_spec = importlib.util.find_spec(module)
        found = spam_spec is not None
    return found


def prog_check(cmd):
    try:
        if EasyProcess(cmd).call().return_code == 0:
            return True
    except Exception:
        return False