from setuptools import find_packages, setup

setup(
    name="experiment",
    packages=find_packages(),
    use_scm_version={"write_to": "experiment/_version.py"},
    setup_requires=["setuptools_scm"],
    description="Experiment control software for touch screen apparatus",
    author="Janahan Selvanayagam",
    author_email="seljanahan@hotmail.com",
    keywords=["touchscreen", "experiment"],
    install_requires=[
        "click",
        "pygame",
        "pyyaml",
        "numpy",
        "pillow",
        "opencv-python",
        "tqdm",
        "pandas",
        "tqdm",
    ],
    entry_points="""
        [console_scripts]
        experiment=experiment.scripts:experiment
    """,
    zip_safe=False,
)
