from setuptools import find_packages, setup
print(find_packages())
"""
Obtaining file:///C:/Users/Jarvis/Desktop/Python%E5%90%8E%E7%AB%AF%E5%AD%A6%E4%B
9%A0/flask_tutorial

"""
setup(
    name="flaskr",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
    ],
)
