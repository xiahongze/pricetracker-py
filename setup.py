from pathlib import Path

from setuptools import setup

__app__ = 'pricetracker'
__version__ = Path(__file__).parent.joinpath(f'{__app__}/assets/VERSION').read_text()


def get_lines(this_path: Path, filename: str):
    lines = this_path.with_name(filename).read_text().split('\n')
    return [l.strip() for l in lines if l.strip()]


if __name__ == "__main__":
    this_path = Path(__file__)
    doc = this_path.with_name("README.md").read_text()
    install_requires = get_lines(this_path, "requirements.txt")
    test_requires = get_lines(this_path, "requirements_test.txt")

    setup(
        name=__app__,
        version=__version__,
        author='Hongze Xia',
        url='https://github.com/xiahongze/pricetracker-py',
        description='Price Tracking Application',
        long_description=doc,
        long_description_content_type='text/markdown',
        license='MIT',
        packages=[__app__],
        package_data={__app__: ["assets/*"]},
        install_requires=install_requires,
        tests_require=test_requires,
        zip_safe=True,
        test_suite="tests"
    )
