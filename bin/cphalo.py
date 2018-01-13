import lib
import logging

#set up logging
logging.root
logging.root.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s %(message)s')
#with zero args , should go to STD ERR
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.root.addHandler(handler)

def test():
	logging.info(lib.Event())
	return None

if __name__ == "__main__":
	test()
    sys.exit(0)

