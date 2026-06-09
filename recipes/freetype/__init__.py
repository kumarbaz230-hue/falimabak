"""Freetype — GitHub mirror (savannah.gnu.org sık 502 veriyor)."""

from pythonforandroid.recipes.freetype import FreetypeRecipe as _Base


class FreetypeRecipe(_Base):
    version = '2.14.1'
    url = (
        'https://github.com/freetype/freetype/releases/download/'
        'VER-2-14-1/freetype-{version}.tar.gz'
    )


recipe = FreetypeRecipe()
