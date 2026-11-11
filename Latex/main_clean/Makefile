PROJECT=MACS
VERSION=0_2_5
BUILD=build
PDF=$(PROJECT)-$(VERSION)

.PHONY: all clean

all:
	if exist $(PDF).pdf del $(PDF).pdf
	$(MAKE) $(PDF).pdf

$(PDF).pdf: main.tex
	if not exist $(BUILD) mkdir $(BUILD)
	pdflatex -jobname="$(PDF)" -output-directory=$(BUILD) main.tex
	pdflatex -jobname="$(PDF)" -output-directory=$(BUILD) main.tex
	copy $(BUILD)\$(PDF).pdf $(PDF).pdf
	rmdir /s /q $(BUILD)

clean:
	if exist $(PDF).pdf del $(PDF).pdf
	if exist $(BUILD) rmdir /s /q $(BUILD)
    