import os
import shutil
import subprocess
from glob import glob
from pathlib import Path

from absl import app, flags, logging

DIRNAME = flags.DEFINE_string(
    'dirname',
    'QMDEIMPaper',
    'The directory in which the tex project resides',
)
PLOTDIR = flags.DEFINE_string(
    'plotdir',
    'PlotSources',
    'Where the plots are located',
)
TEXFILE = flags.DEFINE_string(
    'texfile',
    'arxiv_version.tex',
    'Name of the arxiv tex main',
)


def modify_gnuplot_figures(plot_dir):
  files = glob(os.path.join(plot_dir, '*.tex'))
  for f in files:
    with open(f, 'r') as fo:
      lines = fo.readlines()
    modified_lines = []
    fname = Path(f).stem
    for l in lines:
      modified_line = l.replace(fname, fname + '_fig')
      modified_lines.append(modified_line)
    with open(f, 'w') as fo:
      fo.writelines(modified_lines)


# def rename_fig_files(directory="."):
#   for filename in os.listdir(directory):
#     if os.path.isdir(os.path.join(directory, filename)):
#       continue
#
#     file_stem, file_extension = os.path.splitext(filename)
#
#     if file_extension == ".tex":
#       continue
#
#     new_filename = f"{file_stem}_fig{file_extension}"
#     old_path = os.path.join(directory, filename)
#     new_path = os.path.join(directory, new_filename)
#
#     os.rename(old_path, new_path)
#     print(f"Renamed: {filename} -> {new_filename}")


def rename_fig_files(directory="."):
  directory = Path(directory)
  tex_stems = {p.stem for p in directory.glob("*.tex")}

  for file in directory.iterdir():
    if file.is_dir() or file.suffix == ".tex":
      continue
    if file.stem in tex_stems:
      new_name = f"{file.stem}_fig{file.suffix}"
      new_path = file.with_name(new_name)
      file.rename(new_path)
      print(f"Renamed: {file.name} -> {new_name}")


def main(_):
  outfile = DIRNAME.value + '_clean.zip'
  if os.path.isfile(outfile):
    os.remove(outfile)
  subprocess.run('arxiv_latex_cleaner ' + DIRNAME.value, shell=True)
  subprocess.run(
      'cp ' + DIRNAME.value + '/*.bib' + ' ' + DIRNAME.value + '_arXiv/',
      shell=True)
  plt_dir = DIRNAME.value + '_arXiv/' + PLOTDIR.value
  MODIFY_GNUPLOT = True
  if MODIFY_GNUPLOT:
    modify_gnuplot_figures(plt_dir)
    rename_fig_files(plt_dir)
  os.chdir(DIRNAME.value + '_arXiv')
  result = subprocess.run(
      f'latexmk {TEXFILE.value} -outdir=.extraFiles -auxdir=.extraFiles',
      shell=True,
  )
  if result.returncode == 1:
    print(result)
    exit(1)
  else:
    shutil.copy(
        f'.extraFiles/{TEXFILE.value[:-4]}.bbl',
        f'{TEXFILE.value[:-4]}.bbl',
    )
    os.chdir('..')
    shutil.copy(f'{DIRNAME.value}_arXiv/.extraFiles/{TEXFILE.value[:-4]}.log',
                'mytmp.log')
  log_file = Path("mytmp.log")

  # Read the log file into memory for efficient lookups
  if log_file.exists():
    with log_file.open("r") as log:
      log_content = log.read().splitlines()
  else:
    log_content = []

  arx_path = Path(f'{DIRNAME.value}_arXiv/')
  for src_file in arx_path.rglob('*'):
    if src_file.name == f'{TEXFILE.value}':
      # Do nothing
      print('found arxiv_file')
    else:
      if src_file.is_file():
        found = 0
        kk = str(src_file.name[:20])
        print(kk)
        for lc in log_content:
          if kk in lc:
            found = 1
        if found == 1:
          logging.info('File %s is in use', src_file.name)
        else:
          logging.info('File %s is not in use, deleting...', src_file.name)
          src_file.unlink()

  extrafilesdir = Path(f'{DIRNAME.value}_arXiv/.extraFiles')
  if extrafilesdir.exists():
    shutil.rmtree(extrafilesdir)

  if log_file.exists():
    log_file.unlink()

  subprocess.run(
      'zip -r ' + DIRNAME.value + '.zip ' + DIRNAME.value + '_arXiv',
      shell=True)
  shutil.rmtree(Path(f'{DIRNAME.value}_arXiv'))


if __name__ == '__main__':
  app.run(main)
