about:
	@echo "Project tasks and demo launcher"

happy_recon.tar.gz:
	wget http://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz

happy_recon: happy_recon.tar.gz
	tar xzvf $^
	touch $@

demo-buddha-lowres: happy_recon
	python demo.py happy_recon/happy_vrip_res4.ply

demo-buddha-highres: happy_recon
	python demo.py happy_recon/happy_vrip.ply
