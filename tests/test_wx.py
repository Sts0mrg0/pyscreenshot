
from pyscreenshot.util import platform_is_osx
from ref import backend_to_check, check_import

if not platform_is_osx() and check_import("wx"):

    def test_wx():
        backend_to_check("wx")
