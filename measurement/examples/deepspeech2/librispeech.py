import os
import wget
import tarfile
import argparse
import subprocess
import shutil
import json

parser = argparse.ArgumentParser(description='Processes and downloads LibriSpeech dataset.')
parser.add_argument("--target_dir", default='/./data', type=str, help="Directory to store the dataset.")
parser.add_argument('--sample_rate', default=16000, type=int, help='Sample rate')
args = parser.parse_args()
LIBRI_SPEECH_URLS = {
    "train": ["http://www.openslr.org/resources/12/train-other-500.tar.gz",
             "http://www.openslr.org/resources/12/train-clean-100.tar.gz",
             "http://www.openslr.org/resources/12/train-clean-360.tar.gz"
             ],
    "val": ["http://www.openslr.org/resources/12/dev-clean.tar.gz",
           "http://www.openslr.org/resources/12/dev-other.tar.gz"]    ,
    "test": ["http://www.openslr.org/resources/12/test-clean.tar.gz",
            "http://www.openslr.org/resources/12/test-other.tar.gz"]
}


def mkdir_all(dst):
    if not os.path.exists(dst):
      parent_path=os.path.dirname(dst)
      if not os.path.exists(parent_path):
        mkdir_all(parent_path)
      os.mkdir(dst)
def _preprocess_transcript(phrase):
    return phrase.strip().lower()   ##change to lower case
def func(element):
        output = subprocess.check_output(
            ['soxi -D %s' % element.strip()],
            shell=True
        )
	return float(output)
def _process_file(wav_dir,json_path, base_filename, root_dir):#add different json files
    full_recording_path = os.path.join(root_dir, base_filename)
    assert os.path.exists(full_recording_path) and os.path.exists(root_dir)
    wav_recording_path = os.path.join(wav_dir, base_filename.replace(".flac", ".wav"))
    subprocess.call(["sox {}  -r {} -b 16 -c 1 {}".format(full_recording_path, str(args.sample_rate),                                                wav_recording_path)], shell=True)
    # process transcript
    transcript_file = os.path.join(root_dir, "-".join(base_filename.split('-')[:-1]) + ".trans.txt")
    assert os.path.exists(transcript_file), "Transcript file {} does not exist.".format(transcript_file)
    transcriptions = open(transcript_file).read().strip().split("\n")
    transcriptions = {t.split()[0].split("-")[-1]: " ".join(t.split()[1:]) for t in transcriptions}
    key = base_filename.replace(".flac", "").split("-")[-1]
    assert key in transcriptions, "{} is not in the transcriptions".format(key)
    with open(json_path, "a") as f:
        djson={"duration": func(wav_recording_path), "text":_preprocess_transcript(transcriptions[key]), "key": wav_recording_path} 
        jStr=json.dumps(djson,ensure_ascii=False)
        f.write(jStr)    
	f.write('\n')
def main():
    target_dl_dir = args.target_dir
    if not os.path.exists(target_dl_dir):
        os.makedirs(target_dl_dir)
    for split_type, lst_libri_urls in LIBRI_SPEECH_URLS.items():
        split_dir = os.path.join(target_dl_dir, split_type) #/./data/val
        if not os.path.exists(split_dir):
            os.makedirs(split_dir)
        split_wav_dir = os.path.join(split_dir, "wav")
        if not os.path.exists(split_wav_dir):
            os.makedirs(split_wav_dir)        #/./data/val/wav
	json_transcript_path = os.path.join(args.target_dir, "Libri_sample.json".replace("sample", split_type))
        extracted_dir = os.path.join(split_dir, "LibriSpeech")
        for url in lst_libri_urls:
          filename = url.split("/")[-1]############
          single_wav_dir = os.path.join(split_wav_dir, filename.split(".")[-3])
          if not os.path.exists(single_wav_dir):
            os.makedirs(single_wav_dir) 
          target_filename = os.path.join(split_dir, filename)
          unzip_file=os.path.join(extracted_dir, filename.split(".")[-3])
          if not os.path.exists(unzip_file):
            print(unzip_file)
            wget.download(url, split_dir)
            print("Unpacking {}...".format(filename))
	    tar = tarfile.open(target_filename)
	    tar.extractall(split_dir)
            tar.close()
            os.remove(target_filename)
        print("Converting flac files to wav and extracting transcripts...")
        assert os.path.exists(extracted_dir), "Archive {} was not properly uncompressed.".format(filename)
        for root, subdirs, files in os.walk(extracted_dir):
	  for f in files:
	    if f.find(".flac") != -1:##############
              dst= os.path.join(root, f) 
              dst=dst.replace("LibriSpeech", "wav")  
              dst=dst.replace(".flac", ".wav") 
              dst= os.path.split(dst)[0] 
              mkdir_all(dst)      
              _process_file(wav_dir=dst,json_path=json_transcript_path,base_filename=f,root_dir=root)      
if __name__ == "__main__":
	main()
