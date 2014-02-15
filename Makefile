test:
	ls .
	pwd
	python -m unittest tests.test_frame

clean:
	rm -rf build dist
