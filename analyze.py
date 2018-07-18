#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finds the images (in a batch from the validation set) for which the network
most disagrees with the targets and displays how the outputs and targets
disagree.

Command line arguments:
dir

dir is the results directory where the network is stored.

Created on Thu Jun 15 15:32:13 2017

@author: jeffmullins
"""

import matplotlib
import tensorflow as tf

from preprocess_setup_launch import *
from train import build_net, load_inputs, load_validation_stamps
from train_launch import BATCH_SIZE
from utils import extract_mask_path_from_time, out_to_image, get_simple_mask, get_network_mask_from_time_and_label

matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUT_DIR = 'good_data'


def disagreement_rate(output, target):
	"""Returns the proportion of pixels in output that disagree with target."""
	return np.sum((output != target).any(axis=2)) / (480 * 480)


def find_worst_results(num_worst, time_stamps, directory, step_version, layer_info):
	"""Returns the the timestamps of the num_worst images for which the network
	most disagrees with the target masks."""
	_, _, saver, _, x, y, _, _ = build_net(layer_info)
	with tf.Session() as sess:
		saver.restore(sess, directory + 'weights-' + str(step_version))
		time_stamps = load_validation_stamps(BATCH_SIZE)
		rates = np.zeros(len(time_stamps))
		for i, s in enumerate(time_stamps):
			inputs = load_inputs([s])
			result = out_to_image(y.eval(feed_dict={x: inputs}))
			result = result.reshape(480, 480, 3)
			mask = read_target(s)
			rates[i] = disagreement_rate(result, mask)
		# Display a graph of accuracies
		fig, ax = plt.subplots(nrows=1, ncols=1)
		ax.plot(np.take(rates * 100, np.flip((rates.argsort()), axis=0)))
		ax.set_ylabel('Percent of Pixels Incorrect')
		ax.set_xlabel('Image (sorted by accuracy)')
		fig.savefig(directory + 'accuracy_plot.png', bbox_inches='tight')
		# Report the worst disagreement rates
		indices = rates.argsort()[num_worst * -1:][::-1]
		print('Worst results percentages:\t' + str(np.take(rates, indices)))
	return np.take(time_stamps, indices)


def read_target(timestamp):
	"""Reads and returns the target mask corresponding to timestamps from
	the simplemask directory."""
	return np.array(misc.imread(extract_mask_path_from_time(timestamp, INPUT_DIR)))


def read_targets(timestamps):
	"""Reads and returns the target masks corresponding to timestamps from
	the simplemask directory."""
	masks = np.empty((len(timestamps), 480, 480, 3))
	for i, s in enumerate(timestamps):
		masks[i] = read_target(s)
	return masks


def run_stamps(saver, x, y, result_dir, iteration, stamps):
	"""Loads the images for the specified timestamps and runs the network
	(using saved weights for iteration) on them. Returns the output images."""
	with tf.Session() as sess:
		saver.restore(sess, result_dir + 'weights-' + str(iteration))
		inputs = load_inputs(stamps)
		outputs = out_to_image(y.eval(feed_dict={x: inputs}))
		return outputs.reshape(-1, 480, 480, 3)


def show_sky_images(timestamps):
	"""Shows the input images for timestamps."""
	for s in timestamps:
		Image.fromarray(np.array(misc.imread(extract_mask_path_from_time(s, INPUT_DIR)))).show()


# TODO: write a function that saves the disagreement rates in a csv file, in order
# TODO: create plots from the csv file

def show_plot_of_pixel_difference(timestamps, exp_label, directory):
	rates = np.zeros(len(timestamps))
	rates = []
	sum = 0
	for i, t in enumerate(timestamps):
		if os.path.isfile(extract_network_mask_path_from_time(t, exp_label)) and os.path.isfile(
				extract_mask_path_from_time(t, 'good_data')):
			tsi_mask = get_simple_mask(t, 'good_data')
			our_mask = get_network_mask_from_time_and_label(t, exp_label)
			rates.append(1 - disagreement_rate(our_mask, tsi_mask))
		# rates[i] = 1 - disagreement_rate(our_mask, tsi_mask)
		else:
			print('tsi:')
			print(extract_mask_path_from_time(t, 'good_data'))
			print('our:')
			print(extract_network_mask_path_from_time(t, exp_label))
			print("not here")
			sum = sum + 1
			pass
	# Save a graph of accuracies
	print("masks are missing:")
	print(sum)
	rates = np.array(rates)
	fig, ax = plt.subplots(nrows=1, ncols=1)
	# ax.plot(np.take(rates * 100, np.flip((rates.argsort()), axis=0)))
	ax.plot(np.take(rates * 100, rates.argsort()))
	ax.set_ylabel('Accuracy (percent of pixels correct)')
	ax.set_xlabel('Decision Images (sorted by accuracy)')
	ax.set_title("Pixel Accuracy for Good Data")
	fig.savefig(directory + '/' + exp_label + '/' + exp_label + 'good1.png', bbox_inches='tight')

if __name__ == '__main__':
	times = sorted(list(extract_data_from_csv('shcu_good_data.csv', 'timestamp_utc')))
	network = 'e70-00'
	show_plot_of_pixel_difference(times, network, 'plots')  # 'results/e70-00'
# timestamps = load_validation_stamps(BATCH_SIZE)
# dir_name = "results/" + sys.argv[1] + "/"
# args = read_parameters(dir_name)
# step_version = read_last_iteration_number(dir_name)
# layer_info = args['Layer info'].split()
# worst_timestamps = find_worst_results(5, timestamps, dir_name, step_version, layer_info)
# print("Worst timestamps:\t" + str(worst_timestamps))
# _, accuracy, saver, _, x, y, y_, _ = build_net(layer_info)
# show_output(accuracy, saver, x, y, y_, dir_name, step_version, True, worst_timestamps, True)
# outputs = run_stamps(saver, x, y, dir_name, step_version, worst_timestamps)
# targets = read_targets(worst_timestamps)
# show_comparison_images(outputs, targets, dir_name)
