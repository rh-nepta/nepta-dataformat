all:

test:
	hatch run test

pip:
	hatch build

clean:
	rm -vf report*.xml
	find . -type f -name "*.pyc" -exec rm -f {} \;
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rvf {} \;


