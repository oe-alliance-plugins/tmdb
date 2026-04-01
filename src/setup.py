from setuptools import setup
import setup_translate

pkg = 'Extensions.tmdb'
setup(name='enigma2-plugin-extensions-tmdb',
       version='3.0',
       description='Show TMDb information',
       package_dir={pkg: 'tmdb'},
       packages=[pkg],
       package_data={pkg: ['images/*.png', '*.png', '*.xml', 'locale/*/LC_MESSAGES/*.mo', 'keymap.xml', 'setup.xml', 'pic/*.png', 'pic/*.jpg']},
       cmdclass=setup_translate.cmdclass,  # for translation
      )
