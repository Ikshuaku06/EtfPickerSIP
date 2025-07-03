from setuptools import setup, find_packages

setup(
    name="EtfPickerSIP",
    version="0.1.0",
    packages=find_packages(include=["Config", "utilities"]),
    install_requires=[
        "streamlit",
        "yfinance",
        "pandas",
        # Add other dependencies here
    ],
    author="Ikshuaku Dhar",
    description="A Streamlit app for ETF tracking and picking.",
    include_package_data=True,
    python_requires=">=3.7",
)
