test:
	pip install TwistedWebsocket
	cd ./tests/
	python test_frame.py

clean:
	rm -rf build dist
