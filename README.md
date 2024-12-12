# arxiver

Call
```
python arxiver.py --dirname MyLatexProject --plotdir PlotSources --texfile arxiv_version.tex
```

This generates a .zip file `MyLatexProject.zip` where
1. All comments are removed from the text
2. All unused files are removed
3. The .bbl file is in the folder (but the .bib files are removed)
4. Renames some plot source files to circumvent the arxiv-bug that occurs when using gnuplot/cairolatex
