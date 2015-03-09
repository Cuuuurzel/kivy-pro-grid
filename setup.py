from setuptools import setup

setup(
    name        ='kv_progrid',
    version     ='0.1.1',
    description ='Easy to use grid for kivy.',
    url         ='https://github.com/Cuuuurzel/kivy-pro-grid',
    author      ='Federico Curzel',
    author_email='cuuuurzel@gmail.com',
    packages    =['progrid'],
    zip_safe    =False,
    install_requires=['kivy','material_ui'],
    include_package_data=True,
)
