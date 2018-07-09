"""
This script is intended to be run after preprocess_stamps_launch.py has completed its task.

Expects the INPUT_DIR directory to contain the following items:
	test.stamps
	train.stamps
	valid.stamps
	always_black_mask.png
	simpleimage/
	simplemask/

Launches the training process.
"""

import os

# Specify the experiment number. EX: 'e70'
exp_number = 'e74'

# Specify the location of the cropped sky photos and simplified decision images
INPUT_DIR = "good_data"

# Specify the batch size, the learning rate, and the number of training steps to complete
BATCH_SIZE = 50
LEARNING_RATE = 0.0001
TRAINING_STEPS = 2000

# Specify the number of cores for BLT. BLT currently does not actually allocate this number of cores for your job,
# but instead uses this number as a way to limit the number of jobs on a node. Training uses tensorflow,
# which automatically takes advantage of all available resources, so by default the job will use the entire node. To
# stop training batches from competing with each other for compute resources, set this to a number larger than half
# of the cores on a single node. For the summer of 2018, 25 works well.
num_cores = 25

# Specify the structure of the network. This defines how train.py constructs the network to train.
variants = ['a:conv-3-32-in b:conv-3-48-a c:conv-3-64-b d:conv-3-80-c e:conv-3-96-d f:concat-e-in g:conv-3-4-f']

if __name__ == "__main__":
	i = 0
	for v in variants:
		for j in range(2):
			exp_label = exp_number + '-{:0>2}'.format(i)
			condition = exp_label + ' ' + v
			os.system('SGE_Batch -r "{}" -c "python3 -u train.py {}" -P {}'.format(exp_label, condition, num_cores))
			i += 1