from pathlib import Path
import json
import numpy as np
import os
from scipy.signal import butter, lfilter
import time
from subprocess import Popen, PIPE
import shlex
import fire


def read_respiratory_trace(bids_physio_file, column=None):
    # Read in physio file and extract only the physio data
    if column is None:
        if "tsv.gz" in bids_physio_file:
            physio_json = bids_physio_file.replace("tsv.gz", "json")
        elif "tsv" in bids_physio_file:
            physio_json = bids_physio_file.replace("tsv", "json")
        else:
            raise ValueError("the physio file must be a tsv or tsv.gz file")
        # read physio json
        with open(physio_json) as f:
            metadata = json.load(f)
        # get respiratory index
        resp_index = metadata["Columns"].index("respiratory")
    else:
        # just set index as column value
        resp_index = int(column)
    # read physio data
    physio_data = np.genfromtxt(bids_physio_file)
    # return column of respiratory trace
    return physio_data[:, resp_index]


def extract_max_freq(resp_trace, sampling_rate):
    fourier_transform = np.fft.rfft(resp_trace)
    abs_fourier_transform = np.abs(fourier_transform)
    power_spectrum = np.square(abs_fourier_transform)
    frequency = np.linspace(0, sampling_rate / 2, len(power_spectrum))
    assert len(power_spectrum) == len(frequency)
    return frequency[np.argmax(power_spectrum)]


def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def filter_frequency(data, fs):
    return butter_bandpass_filter(data, 0.05, 1, fs)


def write_output(output_folder, physio_path, data):
    out = Path(output_folder)
    if not out.is_dir():
        raise FileNotFoundError("output directory is not found")
    outname = "{}.1D".format(os.path.basename(physio_path).split(".")[0])
    np.savetxt(str(out / outname), data, fmt="%.06f")
    return str(out / outname)


def process_physio(physio_path, output_dir, fs):
    rt = read_respiratory_trace(physio_path, column=2)
    # demean rt
    rt = rt - np.mean(rt)
    max_freq = extract_max_freq(rt, fs)
    if (max_freq > 0.15) and (max_freq < 1):
        filtered = filter_frequency(rt, fs)
        # extract_max_freq(filtered, 62.5)
        return write_output(output_dir, physio_path, filtered)
    else:
        return None
    
def process_physio_no_filter(physio_path, output_dir, fs):
    rt = read_respiratory_trace(physio_path, column=2)
    # demean rt
    rt = rt - np.mean(rt)
    return write_output(output_dir, physio_path, rt)


def make_retroicor_string(nifti_image, physio_path, output_dir):
    new_nifti_name = "{}_retroicor.nii.gz".format(
        os.path.basename(nifti_image).split(".")[0]
    )
    output_dir = Path(output_dir).resolve()
    return "3dretroicor -prefix {} -resp {} {}".format(
        output_dir / new_nifti_name, physio_path, nifti_image
    )


def print_cmd(cmd_str):
    print(cmd_str.replace(" -", "\n -"))


def run_cmd(cmd):
    start_time = time.time()
    print_cmd(cmd)
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    print("Elapsed time: {:.2f}s".format(time.time() - start_time))


def run(nifti_image, physio_path, output_dir, fs):
    processed_physio_path = process_physio_no_filter(physio_path, output_dir, fs)
    if processed_physio_path is None:
        print("{}: bad physio file".format(physio_path))
        return
    # resolve full physio_path
    processed_physio_path = Path(processed_physio_path).resolve()
    retroicor_str = make_retroicor_string(
        nifti_image, processed_physio_path, output_dir
    )
    print(retroicor_str)
    run_cmd(retroicor_str)


if __name__ == "__main__":
    fire.Fire()
