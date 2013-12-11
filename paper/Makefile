
MANUSCRIPT_FILES = \
    biblio.bib \
    analysis.tex \     
    cover.tex \        
    formulation.tex \  
    intro.tex \        
    paper.tex \        
    results.tex \
    uqpce.tex \
    coefs.tex \
    figures.tex \
    inference.tex \
    mcmc.tex \
    pcstudy.tex \
    tsunami.tex

OTHER_FILES = 
FIGURES_FILES = 

.PHONY: manuscript figures

all: clean manuscript figures

clean:
    -rm manuscript.tgz figures.tgz

manuscript: manuscript.tgz

figures: figures.tgz

# Note that COPYFILE_DISABLE=1 is included in an alias
manuscript.tgz: $(MANUSCRIPT_FILES) $(OTHER_FILES)
    tar cvzf $@ $(MANUSCRIPT_FILES)

# Note that COPYFILE_DISABLE=1 is included in an alias
figures.tgz: $(FIGURES_FILES)
    tar cvzf $@ $(FIGURES_FILES)

makepdf:
    makepdf
