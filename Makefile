all:

test:
	pytest-3 -vs

pip:
	python3 setup.py sdist

clean:
	find . -type f -name "*.pyc" -exec rm -f {} \;
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rvf {} \;


