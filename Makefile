style:
	@python -m pip install pre-commit
	@pre-commit run --all-files --show-diff-on-failure

docker-pull:
	@bash .ci/pull_fluent_image.sh

build-doc:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install .[doc]
	@xvfb-run make -C doc html
	@touch doc/_build/html/.nojekyll
	@echo "$(DOCS_CNAME)" >> doc/_build/html/CNAME
