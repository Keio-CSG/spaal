from distutils.core import setup

setup(
    name="spaal",
    py_modules=["spaal"],
    version="0.1",
    description="Simulator of Spoofing Attacks against LiDARs",
    author="Yuki Hayakawa",
    author_email="hykwyuk@keio.jp",
    install_requires=["numpy","pandas","matplotlib"],
)
