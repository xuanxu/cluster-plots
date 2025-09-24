DIRS	= LIB C PYTHON

all:	$(DIRS)
	@for D in $(DIRS); do (cd $$D; make all); done

clean:	$(DIRS)
	@for D in $(DIRS); do (cd $$D; make clean); done

raz:	$(DIRS)
	@for D in $(DIRS); do (cd $$D; make raz); done
