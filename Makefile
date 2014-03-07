test:
	python -m unittest tests.test_frame


clean:
	rm -rf build dist
	rm `find . | grep pyc`
