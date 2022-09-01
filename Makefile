default:
	rm -f *.pdf
	./draw-templates.py
	open *.pdf
