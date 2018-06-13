import sys

from preprocess import simplify_image, simplify_mask

if __name__ == "__main__":
	f = open(sys.argv[1])  # This is the name of the file containing timestamps
	print("Opened {}".format(sys.argv[1]))
	for time in f:
		time = time.replace('\n', '')
		simplify_mask(time)
		simplify_image(time)